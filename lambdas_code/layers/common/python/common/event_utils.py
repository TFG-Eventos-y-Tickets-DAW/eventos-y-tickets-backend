from common.constants.event_categories import EVENT_CATEGORIES_NAME_BY_ID
from common.constants.event_statuses import EVENT_STATUS_NAME_BY_ID
from common.jwt_utils import decode_jwt_token

EVENT_IMAGE_PLACEHOLDER = (
    "https://eventos-y-tickets-event-images.s3.amazonaws.com/placeholder.jpg"
)


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
