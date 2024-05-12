from common.constants.event_statuses import DELETED_ID
from common.event_utils import (
    convert_datetime_to_strings,
    format_and_prepare_event_details,
    get_user_id_from_jwt,
)
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection
import humps

connection = create_rds_connection()
connection.autocommit(True)
jwt_secret = get_jwt_secret()


def lambda_handler(event, _):
    headers = event.get("headers", {})

    current_user_id = get_user_id_from_jwt(headers, jwt_secret)
    user_events = fetch_all_events_by_user_id(current_user_id)

    if len(user_events) == 0:
        return {"events": []}

    formatted_events = list(map(format_events, user_events))
    return {"events": formatted_events}


def format_events(event_details: dict):
    new_event_details = event_details.copy()
    format_and_prepare_event_details(new_event_details)
    convert_datetime_to_strings(new_event_details)
    return humps.camelize(new_event_details)


def fetch_all_events_by_user_id(owner_id):
    with connection.cursor() as cur:
        select_sql = "SELECT * FROM `events` WHERE `owner_id`=%s AND `status_id` != %s"
        cur.execute(select_sql, (owner_id, DELETED_ID))

        result = cur.fetchall()

    return result
