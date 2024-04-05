from common.constants.event_categories import (
    EVENT_CATEGORIES_ID_BY_NAME,
)
from common.constants.event_statuses import (
    EVENT_STATUS_ID_BY_NAME,
    PUBLISHED,
)
from common.constants.ticket_types import FREE_TICKET, PAID_TICKET
from common.error_types import INVALID_REQUEST
from common.event_utils import get_user_id_from_jwt
from common.event_validation import (
    are_tickets_properly_configured,
    has_all_necessary_publish_event_data,
    has_paid_tickets_with_payout_instrument_assigned,
    is_payout_instrument_valid,
    is_prevalidate_request,
    is_valid_event_date_configuration,
    is_valid_event_from_path,
)
from common.http_utils import generic_server_error, http_error_response
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection
from common.schema import is_valid_schema_request
from common.api_json_schemas import UPDATE_EVENT_SCHEMA

import json

connection = create_rds_connection()
jwt_secret = get_jwt_secret()


@is_valid_schema_request(UPDATE_EVENT_SCHEMA)
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

    body = json.loads(event.get("body", {})) or {}
    headers = event.get("headers", {})
    current_user_id = get_user_id_from_jwt(headers, jwt_secret)

    if current_user_id != event_details["owner_id"]:
        return http_error_response(
            status_code=401,
            error_type="UNAUTHORIZED",
            error_detail="You are not allowed to update this event.",
        )

    # Publish status data validation
    desired_event_status = body.get("status")
    is_free_event = body.get("tickets", {}).get("price", 0) <= 0
    if desired_event_status == PUBLISHED and not has_all_necessary_publish_event_data(
        body, is_free_event
    ):
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="You can't publish the event, please fill all required fields: `address`, `category`, `tickets`, `payoutInstrument`, `country`, `startsAt`, `endsAt`.",
        )

    # Payout instrument validation
    payout_instrument = body.get("payoutInstrument", {}) or {}
    is_free_event = body.get("tickets", {}).get("price", 0) <= 0
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
        # Schema and validation above passed, so we are fine to approve the request
        return {"preValidate": True, "message": "Event pre-validation accepted."}

    # Update Event record
    print("UPDATING EVENT RECORD...")
    try:
        update_event(body, event_details)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    # Update Payout Instrument record
    print("UPDATING PAYOUT INSTRUMENT...")
    try:
        if not is_free_event:
            update_or_create_payout_instrument(payout_instrument, event_details)
    except Exception as exc:
        print(exc)
        return generic_server_error()

    # Update Tickets
    print("UPDATING TICKETS...")
    try:
        if tickets:
            update_or_create_tickets(body, event_details["id"])
    except Exception as exc:
        print(exc)
        return generic_server_error()

    # Save changes to DB
    print("SAVING CHANGES TO DB...")
    connection.commit()

    return {"eventId": event_details["id"], "message": "Event successfully updated!"}


