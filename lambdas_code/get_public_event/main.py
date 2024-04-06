from common.constants.ticket_types import TICKET_TYPE_NAME_BY_ID
from common.event_utils import (
    convert_datetime_to_strings,
    format_and_prepare_event_details,
)
from common.event_validation import (
    is_valid_event_from_path,
    retrieve_tickets_details_by_event_id,
)
from common.http_utils import http_error_response, generic_server_error
from common.rds_conn import create_rds_connection
import humps

connection = create_rds_connection()
connection.autocommit(True)


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

    # Prepare and enrich event details by replacing from id to string values
    format_and_prepare_event_details(event_details)
    # Format date
    convert_datetime_to_strings(event_details)

    # Retrieve tickets configuration information
    try:
        tickets_details = retrieve_tickets_details_by_event_id(
            event_details["id"], connection
        )
        if tickets_details is not None:
            tickets_details["type"] = TICKET_TYPE_NAME_BY_ID[tickets_details["type_id"]]
            del tickets_details["type_id"]
    except Exception as exc:
        print(exc)
        return generic_server_error()

    event_details["tickets"] = tickets_details

    return humps.camelize(event_details)
