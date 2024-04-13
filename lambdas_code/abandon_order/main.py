from common.api_json_schemas import ABANDON_ORDER_SCHEMA
from common.constants.order_statuses import ABANDONED, ABANDONED_ID
from common.http_utils import generic_server_error, http_error_response
from common.rds_conn import create_rds_connection
import os
import json
import boto3

from common.schema import is_valid_schema_request

connection = create_rds_connection()
dynamodb_resource = boto3.resource("dynamodb")
order_sessions_table = dynamodb_resource.Table(
    os.environ.get("ORDER_SESSIONS_TABLE_NAME", "")
)


@is_valid_schema_request(ABANDON_ORDER_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    order_session_id = body.get("orderSessionId")
    order_id = body.get("orderId")
    event_id = body.get("eventId")

    order_session, error = get_order_session(order_session_id, event_id)

    if error:
        return error

    delete_order_session(order_session_id, event_id)
    # Update orders table if order id provided
    # TODO: enforce check for paypal orders
    if order_id:
        update_order_status_in_database(order_id, ABANDONED_ID)

    return {"status": ABANDONED}


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
