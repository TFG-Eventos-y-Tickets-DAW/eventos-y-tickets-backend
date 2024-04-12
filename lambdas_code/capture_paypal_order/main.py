from common.api_json_schemas import CAPTURE_PAYPAL_ORDER_SCHEMA
from common.constants.order_statuses import ABANDONED_ID, COMPLETED_ID
from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response
from common.paypal.client import PayPalClient
from common.paypal.constants import JOURNAL_RESPONSE
from common.rds_conn import create_rds_connection
from datetime import datetime, timezone
import os
import json
import boto3

from common.schema import is_valid_schema_request

connection = create_rds_connection()
paypal_client = PayPalClient(connection)
dynamodb_resource = boto3.resource("dynamodb")
order_sessions_table = dynamodb_resource.Table(
    os.environ.get("ORDER_SESSIONS_TABLE_NAME", "")
)


@is_valid_schema_request(CAPTURE_PAYPAL_ORDER_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    paypal_order_id = body.get("paypalOrderId")

    if not paypal_order_id:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="Please specify a valid paypal order id.",
        )

    database_order_id, reference_id = retrieve_order_id_by_paypal_id(paypal_order_id)
    if order_is_invalid(reference_id):
        return http_error_response(
            status_code=400,
            error_type="ORDER_EXPIRED",
            error_detail="The order has expired or it has been abandoned.",
        )

    if not database_order_id:
        return http_error_response(
            status_code=404,
            error_type="NOT_FOUND",
            error_detail="The paypal order id doesn't seem to have an order associated.",
        )

    is_valid, status, response, err_msg = paypal_client.capture_order(
        paypal_order_id, database_order_id, reference_id
    )

    if not is_valid:
        return http_error_response(
            status_code=400, error_type=status, error_detail=err_msg
        )

    order_session_id, db_order_id, event_id = response.get("reference_id", "").split(
        "-"
    )

    # Update orders table + delete order session
    update_order_status_in_database(database_order_id, COMPLETED_ID)
    delete_order_session(order_session_id, event_id)
    return {"status": status, "message": "The order has been captured."}


def order_is_invalid(reference_id):
    order_session_id, db_order_id, event_id = reference_id.split("-")

    with connection.cursor() as cur:
        sql = "SELECT `status_id` FROM orders where `id` = %s"
        cur.execute(sql, (int(db_order_id)))
        res = cur.fetchone()
        connection.commit()

        if res is not None and res["status_id"] == ABANDONED_ID:
            return True

    try:
        res = order_sessions_table.get_item(
            Key={
                "orderId": str(order_session_id),
                "eventId": str(event_id),
            }
        )
    except Exception as exc:
        print(f"Error while getting order session {order_session_id} - {exc}")
        return True

    if "Item" not in res:
        return True

    # Scenario where order session record exists but its timestamp ttl has expired
    ttl = int(res.get("Item").get("ttl"))
    ttl_datetime_utc = datetime.fromtimestamp(ttl, timezone.utc)
    now_utc = datetime.now(timezone.utc)
    if now_utc >= ttl_datetime_utc:
        return True

    return False


def retrieve_order_id_by_paypal_id(paypal_order_id):
    with connection.cursor() as cur:
        sql = "SELECT `order_id`, `reference_id` FROM `paypal_journal` WHERE paypal_order_id = %s AND `journal_type` = %s ORDER BY `id` DESC LIMIT 1"
        cur.execute(sql, (paypal_order_id, JOURNAL_RESPONSE))
        res = cur.fetchone()
        connection.commit()

        if res is not None:
            return res["order_id"], res["reference_id"]

    return None


def delete_order_session(order_id, event_id):
    try:
        order_sessions_table.delete_item(
            Key={"orderId": str(order_id), "eventId": str(event_id)}
        )
    except Exception as exc:
        print(
            f"Error while deleting order session {order_id} with event_id {event_id} - {exc}"
        )


def update_order_status_in_database(order_id, status_id):
    with connection.cursor() as cur:
        sql = "UPDATE `orders` SET `status_id` = %s WHERE id = %s"
        cur.execute(
            sql,
            (status_id, order_id),
        )
        connection.commit()
