from common.api_json_schemas import LIST_ORDERS_SCHEMA
from common.constants.order_statuses import (
    ORDER_STATUS_ID_BY_NAME,
)
from common.constants.payment_methods import FREE, PAYMENT_METHOD_NAME_BY_ID
from common.error_types import INVALID_REQUEST
from common.event_utils import get_user_id_from_jwt
from common.event_validation import is_valid_event_from_path
from common.http_utils import http_error_response
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection
import json
import humps
import boto3
import os

from common.schema import is_valid_schema_request

connection = create_rds_connection()
connection.autocommit(True)
jwt_secret = get_jwt_secret()
dynamodb_resource = boto3.resource("dynamodb")
event_views_table = dynamodb_resource.Table(
    os.environ.get("EVENT_VIEWS_TABLE_NAME", "")
)


@is_valid_schema_request(LIST_ORDERS_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    event_id = event.get("pathParameters", {}).get("eventId")

    if not event_id:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="Please specify a valid event id.",
        )

    is_valid, event_details = is_valid_event_from_path(event_id, connection)

    if not is_valid:
        return http_error_response(
            status_code=404,
            error_type="NOT_FOUND",
            error_detail="The event id provided doesn't exist.",
        )

    headers = event.get("headers", {})
    current_user_id = get_user_id_from_jwt(headers, jwt_secret)
    if current_user_id != event_details["owner_id"]:
        return http_error_response(
            status_code=401,
            error_type="UNAUTHORIZED",
            error_detail="You are not allowed to view orders for this event.",
        )

    filters = body.get("filters")
    orders_list = list(
        map(
            format_orders,
            retrieve_orders_by_event_and_status(event_id, filters.get("status")),
        )
    )

    return {
        "orders": orders_list,
        "eventViewsCount": retrieve_event_views(str(event_details["id"])),
    }


def retrieve_orders_by_event_and_status(event_id, status):
    status_id = ORDER_STATUS_ID_BY_NAME.get(status)

    with connection.cursor() as cur:
        sql = "SELECT o.id, o.quantity, o.total, u.first_name, u.email, pj.payment_method_id, pj.card_brand, pj.card_last_digits, pj.paypal_payer_email, o.created_at FROM orders o"
        sql += " JOIN users u ON o.payer_id = u.id"
        sql += " LEFT JOIN paypal_journal pj ON pj.order_id = o.id"
        sql += " WHERE o.event_id = %s AND o.status_id = %s"
        sql += " AND (pj.journal_type IN ('RESPONSE', 'CAPTURE_RESPONSE')"
        sql += " AND (pj.card_brand IS NOT NULL OR pj.card_last_digits IS NOT NULL OR pj.paypal_payer_email IS NOT NULL))"
        sql += " OR (o.total = 0 AND o.event_id = %s AND o.status_id = %s)"  # Free orders constraint

        cur.execute(sql, (event_id, status_id, event_id, status_id))
        result = cur.fetchall()

    return result


def format_orders(order: dict):
    new_order = order.copy()
    convert_datetime_to_string(new_order)
    replace_payment_method_id(new_order)

    return humps.camelize(new_order)


def convert_datetime_to_string(order: dict):
    if "created_at" in order:
        order["created_at"] = (
            order["created_at"].strftime("%d-%m-%Y %H:%M:%S")
            if order["created_at"] is not None
            else None
        )


def replace_payment_method_id(order: dict):
    if "payment_method_id" in order:
        order["payment_method"] = (
            PAYMENT_METHOD_NAME_BY_ID.get(order["payment_method_id"]) or FREE
        )
        del order["payment_method_id"]


def retrieve_event_views(event_id):
    event_views_metadata = event_views_table.get_item(Key={"eventId": event_id})
    if "Item" not in event_views_metadata:
        return 0

    return event_views_metadata.get("Item", {}).get("viewCount", 0) or 0
