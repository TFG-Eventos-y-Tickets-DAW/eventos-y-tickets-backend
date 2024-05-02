from datetime import datetime, timedelta, timezone
from common.constants.event_categories import EVENT_CATEGORIES_NAME_BY_ID
from common.constants.event_statuses import EVENT_STATUS_NAME_BY_ID
from common.jwt_utils import decode_jwt_token

EVENT_IMAGE_PLACEHOLDER = "https://eventngreet.com/images/placeholder.jpg"


def format_and_prepare_event_details(event_details):
    if "category_id" in event_details:
        event_details["category"] = EVENT_CATEGORIES_NAME_BY_ID[
            event_details["category_id"]
        ]
        del event_details["category_id"]

    if "status_id" in event_details:
        event_details["status"] = EVENT_STATUS_NAME_BY_ID[event_details["status_id"]]
        del event_details["status_id"]


def convert_datetime_to_strings(event_details):
    if "starts_at" in event_details:
        event_details["starts_at"] = (
            event_details["starts_at"].strftime("%d-%m-%Y %H:%M:%S")
            if event_details["starts_at"] is not None
            else None
        )
    if "ends_at" in event_details:
        event_details["ends_at"] = (
            event_details["ends_at"].strftime("%d-%m-%Y %H:%M:%S")
            if event_details["ends_at"] is not None
            else None
        )

    if "created_at" in event_details:
        event_details["created_at"] = (
            event_details["created_at"].strftime("%d-%m-%Y %H:%M:%S")
            if event_details["created_at"] is not None
            else None
        )


def get_user_id_from_jwt(headers, jwt_secret):
    jwt_token = headers.get("authorization", "").split(" ")[
        -1
    ]  # Get Token (Bearer <token>)
    return decode_jwt_token(jwt_token, jwt_secret).get("userId")


def get_user_data_from_jwt(headers, jwt_secret):
    jwt_token = headers.get("authorization", "").split(" ")[
        -1
    ]  # Get Token (Bearer <token>)
    return decode_jwt_token(jwt_token, jwt_secret)


def get_ttl_for_the_next_minutes(minutes: int):
    utc_now = datetime.now(timezone.utc)
    future_time = utc_now + timedelta(minutes=minutes)
    epoch_future_time = int(future_time.timestamp())
    return epoch_future_time


def assign_event_lifcycle_ends_at_ttl(event_lifecycle_table, event_id, ends_at):
    """
    Creates or updates the DynamoDB event lifecycle table
    with the ends at date from the event created/updated
    """
    ends_at_datetime = datetime.strptime(ends_at, "%Y-%m-%d %H:%M:%S") - timedelta(
        hours=2
    )  # not ideal but for now its ok, it would be better if we infer the user local zone
    epoch_time = int(ends_at_datetime.timestamp())

    event_lifecycle_table.put_item(Item={"eventId": str(event_id), "ttl": epoch_time})


def delete_event_lifecycle_ttl(event_lifecycle_table, event_id):
    event_lifecycle_table.delete_item(Key={"eventId": str(event_id)})
