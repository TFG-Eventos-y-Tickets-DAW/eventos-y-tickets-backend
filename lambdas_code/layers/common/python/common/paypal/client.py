import requests
import boto3
import json

from common.constants.order_statuses import FAILED
from common.constants.payment_methods import PAYMENT_METHOD_ID_BY_NAME
from common.paypal.constants import (
    ORDER_STATUS_BY_PAYPAL_ERROR,
    PAYPAL_COMPLETED,
    TRANSACTION_REFUSED,
    UNPROCESSABLE_ENTITY,
)


class PayPalClient:
    access_token: str = ""

    def __init__(self) -> None:
        self.ssm_parameter_store = boto3.client("ssm")
        self.user = self._get_paypal_cred("/paypal/api/username")
        self.password = self._get_paypal_cred("/paypal/api/password")

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

    def process_credit_order(
        self, payment_method_details, order_metadata, order_id, event_id
    ):
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(order_id),
                    "amount": {
                        "currency_code": order_metadata.get("currency", "USD"),
                        "value": order_metadata.get("totalAmount"),
                    },
                }
            ],
            "payment_source": {
                "card": {
                    "name": payment_method_details.get("cardholderName"),
                    "number": payment_method_details.get("cardNumber"),
                    "security_code": payment_method_details.get("cvv"),
                    "expiry": payment_method_details.get("expiry"),
                    "experience_context": {
                        "return_url": "https://example.com/returnUrl",
                        "cancel_url": "https://example.com/cancelUrl",
                    },
                }
            },
        }

        try:
            response = requests.post(
                "https://api-m.sandbox.paypal.com/v2/checkout/orders",
                headers=self._create_request_header(order_id, event_id),
                data=json.dumps(payload),
            )
            response_json = response.json()
            print(f"Response received from PayPal: {response_json}")

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

                response = {
                    "card_last_digits": payment_card_source.get("last_digits"),
                    "card_brand": payment_card_source.get("brand"),
                    "paypal_order_id": capture.get("id"),
                    "paypal_fee": capture.get("seller_receivable_breakdown", {})
                    .get("paypal_fee")
                    .get("value"),
                }
                return PAYPAL_COMPLETED, response

            # Identify why the transaction failed
            error_type = response_json.get("name")
            if error_type == UNPROCESSABLE_ENTITY:
                details = response_json.get("details", [{}])[0]
                issue = details.get("issue", "UNKNOWN")
                desc = details.get("description", "")
                return ORDER_STATUS_BY_PAYPAL_ERROR.get(issue), {
                    "error_type": error_type,
                    "error_details": desc,
                }

            return FAILED, {"error_type": "UNKNOWN", "error_details": "UNKNOWN"}
        except Exception as exc:
            print(f"Error paying order: {exc}")
            return FAILED, {"error_type": "UNKNOWN", "error_details": "UNKNOWN"}

    def create_journal_record(
        self,
        connection,
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
    ):
        with connection.cursor() as cur:
            sql = "INSERT INTO `paypal_journal` (`order_id`, `payment_method_id`, `journal_type`, `paypal_order_id`, `paypal_fee`, `status`, `card_brand`, `card_last_digits`, `paypal_payer_email`, `error_type`, `error_details`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
                ),
            )
