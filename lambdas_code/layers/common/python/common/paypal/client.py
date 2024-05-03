import requests
import boto3
import json

from common.constants.order_statuses import FAILED
from common.constants.payment_methods import CREDIT, PAYMENT_METHOD_ID_BY_NAME, PAYPAL
from common.paypal.constants import (
    APPROVED,
    INTERNAL_ERROR,
    JOURNAL_CAPTURE_FAILURE,
    JOURNAL_CAPTURE_REQUEST,
    JOURNAL_CAPTURE_RESPONSE,
    JOURNAL_FAILURE,
    JOURNAL_REQUEST,
    JOURNAL_RESPONSE,
    ORDER_STATUS_BY_PAYPAL_ERROR,
    PAYER_ACTION_REQUIRED,
    PAYPAL_COMPLETED,
    RESOURCE_NOT_FOUND,
    UNKNOWN,
    UNPROCESSABLE_ENTITY,
)


class PayPalClient:
    access_token: str = ""

    def __init__(self, db_connection) -> None:
        self.ssm_parameter_store = boto3.client("ssm")
        self.user = self._get_paypal_cred("/paypal/api/username")
        self.password = self._get_paypal_cred("/paypal/api/password")

        self.db_connection = db_connection
        self.access_token = self._generate_access_token()

    def _generate_access_token(self):
        try:
            auth_response = requests.post(
                "https://api-m.sandbox.paypal.com/v1/oauth2/token",
                auth=(self.user, self.password),
                data="grant_type=client_credentials",
            )
            auth_json_response = auth_response.json()
            return auth_json_response.get("access_token", "")
        except Exception as exc:
            print("Error generating PayPal access token, can't proceed.")
            raise exc

    def _create_request_header(self, order_id, event_id):
        return {
            "Content-Type": "application/json",
            "PayPal-Request-Id": f"{order_id}-{event_id}",
            "Authorization": f"Bearer {self.access_token}",
        }

    def _get_paypal_cred(self, cred_path):
        parameter = self.ssm_parameter_store.get_parameter(
            Name=cred_path, WithDecryption=True
        )
        return parameter.get("Parameter", {}).get("Value", "")

    def process_order(
        self,
        payment_method,
        payment_method_details,
        order_metadata,
        order_id,
        event_id,
        order_session_id,
        origin,
    ):
        # reference id to be used on paypal + our side:
        reference_id = f"{order_session_id}-{order_id}-{event_id}"

        # We create a journal record, evidence of the first request sent to PayPal
        self._create_journal_record(
            order_id=order_id,
            payment_method=payment_method,
            journal_type=JOURNAL_REQUEST,
            reference_id=reference_id,
        )
        self.db_connection.commit()

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "amount": {
                        "currency_code": order_metadata.get("currency", "USD"),
                        "value": order_metadata.get("totalAmount"),
                    },
                }
            ],
            "payment_source": self._build_payment_source_by_payment_method(
                payment_method, payment_method_details, origin
            ),
        }

        try:
            response = requests.post(
                "https://api-m.sandbox.paypal.com/v2/checkout/orders",
                headers=self._create_request_header(order_id, event_id),
                data=json.dumps(payload),
            )
            response_json = response.json()
            print(f"Response received from PayPal: {response_json}")

            # Refresh token in case it has expired
            # may happen if lambda was warm too much time
            if response_json.get("error", "") == "invalid_token":
                print("Access token expired, regenerating new one...")
                self.access_token = self._generate_access_token()
                response = requests.post(
                    "https://api-m.sandbox.paypal.com/v2/checkout/orders",
                    headers=self._create_request_header(order_id, event_id),
                    data=json.dumps(payload),
                )
                response_json = response.json()

            if response_json.get("status") == PAYPAL_COMPLETED:
                payment_card_source = response_json.get("payment_source", {}).get(
                    "card", {}
                )
                purchase_unit = response_json.get("purchase_units", [{}])[0].get(
                    "payments"
                )
                capture = purchase_unit.get("captures", [{}])[0]

                response_data = {
                    "card_last_digits": payment_card_source.get("last_digits"),
                    "card_brand": payment_card_source.get("brand"),
                    "paypal_order_id": capture.get("id"),
                    "paypal_fee": capture.get("seller_receivable_breakdown", {})
                    .get("paypal_fee")
                    .get("value"),
                }

                # We create a journal record, evidence of the response received by PayPal
                self._create_journal_record(
                    order_id=order_id,
                    payment_method=payment_method,
                    journal_type=JOURNAL_RESPONSE,
                    status=PAYPAL_COMPLETED,
                    paypal_order_id=response_data.get("paypal_order_id"),
                    paypal_fee=response_data.get("paypal_fee"),
                    card_last_digits=response_data.get("card_last_digits"),
                    card_brand=response_data.get("card_brand"),
                    reference_id=reference_id,
                )
                self.db_connection.commit()

                return PAYPAL_COMPLETED, response_data

            if response_json.get("status") == PAYER_ACTION_REQUIRED:
                paypal_url_to_redirect = response_json.get("links")[1].get("href")
                paypal_order_id = response_json.get("id")
                response_data = {
                    "paypal_order_id": paypal_order_id,
                    "paypal_url_to_redirect": paypal_url_to_redirect,
                }

                # We create a journal record, evidence of the response received by PayPal
                self._create_journal_record(
                    order_id=order_id,
                    payment_method=payment_method,
                    journal_type=JOURNAL_RESPONSE,
                    status=PAYER_ACTION_REQUIRED,
                    paypal_order_id=response_data.get("paypal_order_id"),
                    reference_id=reference_id,
                )
                self.db_connection.commit()

                return PAYER_ACTION_REQUIRED, response_data

            # Identify why the transaction failed
            error_type = response_json.get("name") or UNKNOWN
            error_desc = UNKNOWN
            if error_type == UNPROCESSABLE_ENTITY:
                details = response_json.get("details", [{}])[0]
                issue = details.get("issue", UNKNOWN)
                error_desc = details.get("description", "")
                self._create_journal_record(
                    order_id=order_id,
                    payment_method=payment_method,
                    journal_type=JOURNAL_FAILURE,
                    status=ORDER_STATUS_BY_PAYPAL_ERROR.get(issue),
                    error_type=error_type,
                    error_details=error_desc,
                    reference_id=reference_id,
                )
                return ORDER_STATUS_BY_PAYPAL_ERROR.get(issue), {
                    "error_type": error_type,
                    "error_details": error_desc,
                }

            # Create journal record for failed transaction along with error details
            self._create_journal_record(
                order_id=order_id,
                payment_method=payment_method,
                journal_type=JOURNAL_FAILURE,
                status=ORDER_STATUS_BY_PAYPAL_ERROR.get(issue),
                error_type=error_type,
                error_details=error_desc,
                reference_id=reference_id,
            )
            self.db_connection.commit()

            return FAILED, {"error_type": error_type, "error_details": error_desc}
        except Exception as exc:
            print(f"Error paying order: {exc}")
            # Create journal record for failed transaction along with error details
            self._create_journal_record(
                order_id=order_id,
                payment_method=payment_method,
                journal_type=JOURNAL_FAILURE,
                status=FAILED,
                error_type=INTERNAL_ERROR,
                error_details=INTERNAL_ERROR,
                reference_id=reference_id,
            )
            self.db_connection.commit()
            return FAILED, {
                "error_type": INTERNAL_ERROR,
                "error_details": INTERNAL_ERROR,
            }

    def get_order_status(self, paypal_order_id):
        try:
            response = requests.get(
                f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}",
                headers=self._create_request_header(paypal_order_id, 0),
            )
            res_json = response.json()

            # Refresh token in case it has expired
            # may happen if lambda was warm too much time
            if res_json.get("error", "") == "invalid_token":
                print("Access token expired, regenerating new one...")
                self.access_token = self._generate_access_token()
                response = requests.get(
                    f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}",
                    headers=self._create_request_header(paypal_order_id, 0),
                )
                res_json = response.json()

            if res_json.get("name", "") == RESOURCE_NOT_FOUND:
                return (
                    RESOURCE_NOT_FOUND,
                    404,
                    "The paypal order id provided doesn't exists.",
                )

            return res_json.get("status", UNKNOWN), 200, None

        except Exception as exc:
            print(
                f"An error ocurred while getting paypal order status for {paypal_order_id} - {exc}"
            )
            return INTERNAL_ERROR, 500, "Something went wrong, please try again later."

    def capture_order(self, paypal_order_id, database_order_id, reference_id):
        """
        Captures a paypal order to finally collect the money
        """
        status, _, _ = self.get_order_status(paypal_order_id)

        if status in [RESOURCE_NOT_FOUND, PAYER_ACTION_REQUIRED, UNKNOWN]:
            return (
                False,
                status,
                None,
                "The order can't be captured since it is in an invalid state.",
            )

        if status == PAYPAL_COMPLETED:
            return (
                False,
                f"ALREADY_{status}",
                None,
                "The order was previously captured.",
            )

        try:
            if status == APPROVED:
                # We create a journal record, evidence of the first capture request sent to PayPal
                self._create_journal_record(
                    order_id=database_order_id,
                    paypal_order_id=paypal_order_id,
                    payment_method=PAYPAL,
                    status=APPROVED,
                    journal_type=JOURNAL_CAPTURE_REQUEST,
                    reference_id=reference_id,
                )
                self.db_connection.commit()

                response = requests.post(
                    f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}/capture",
                    headers=self._create_request_header(
                        paypal_order_id, database_order_id
                    ),
                )
                res_json = response.json()

                # Refresh token in case it has expired
                # may happen if lambda was warm too much time
                if res_json.get("error", "") == "invalid_token":
                    print("Access token expired, regenerating new one...")
                    self.access_token = self._generate_access_token()
                    response = requests.get(
                        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}/capture",
                        headers=self._create_request_header(
                            paypal_order_id, database_order_id
                        ),
                    )
                    res_json = response.json()

                if res_json.get("status", "") == PAYPAL_COMPLETED:
                    paypal_payer_email = res_json.get("payer", {}).get("email_address")
                    purchase_units = res_json.get("purchase_units")[0]
                    capture = purchase_units.get("payments").get("captures")[0]
                    paypal_fee = (
                        capture.get("seller_receivable_breakdown")
                        .get("paypal_fee")
                        .get("value")
                    )
                    response_data = {"reference_id": purchase_units.get("reference_id")}
                    self._create_journal_record(
                        order_id=database_order_id,
                        paypal_order_id=paypal_order_id,
                        payment_method=PAYPAL,
                        journal_type=JOURNAL_CAPTURE_RESPONSE,
                        status=PAYPAL_COMPLETED,
                        paypal_payer_email=paypal_payer_email,
                        paypal_fee=float(paypal_fee),
                        reference_id=reference_id,
                    )
                    self.db_connection.commit()
                    return True, res_json.get("status", ""), response_data, None

                # Identify why the transaction failed
                error_type = res_json.get("name") or UNKNOWN
                error_desc = UNKNOWN
                if error_type == UNPROCESSABLE_ENTITY:
                    details = res_json.get("details", [{}])[0]
                    error_desc = details.get("description", "")

                # Create journal record for failed transaction along with error details
                self._create_journal_record(
                    order_id=database_order_id,
                    payment_method=PAYPAL,
                    paypal_order_id=paypal_order_id,
                    journal_type=JOURNAL_CAPTURE_FAILURE,
                    status=FAILED,
                    error_type=error_type,
                    error_details=error_desc,
                    reference_id=reference_id,
                )
                self.db_connection.commit()

                return False, status, None, error_desc
        except Exception as exc:
            print(
                f"An error ocurred while capturing PayPal Order {paypal_order_id} - {exc}"
            )
            # Create journal record for failed transaction along with error details
            self._create_journal_record(
                order_id=database_order_id,
                payment_method=PAYPAL,
                journal_type=JOURNAL_CAPTURE_FAILURE,
                status=FAILED,
                error_type=error_type,
                error_details=error_desc,
                reference_id=reference_id,
            )
            self.db_connection.commit()

        return False, status, None, "Unknown status from PayPal."

    def _create_journal_record(
        self,
        order_id,
        payment_method,
        journal_type,
        paypal_order_id=None,
        paypal_fee=None,
        status=None,
        card_brand=None,
        card_last_digits=None,
        paypal_payer_email=None,
        error_type=None,
        error_details=None,
        reference_id=None,
    ):
        with self.db_connection.cursor() as cur:
            sql = "INSERT INTO `paypal_journal` (`order_id`, `payment_method_id`, `journal_type`, `paypal_order_id`, `paypal_fee`, `status`, `card_brand`, `card_last_digits`, `paypal_payer_email`, `error_type`, `error_details`, `reference_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(
                sql,
                (
                    order_id,
                    PAYMENT_METHOD_ID_BY_NAME.get(payment_method),
                    journal_type,
                    paypal_order_id,
                    paypal_fee,
                    status,
                    card_brand,
                    card_last_digits,
                    paypal_payer_email,
                    error_type,
                    error_details,
                    reference_id,
                ),
            )

    def _build_payment_source_by_payment_method(
        self, payment_method, payment_method_details, origin
    ):
        if payment_method == CREDIT:
            return {
                "card": {
                    "name": payment_method_details.get("cardholderName"),
                    "number": payment_method_details.get("cardNumber"),
                    "security_code": payment_method_details.get("cvv"),
                    "expiry": payment_method_details.get("expiry"),
                    "experience_context": {
                        "return_url": f"{origin}/paypal/capture",
                        "cancel_url": f"{origin}/paypal/capture/cancel",
                    },
                }
            }
        # PayPal
        return {
            "paypal": {
                "experience_context": {
                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                    "brand_name": "Event & Greet",
                    "locale": "en-US",
                    "landing_page": "LOGIN",
                    "shipping_preference": "GET_FROM_FILE",
                    "user_action": "PAY_NOW",
                    "return_url": f"{origin}/paypal/capture",
                    "cancel_url": f"{origin}/paypal/capture/cancel",
                }
            }
        }
