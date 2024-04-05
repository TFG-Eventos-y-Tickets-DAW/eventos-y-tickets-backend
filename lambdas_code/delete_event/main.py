from common.error_types import INVALID_REQUEST
from common.event_utils import get_user_id_from_jwt
from common.event_validation import (
    is_valid_event_from_path,
)
from common.http_utils import generic_server_error, http_error_response
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection

connection = create_rds_connection()
jwt_secret = get_jwt_secret()


def lambda_handler(event, _):
    is_valid_event_id, event_details = is_valid_event_from_path(
        event.get("pathParameters", {}).get("id"), connection
    )

    if not is_valid_event_id:
        return http_error_response(
            status_code=400,
            error_type="NOT_FOUND",
            error_detail="The event id passed was not found or it was malformed.",
        )

    headers = event.get("headers", {})
    current_user_id = get_user_id_from_jwt(headers, jwt_secret)

    if current_user_id != event_details["owner_id"]:
        return http_error_response(
            status_code=401,
            error_type="UNAUTHORIZED",
            error_detail="You are not allowed to delete this event.",
        )

    event_id = event_details["id"]

    # Check if event has sold tickets and no refunds (equal to the sold amount)
    if has_sold_tickets_and_no_refunds(event_id):
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="The event has sold at least 1 ticket and performed no refunds on it.",
        )

    try:
        delete_event(event_id)
    except Exception as exc:
        print(f"Error while deleting event {event_id}: {exc}")
        return generic_server_error()

    connection.commit()

    return {"eventId": event_id, "message": "Event deleted successfully!"}


def delete_event(event_id):
    with connection.cursor() as cur:
        sql_delete_tickets = "DELETE FROM `tickets` WHERE event_id = %s"
        sql_delete_payout_instrument = (
            "DELETE FROM `payout_instruments` WHERE event_id = %s"
        )
        sql_delete_event = "DELETE FROM `events` WHERE id = %s"

        cur.execute(sql_delete_payout_instrument, (event_id,))
        cur.execute(sql_delete_tickets, (event_id,))
        cur.execute(sql_delete_event, (event_id,))


def has_sold_tickets_and_no_refunds(event_id):
    with connection.cursor() as cur:
        sql = "SELECT COUNT(*) as total_orders FROM `orders` WHERE `event_id`=%s"
        cur.execute(sql, (event_id,))

        result = cur.fetchone()

    total_orders = result["total_orders"]

    if total_orders <= 0:
        return False

    with connection.cursor() as cur:
        sql = "SELECT COUNT(*) as total_refunded_orders FROM `order_reversals` WHERE `event_id`=%s"
        cur.execute(sql, (event_id,))

        result = cur.fetchone()

    total_refunded_orders = result["total_refunded_orders"]

    if total_orders == total_refunded_orders:
        return False

    return True