def update_event(body, event_details):
    """
    Update event with given body value or defaults to existing event table values.
    """
    new_title = body.get("title", event_details["title"])
    new_description = body.get("description", event_details["description"])
    new_address = body.get("address", event_details["address"])
    new_img_src = body.get("imgSrc", event_details["img_src"])
    new_starts_at = body.get("startsAt", event_details["starts_at"])
    new_ends_at = body.get("endsAt", event_details["ends_at"])
    new_status = (
        EVENT_STATUS_ID_BY_NAME.get(body["status"]) or event_details["status_id"]
    )
    new_category = (
        EVENT_CATEGORIES_ID_BY_NAME.get(body.get("category", ""))
        or event_details["category_id"]
    )
    new_currency = body.get("currency", event_details["currency"])
    new_country = body.get("country", event_details["country"])

    with connection.cursor() as cur:
        sql = "UPDATE `events` SET `title` = %s, `description` = %s, `address` = %s, `img_src` = %s, `starts_at` = %s, `ends_at` = %s, `status_id` = %s, `category_id` = %s, `country` = %s, `currency` = %s WHERE `id` = %s"
        cur.execute(
            sql,
            (
                (
                    new_title
                    if event_details["title"] != new_title
                    else event_details["title"]
                ),
                (
                    new_description
                    if event_details["description"] != new_description
                    else event_details["description"]
                ),
                (
                    new_address
                    if event_details["address"] != new_address
                    else event_details["address"]
                ),
                (
                    new_img_src
                    if event_details["img_src"] != new_img_src
                    else event_details["img_src"]
                ),
                (
                    new_starts_at
                    if event_details["starts_at"] != new_starts_at
                    else event_details["starts_at"]
                ),
                (
                    new_ends_at
                    if event_details["ends_at"] != new_ends_at
                    else event_details["ends_at"]
                ),
                (
                    new_status
                    if event_details["status_id"] != new_status
                    else event_details["status_id"]
                ),
                (
                    new_category
                    if event_details["category_id"] != new_category
                    else event_details["category_id"]
                ),
                (
                    new_country
                    if event_details["country"] != new_country
                    else event_details["country"]
                ),
                (
                    new_currency
                    if event_details["currency"] != new_currency
                    else event_details["currency"]
                ),
                event_details["id"],
            ),
        )


def update_or_create_payout_instrument(payout_instrument, event_details):
    payout_details = False

    with connection.cursor() as cur:
        sql = "SELECT * FROM payout_instruments WHERE event_id = %s"
        cur.execute(sql, (event_details["id"],))

        payout_details = cur.fetchone()

    if payout_details is None:
        with connection.cursor() as cur:
            sql = "INSERT INTO `payout_instruments` (`owner_id`, `event_id`, `iban`, `swift_bic`, `paypal_email`, `is_deleted`) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(
                sql,
                (
                    event_details["owner_id"],
                    event_details["id"],
                    payout_instrument.get("iban", ""),
                    payout_instrument.get("swiftbic", ""),
                    payout_instrument.get("paypalEmail", ""),
                    False,
                ),
            )
    else:
        existing_iban = payout_details.get("iban", "")
        existing_swiftbic = payout_details.get("swift_bic", "")
        existing_paypal = payout_details.get("paypal_email", "")

        new_iban = payout_instrument.get("iban", "")
        new_swiftbic = payout_instrument.get("swiftbic", "")
        new_paypal = payout_instrument.get("paypalEmail", "")

        with connection.cursor() as cur:
            sql = "UPDATE `payout_instruments` SET `iban` = %s, `swift_bic` = %s, `paypal_email` = %s WHERE id = %s"
            cur.execute(
                sql,
                (
                    new_iban if new_iban != existing_iban else existing_iban,
                    (
                        new_swiftbic
                        if new_swiftbic != existing_swiftbic
                        else existing_swiftbic
                    ),
                    new_paypal if new_paypal != existing_paypal else existing_paypal,
                    payout_details["id"],
                ),
            )


def update_or_create_tickets(body, event_id):
    tickets = body.get("tickets", {})
    quantity = tickets.get("quantity", 0)
    price = tickets.get("price", 0.0)
    ticket_type = FREE_TICKET if price <= 0.0 else PAID_TICKET

    ticket_details = False

    with connection.cursor() as cur:
        sql = "SELECT * FROM tickets WHERE event_id = %s"
        cur.execute(sql, (event_id,))

        ticket_details = cur.fetchone()

    if ticket_details is None:
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
    else:
        old_quantity = ticket_details.get("quantity")
        old_price = ticket_details.get("price")
        old_ticket_type = ticket_details.get("type_id")

        with connection.cursor() as cur:
            sql = "UPDATE `tickets` SET `quantity` = %s, `price` = %s, `type_id` = %s WHERE id = %s"
            cur.execute(
                sql,
                (
                    quantity if old_quantity != quantity else old_quantity,
                    price if old_price != price else old_price,
                    ticket_type if old_ticket_type != ticket_type else old_ticket_type,
                    ticket_details["id"],
                ),
            )
