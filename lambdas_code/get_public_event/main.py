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
import boto3
import os

connection = create_rds_connection()
connection.autocommit(True)

dynamodb_resource = boto3.resource("dynamodb")
order_sessions_table = dynamodb_resource.Table(
    os.environ.get("ORDER_SESSIONS_TABLE_NAME", "")
)
event_views_table = dynamodb_resource.Table(
    os.environ.get("EVENT_VIEWS_TABLE_NAME", "")
)


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
            event_details["id"], connection, order_sessions_table
        )
        if tickets_details is not None:
            tickets_details["type"] = TICKET_TYPE_NAME_BY_ID[tickets_details["type_id"]]
            del tickets_details["type_id"]
    except Exception as exc:
        print(exc)
        return generic_server_error()

    event_details["tickets"] = tickets_details

    # Event views counter
    update_event_views_counter(str(event_details["id"]))

    return humps.camelize(event_details)


def update_event_views_counter(event_id):
    event_views_metadata = event_views_table.get_item(Key={"eventId": event_id})
    if "Item" not in event_views_metadata:
        event_views_table.put_item(
            Item={
                "eventId": event_id,
                "viewCount": 1,
            }
        )
    else:
        event_views_table.update_item(
            Key={
                "eventId": event_id,
            },
            UpdateExpression="SET viewCount = viewCount + :val",
            ExpressionAttributeValues={":val": 1},
            ReturnValues="UPDATED_NEW",
        )
