from common.constants.event_statuses import FINALIZED_ID
from common.rds_conn import create_rds_connection


connection = create_rds_connection()


def lambda_handler(event, _):
    failed_event_ids = []

    for record in event["Records"]:
        record_keys = record.get("dynamodb", {}).get("Keys", {})
        event_id = int(record_keys.get("eventId", {}).get("S", 0))
        try:
            finalize_event_by_id(event_id)
        except Exception as exc:
            print(f"Failed to finalize event id {event_id} - {exc}")

    return {"failed_event_ids": failed_event_ids}


def finalize_event_by_id(event_id):
    with connection.cursor() as cur:
        sql = "UPDATE `events` SET `status_id` = %s WHERE id = %s"
        cur.execute(sql, (FINALIZED_ID, event_id))

    connection.commit()
