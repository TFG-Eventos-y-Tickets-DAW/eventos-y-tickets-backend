from common.constants.event_categories import EVENT_CATEGORIES_ID_BY_NAME
from common.constants.event_statuses import EVENT_STATUS_ID_BY_NAME
from common.constants.ticket_types import FREE_TICKET, PAID_TICKET
from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response, generic_server_error
from common.rds_conn import create_rds_connection
from common.jwt_utils import get_jwt_secret, decode_jwt_token
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

    if is_prevalidate_request(body):
        # If it reached until this point, then schema is ok
        # So we don't perform database operations
        return {"preValidate": True, "message": "Event pre-validation accepted."}

    current_user_id = get_user_id_from_jwt(headers)

    # Start by creating the payout instrument record
    # since it will be directly referenced by the event record
    payout_instrument = body.get("payoutInstrument", {}) or {}
    if not is_payout_instrument_valid(payout_instrument):
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="The payout instrument should be an IBAN + SWIFT/BIC or PayPal email but not both.",
        )

    try:
        payout_instrument_id = create_payout_instrument(
            payout_instrument, current_user_id
        )
    except Exception as exc:
        print(exc)
        return generic_server_error()

    try:
        event_id = create_event(body, current_user_id, payout_instrument_id)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    try:
        create_tickets(body, event_id)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    # Persist tables locally created to DB
    connection.commit()

    return {"eventId": event_id, "message": "Event successfully created!"}


def is_prevalidate_request(body):
    return bool(body.get("preValidate"))


def get_user_id_from_jwt(headers):
    jwt_token = headers.get("authorization", "").split(" ")[
        -1
    ]  # Get Token (Bearer <token>)
    return decode_jwt_token(jwt_token, jwt_secret).get("userId")


def is_payout_instrument_valid(payout_instrument):
    """
    When creating a new event, a payout instrument is optional
    so, an empty payout_instrument is valid.
    If a payout instrument is specified, then it should be
    iban + swift/bic OR a PayPal Email, but not both.
    """
    if not payout_instrument:
        return True

    iban = payout_instrument.get("iban", "")
    swiftbic = payout_instrument.get("swiftbic", "")
    paypal_email = payout_instrument.get("paypalEmail", "")

    if (iban != "" or swiftbic != "") and paypal_email != "":
        return False

    if (iban != "" and swiftbic == "") or (iban == "" and swiftbic != ""):
        return False

    return True


def create_payout_instrument(payout_instrument, owner_id):
    payout_instrument_id = None

    with connection.cursor() as cur:
        sql = "INSERT INTO `payout_instruments` (`owner_id`, `iban`, `swift_bic`, `paypal_email`, `is_deleted`) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                owner_id,
                payout_instrument.get("iban", ""),
                payout_instrument.get("swiftbic", ""),
                payout_instrument.get("paypalEmail", ""),
                False,
            ),
        )
        payout_instrument_id = cur.lastrowid

    return payout_instrument_id


def create_event(body, owner_id, payout_instrument_id):
    event_id = None

    with connection.cursor() as cur:
        sql = "INSERT INTO `events` (`owner_id`, `title`, `description`, `img_src`, `starts_at`, `ends_at`, `status_id`, `category_id`, `country`, `currency`, `payout_instrument_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
                payout_instrument_id,
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
