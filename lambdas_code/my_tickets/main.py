import humps
from common.constants.event_statuses import EVENT_STATUS_NAME_BY_ID
from common.constants.order_statuses import COMPLETED_ID
from common.constants.ticket_types import FREE, PAID
from common.event_utils import (
    convert_datetime_to_strings,
    get_user_id_from_jwt,
)
from common.http_utils import generic_server_error
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection


connection = create_rds_connection()
connection.autocommit(True)
jwt_secret = get_jwt_secret()


def lambda_handler(event, _):
    headers = event.get("headers", {})
    current_user_id = get_user_id_from_jwt(headers, jwt_secret)

    try:
        my_tickets = retrieve_my_orders_details_by_user_id(current_user_id)
        my_tickets_formatted = list(map(format_my_tickets, my_tickets))
    except Exception as exc:
        print(
            f"An error ocurred while retrieving tickets for user {current_user_id} - {exc}"
        )
        return generic_server_error()

    return {"tickets": my_tickets_formatted}


def retrieve_my_orders_details_by_user_id(user_id):
    with connection.cursor() as cur:
        sql = "SELECT o.id as order_id, o.event_id, o.total as price, o.quantity, e.title, e.description, e.status_id as event_status_id, e.img_src, e.starts_at, e.ends_at FROM orders o "
        sql += "JOIN events e ON o.event_id = e.id "
        sql += "WHERE o.payer_id = %s AND o.status_id = %s"

        cur.execute(sql, (user_id, COMPLETED_ID))
        result = cur.fetchall()

    return result


def format_my_tickets(event_details: dict):
    new_event_details = event_details.copy()

    if "event_status_id" in new_event_details:
        new_event_details["status"] = EVENT_STATUS_NAME_BY_ID[
            new_event_details["event_status_id"]
        ]
        del new_event_details["event_status_id"]

    convert_datetime_to_strings(new_event_details)

    if (event_details.get("price") or 0) <= 0:
        new_event_details["type"] = FREE
    else:
        new_event_details["type"] = PAID

    return humps.camelize(new_event_details)
