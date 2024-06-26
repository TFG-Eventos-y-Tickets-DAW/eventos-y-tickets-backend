from common.api_json_schemas import CREATE_ORDER_SCHEMA
from common.constants.event_statuses import PUBLISHED_ID
from common.constants.order_statuses import CREATED, CREATED_ID
from common.error_types import INVALID_REQUEST
from common.event_utils import (
    get_ttl_for_the_next_minutes,
    get_user_data_from_jwt,
)
from common.event_validation import (
    is_valid_event_from_path,
    retrieve_tickets_details_by_event_id,
)
from common.http_utils import http_error_response, generic_server_error
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection
from common.schema import is_valid_schema_request
from uuid import uuid4

import json
import boto3
import os

connection = create_rds_connection()
jwt_secret = get_jwt_secret()

dynamodb_resource = boto3.resource("dynamodb")
order_sessions_table = dynamodb_resource.Table(
    os.environ.get("ORDER_SESSIONS_TABLE_NAME", "")
)


@is_valid_schema_request(CREATE_ORDER_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}

    is_valid_event_id, event_details = is_valid_event_from_path(
        body.get("eventId"), connection
    )
    if not is_valid_event_id:
        return http_error_response(
            status_code=400,
            error_type="NOT_FOUND",
            error_detail="The event id passed was not found or it was malformed.",
        )

    if event_details.get("status_id") != PUBLISHED_ID:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="You can't create an order if the event is not PUBLISHED.",
        )

    # TODO: Free Order scenario -> create order directly.

    # Check if there are available tickets
    tickets_details = retrieve_tickets_details_by_event_id(
        event_details["id"], connection, order_sessions_table
    )
    if tickets_details.get("quantityAvailable") <= 0:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="The event doesn't have available tickets right now.",
        )

    total_amount, err_message = calculate_order_amount(body)
    if err_message:
        return http_error_response(
            status_code=400, error_type=INVALID_REQUEST, error_detail=err_message
        )

    headers = event.get("headers", {})
    current_auth_user = get_user_data_from_jwt(headers, jwt_secret)
    attendee = body.get("attendee")
    print("Current auth user: ", current_auth_user)

    # Scenario where the buyer user is already registered
    if current_auth_user:
        user_id = current_auth_user.get("userId")
    else:
        # Different attendee email than the auth user (or no auth user at all)
        user_id = create_or_infer_buyer_user_from_attendee_data(attendee)

    try:
        order_id = start_order_session(event_details, user_id, body, total_amount)
    except Exception as exc:
        print(f"Error while creating order session: {exc}")
        # Fail Order SQL here
        return generic_server_error()

    connection.commit()

    return {"orderId": order_id, "total": total_amount, "status": CREATED, **body}


def calculate_order_amount(body):
    total = 0

    with connection.cursor() as cur:
        sql = "SELECT `price` FROM `tickets` WHERE `id` = %s AND `event_id` = %s"
        cur.execute(sql, (body.get("ticketId"), body.get("eventId")))
        result = cur.fetchone()

    if result is None:
        return total, "It seems the ticket don't match with the event provided."

    total = round(result["price"] * body.get("quantity"), 2)

    return total, None


def create_order_in_database(event_details, user_id, body, total_amount):
    order_id = 0

    with connection.cursor() as cur:
        sql = "INSERT INTO `orders` (`event_id`, `ticket_id`, `payer_id`, `payee_id`, `status_id`, `total`, `quantity`) VALUES (%s, %s ,%s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                event_details["id"],
                body.get("ticketId"),
                user_id,
                event_details["owner_id"],
                CREATED_ID,
                total_amount,
                body.get("quantity"),
            ),
        )

        order_id = cur.lastrowid

    return order_id


def start_order_session(event_details, user_id, body, total_amount):
    order_id = str(uuid4()).split("-")[0]
    metadata = {
        "quantity": str(body.get("quantity")),
        "ticketId": str(body.get("ticketId")),
        "totalAmount": str(total_amount),
        "currency": str(event_details.get("currency", "")),
        "payerId": str(user_id),
        "payeeId": str(event_details["owner_id"]),
        "attendee": body.get("attendee", {}),
    }

    order_sessions_table.put_item(
        Item={
            "orderId": str(order_id),
            "eventId": str(event_details["id"]),
            "metadata": json.dumps(metadata),
            "ttl": get_ttl_for_the_next_minutes(15),
        }
    )

    return order_id


def create_or_infer_buyer_user_from_attendee_data(attendee):
    with connection.cursor() as cur:
        sql = "SELECT `id` FROM `users` WHERE `email` = %s AND `is_anonymous` = %s"
        cur.execute(sql, (attendee.get("email"), True))

        result = cur.fetchone()

    if result is not None:
        return result["id"]

    # We need to create an anonymous user
    anonymous_id = None
    with connection.cursor() as cur:
        sql = "INSERT INTO `users` (`first_name`, `email`, `is_anonymous`) VALUES (%s, %s, %s)"
        cur.execute(sql, (attendee.get("name"), attendee.get("email"), True))

        anonymous_id = cur.lastrowid
    return anonymous_id
