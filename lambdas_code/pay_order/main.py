from common.api_json_schemas import PAY_ORDER_SCHEMA
from common.constants.order_statuses import (
    COMPLETED_ID,
    FAILED_ID,
    ORDER_STATUS_ID_BY_NAME,
    PENDING_ID,
)
from common.constants.payment_methods import CREDIT, FREE, PAYPAL
from common.error_types import INVALID_REQUEST, PAYMENT_FAILED
from common.http_utils import http_error_response, generic_server_error
from common.payment_method_validation import validate_payment_method
from common.paypal.client import PayPalClient
from common.paypal.constants import (
    PAYER_ACTION_REQUIRED,
    PAYPAL_COMPLETED,
)
from common.rds_conn import create_rds_connection
from common.schema import is_valid_schema_request

import json
import boto3
import os

connection = create_rds_connection()

dynamodb_resource = boto3.resource("dynamodb")
order_sessions_table = dynamodb_resource.Table(
    os.environ.get("ORDER_SESSIONS_TABLE_NAME", "")
)

# PayPal Processor
paypal_client = PayPalClient(connection)


@is_valid_schema_request(PAY_ORDER_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    order_id = event.get("pathParameters", {}).get("id")
    event_id = body.get("eventId")
    order_session, error = get_order_session(order_id, event_id)
    hostOrigin = event.get("headers", {}).get("origin", "")

    if error:
        return error

    payment_method = body.get("paymentMethod")
    payment_method_details = body.get("paymentMethodDetails", {})
    is_valid, err_msg = validate_payment_method(payment_method, payment_method_details)

    if not is_valid:
        return http_error_response(
            status_code=400, error_type=INVALID_REQUEST, error_detail=err_msg
        )

    if payment_method == FREE and float(order_session.get("totalAmount")) > 0:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="You can't pay this order as a FREE order since its amount is greater than 0."
        )

    if float(order_session.get("totalAmount")) <= 0 and payment_method != FREE:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="You can't pay this order using PayPal or Credit cards since it is a FREE order."
        )

    if payment_method == FREE:
        database_order_id = create_order_in_database(order_session, COMPLETED_ID)
        connection.commit()
        delete_order_session(order_id, event_id)
        return {
            "status": PAYPAL_COMPLETED,
            "orderId": database_order_id,
            "quantity": int(order_session.get("quantity")),
            "ticketId": int(order_session.get("ticketId")),
            "total": float(order_session.get("totalAmount")),
        }

    try:
        database_order_id = create_order_in_database(order_session)
    except Exception as exc:
        print(f"An error ocurred while creating order {order_id}: {exc}")
        return generic_server_error()

    # We are now attempting to start a credit transaction with paypal
    try:
        paypal_status, response_data = paypal_client.process_order(
            payment_method=payment_method,
            payment_method_details=payment_method_details,
            order_metadata=order_session,
            order_id=database_order_id,
            event_id=event_id,
            order_session_id=order_id,
            origin=hostOrigin
        )

        if paypal_status != PAYPAL_COMPLETED and paypal_status != PAYER_ACTION_REQUIRED:
            update_order_status_in_database(
                database_order_id, ORDER_STATUS_ID_BY_NAME.get(paypal_status, FAILED_ID)
            )
            return http_error_response(
                status_code=500,
                error_type=PAYMENT_FAILED,
                error_detail=f"The payment failed with status: {paypal_status} - {response_data.get("error_details")}",
            )
    except Exception as exc:
        print(f"An error ocurred while attempting to process a payment. - {exc}")
        return generic_server_error()

    try:
        if payment_method == CREDIT:
            update_order_status_in_database(database_order_id, COMPLETED_ID)
            connection.commit()
    except Exception as exc:
        print(f"Error while updating order status - {exc}")
        return generic_server_error()

    # Clean up order session for CREDIT - we want to keep order sessions for redirected payments (paypal)
    if payment_method == CREDIT:
        delete_order_session(order_id, event_id)

    return build_result_by_payment_method(payment_method, paypal_status, database_order_id, order_session, response_data)


def build_result_by_payment_method(payment_method, paypal_status, database_order_id, order_session, response_data):
    result = {
        "status": paypal_status,
        "orderId": database_order_id,
        "quantity": int(order_session.get("quantity")),
        "ticketId": int(order_session.get("ticketId")),
        "total": float(order_session.get("totalAmount")),
    }
    if payment_method == PAYPAL:
        result["redirectUrl"] = response_data.get("paypal_url_to_redirect", "")
        result["paypalOrderId"] = response_data.get("paypal_order_id", "")

    return result


def create_order_in_database(order_session, status=PENDING_ID):
    order_id = 0

    with connection.cursor() as cur:
        sql = "INSERT INTO `orders` (`event_id`, `ticket_id`, `payer_id`, `payee_id`, `status_id`, `total`, `quantity`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                int(order_session.get("eventId")),
                int(order_session.get("ticketId")),
                int(order_session.get("payerId")),
                int(order_session.get("payeeId")),
                status,
                float(order_session.get("totalAmount")),
                int(order_session.get("quantity")),
            ),
        )

        order_id = cur.lastrowid

    return order_id


def update_order_status_in_database(order_id, status_id):
    with connection.cursor() as cur:
        sql = "UPDATE `orders` SET `status_id` = %s WHERE id = %s"
        cur.execute(
            sql,
            (status_id, order_id),
        )


def get_order_session(order_id, event_id):
    try:
        res = order_sessions_table.get_item(
            Key={
                "orderId": str(order_id),
                "eventId": str(event_id),
            }
        )
    except Exception as exc:
        print(f"Error while getting order session {order_id} - {exc}")
        return None, generic_server_error()

    if "Item" not in res:
        return None, http_error_response(
            status_code=404,
            error_type="NOT_FOUND",
            error_detail="The order provided doesn't exist or has expired.",
        )

    order_metadata = json.loads(res.get("Item").get("metadata"))
    event_id = res.get("Item").get("eventId")
    order_metadata["eventId"] = event_id

    return order_metadata, None


def delete_order_session(order_id, event_id):
    try:
        order_sessions_table.delete_item(
            Key={"orderId": str(order_id), "eventId": str(event_id)}
        )
    except Exception as exc:
        print(
            f"Error while deleting order session {order_id} with event_id {event_id} - {exc}"
        )
