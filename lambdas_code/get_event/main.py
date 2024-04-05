from common.constants.event_categories import EVENT_CATEGORIES_NAME_BY_ID
from common.constants.event_statuses import EVENT_STATUS_NAME_BY_ID
from common.constants.ticket_types import TICKET_TYPE_NAME_BY_ID
from common.event_utils import (
    convert_datetime_to_strings,
    format_and_prepare_event_details,
)
from common.http_utils import http_error_response, generic_server_error
from common.rds_conn import create_rds_connection
import humps

connection = create_rds_connection()
connection.autocommit(True)


def lambda_handler(event, _):

    is_valid_event_id, event_details = is_valid_event_from_path(
        event.get("pathParameters", {}).get("id")
    )

    if not is_valid_event_id:
        return http_error_response(
            status_code=400,
            error_type="NOT_FOUND",
            error_detail="The event id passed was not found or it was malformed.",
        )

    # Prepare and enrich event details by replacing from id to string values
    format_and_prepare_event_details(event_details)
    # Format date
    convert_datetime_to_strings(event_details)

    # Retrieve payout instrument information
    try:
        payout_instrument_details = retrieve_payout_instrument_by_event_id(
            event_details["id"]
        )
    except Exception as exc:
        print(exc)
        return generic_server_error()

    event_details["payout_instrument"] = payout_instrument_details

    # Retrieve tickets configuration information
    try:
        tickets_details = retrieve_tickets_configuration_by_event_id(
            event_details["id"]
        )
        if tickets_details is not None:
            tickets_details["type"] = TICKET_TYPE_NAME_BY_ID[tickets_details["type_id"]]
            del tickets_details["type_id"]
    except Exception as exc:
        print(exc)
        return generic_server_error()

    event_details["tickets_configuration"] = tickets_details

    return humps.camelize(event_details)


def is_valid_event_from_path(event_id):
    if event_id is None:
        return False, None

    try:
        event_id_int = int(event_id)
    except ValueError:
        return False, None
    except Exception as exc:
        print(exc)
        return False, None

    try:
        with connection.cursor() as cur:
            select_sql = "SELECT * FROM `events` WHERE `id`=%s"
            cur.execute(select_sql, (event_id_int,))

            result = cur.fetchone()

        if result is None:
            return False, None

    except Exception as exc:
        print(exc)
        return False, None

    return True, result


def retrieve_payout_instrument_by_event_id(event_id):
    with connection.cursor() as cur:
        select_sql = "SELECT `iban`, `swift_bic`, `paypal_email` FROM `payout_instruments` WHERE `event_id`=%s"
        cur.execute(select_sql, (event_id,))

        result = cur.fetchone()

    return result


def retrieve_tickets_configuration_by_event_id(event_id):
    with connection.cursor() as cur:
        select_sql = (
            "SELECT `quantity`, `price`, `type_id` FROM `tickets` WHERE `event_id`=%s"
        )
        cur.execute(select_sql, (event_id,))

        result = cur.fetchone()

    return result
