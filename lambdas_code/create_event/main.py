from common.constants.event_categories import EVENT_CATEGORIES_ID_BY_NAME
from common.constants.event_statuses import EVENT_STATUS_ID_BY_NAME, PUBLISHED
from common.event_utils import get_user_id_from_jwt
from common.event_validation import (
    are_tickets_properly_configured,
    has_all_necessary_publish_event_data,
    has_paid_tickets_with_payout_instrument_assigned,
    is_payout_instrument_valid,
    is_prevalidate_request,
    is_valid_event_date_configuration,
)
from common.constants.ticket_types import FREE_TICKET, PAID_TICKET
from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response, generic_server_error
from common.rds_conn import create_rds_connection
from common.jwt_utils import get_jwt_secret
from common.schema import is_valid_schema_request
from common.api_json_schemas import CREATE_EVENT_SCHEMA

import json

connection = create_rds_connection()
jwt_secret = get_jwt_secret()

EVENT_IMAGE_PLACEHOLDER = (
    "https://eventos-y-tickets-event-images.s3.amazonaws.com/placeholder.jpg"
)


@is_valid_schema_request(CREATE_EVENT_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    headers = event.get("headers", {})

    current_user_id = get_user_id_from_jwt(headers, jwt_secret)

    # Publish status data validation
    desired_event_status = body.get("status")
    is_free_event = body.get("tickets", {}).get("price", 0) <= 0
    if desired_event_status == PUBLISHED and not has_all_necessary_publish_event_data(
        body, is_free_event
    ):
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="You can't publish the event, please fill all required fields: `category`, `tickets`, `payoutInstrument`, `country`, `startsAt`, `endsAt`.",
        )

    # Start by creating the payout instrument record
    # since it will be directly referenced by the event record
    payout_instrument = body.get("payoutInstrument", {}) or {}
    if not is_payout_instrument_valid(
        payout_instrument, is_free_event, desired_event_status
    ):
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="The payout instrument should be an IBAN + SWIFT/BIC or PayPal email but not both.",
        )

    # Date validation startsAt vs endsAt, treated as UTC time
    is_valid_datetime, error_detail = is_valid_event_date_configuration(body)
    if not is_valid_datetime:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail=error_detail,
        )

    tickets = body.get("tickets", {})
    are_tickets_valid, ticket_err = are_tickets_properly_configured(body, tickets)
    if not are_tickets_valid:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail=ticket_err,
        )

    if not has_paid_tickets_with_payout_instrument_assigned(
        tickets, payout_instrument, desired_event_status
    ):
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="A payout instrument is required when setting paid tickets.",
        )

    if is_prevalidate_request(body):
        # If it reached until this point, then schema is ok
        # So we don't perform database operations
        return {"preValidate": True, "message": "Event pre-validation accepted."}

    try:
        event_id = create_event(body, current_user_id)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    try:
        if not is_free_event:
            create_payout_instrument(payout_instrument, current_user_id, event_id)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    try:
        if tickets:
            create_tickets(body, event_id)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    # Persist tables locally created to DB
    connection.commit()

    return {"eventId": event_id, "message": "Event successfully created!"}


def create_payout_instrument(payout_instrument, owner_id, event_id):
    with connection.cursor() as cur:
        sql = "INSERT INTO `payout_instruments` (`owner_id`, `event_id`, `iban`, `swift_bic`, `paypal_email`, `is_deleted`) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                owner_id,
                event_id,
                payout_instrument.get("iban", ""),
                payout_instrument.get("swiftbic", ""),
                payout_instrument.get("paypalEmail", ""),
                False,
            ),
        )


def create_event(body, owner_id):
    event_id = None

    with connection.cursor() as cur:
        sql = "INSERT INTO `events` (`owner_id`, `title`, `description`, `img_src`, `starts_at`, `ends_at`, `status_id`, `category_id`, `country`, `currency`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                owner_id,
                body.get("title"),
                body.get("description"),
                body.get("imgSrc", EVENT_IMAGE_PLACEHOLDER),
                body.get("startsAt"),
                body.get("endsAt"),
                EVENT_STATUS_ID_BY_NAME.get(body["status"]),
                EVENT_CATEGORIES_ID_BY_NAME.get(body.get("category", "OTHER")),
                body.get("country"),
                body.get("currency"),
            ),
        )
        event_id = cur.lastrowid

    return event_id


def create_tickets(body, event_id):
    tickets = body.get("tickets", {})
    quantity = tickets.get("quantity", 0)
    price = tickets.get("price", 0.0)
    ticket_type = FREE_TICKET if price <= 0.0 else PAID_TICKET

    with connection.cursor() as cur:
        sql = "INSERT INTO `tickets` (`event_id`, `quantity`, `price`, `type_id`) VALUES (%s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                event_id,
                quantity,
                price,
                ticket_type,
            ),
        )
