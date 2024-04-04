from common.constants.event_categories import EVENT_CATEGORIES_NAME_BY_ID
from common.constants.event_statuses import EVENT_STATUS_NAME_BY_ID, PUBLISHED
from common.constants.ticket_types import FREE_TICKET, PAID_TICKET
from common.error_types import INVALID_REQUEST
from common.event_validation import (
    are_tickets_properly_configured,
    has_all_necessary_publish_event_data,
    has_paid_tickets_with_payout_instrument_assigned,
    is_payout_instrument_valid,
    is_prevalidate_request,
    is_valid_event_date_configuration,
    is_valid_event_from_path,
)
from common.http_utils import http_error_response
from common.rds_conn import create_rds_connection
from common.schema import is_valid_schema_request
from common.api_json_schemas import UPDATE_EVENT_SCHEMA

import json

connection = create_rds_connection()


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

    # TODO: logic to update event data

    return {"eventId": event_details["id"], "message": "Event successfully updated!"}
