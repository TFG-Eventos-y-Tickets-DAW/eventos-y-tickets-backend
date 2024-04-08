from common.api_json_schemas import PAY_ORDER_SCHEMA
from common.constants.order_statuses import (
    COMPLETED_ID,
    FAILED_ID,
    ORDER_STATUS_ID_BY_NAME,
    PENDING_ID,
)
from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response, generic_server_error
from common.payment_method_validation import validate_payment_method
from common.paypal.client import PayPalClient
from common.paypal.constants import (
    JOURNAL_FAILURE,
    JOURNAL_REQUEST,
    JOURNAL_RESPONSE,
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
paypal_client = PayPalClient()


@is_valid_schema_request(PAY_ORDER_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    order_id = event.get("pathParameters", {}).get("id")
    event_id = body.get("eventId")
    order_session, error = get_order_session(order_id, event_id)

    if error:
        return error

    payment_method = body.get("paymentMethod")
    payment_method_details = body.get("paymentMethodDetails", {})
    is_valid, err_msg = validate_payment_method(payment_method, payment_method_details)

    if not is_valid:
        return http_error_response(
            status_code=400, error_type=INVALID_REQUEST, error_detail=err_msg
        )

    try:
        database_order_id = create_order_in_database(order_session)
    except Exception as exc:
        print(f"An error ocurred while creating order {order_id}: {exc}")
        return generic_server_error()

    # We create a journal record, evidence of the first request sent to PayPal
    try:
        paypal_client.create_journal_record(
            connection=connection,
            order_id=database_order_id,
            payment_method=payment_method,
            journal_type=JOURNAL_REQUEST,
        )
        connection.commit()
    except Exception as exc:
        print(f"An error ocurred while creating PayPal Request Journal record. - {exc}")
        return generic_server_error()

    # We are now attempting to start a transaction with paypal
    try:
        paypal_status, response_data = paypal_client.process_credit_order(
            payment_method_details=payment_method_details,
            order_metadata=order_session,
            order_id=database_order_id,
            event_id=event_id,
        )

        # TODO: support for PayPal Redirected payment status (pending external action) `PAYER_ACTION_REQUIRED`
        if paypal_status != PAYPAL_COMPLETED:
            update_order_status_in_database(
                database_order_id, ORDER_STATUS_ID_BY_NAME.get(paypal_status, FAILED_ID)
            )
            # Create journal record for failed transaction along with error details
            paypal_client.create_journal_record(
                connection=connection,
                order_id=database_order_id,
                payment_method=payment_method,
                journal_type=JOURNAL_FAILURE,
                status=paypal_status,
                error_type=response_data.get("error_type"),
                error_details=response_data.get("error_details")
            )
            connection.commit()

            return http_error_response(
                status_code=500,
                error_type="PAYMENT_FAILED",
                error_detail=f"The payment failed with status: {paypal_status} - {response_data.get("error_details")}",
            )
    except Exception as exc:
        print(f"An error ocurred while attempting to process a payment. - {exc}")
        return generic_server_error()

    # We create a journal record, evidence of the response received by PayPal
    try:
        paypal_client.create_journal_record(
            connection=connection,
            order_id=database_order_id,
            payment_method=payment_method,
            journal_type=JOURNAL_RESPONSE,
            status=paypal_status,
            paypal_order_id=response_data.get("paypal_order_id"),
            paypal_fee=response_data.get("paypal_fee"),
            card_last_digits=response_data.get("card_last_digits"),
            card_brand=response_data.get("card_brand"),
        )
        connection.commit()
    except Exception as exc:
        print(
            f"An error ocurred while creating PayPal Response Journal record. - {exc}"
        )
        return generic_server_error()

    try:
        update_order_status_in_database(database_order_id, COMPLETED_ID)
        connection.commit()
    except Exception as exc:
        print(f"Error while updating order status - {exc}")
        return generic_server_error()

    # Finally, Clean up order session
    delete_order_session(order_id, event_id)

    # Everything went ok at this point!
    return {
        "status": paypal_status,
        "orderId": database_order_id,
        "quantity": int(order_session.get("quantity")),
        "ticketId": int(order_session.get("ticketId")),
        "total": float(order_session.get("totalAmount")),
    }


def create_order_in_database(order_session):
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
                PENDING_ID,
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
