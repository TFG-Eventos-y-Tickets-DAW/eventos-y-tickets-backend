from common.rds_conn import create_rds_connection
import json

connection = create_rds_connection()
connection.autocommit(True)


def lambda_handler(event, context):
    failed_records = []

    records = event["Records"]
    for record in records:
        try:
            event_details = json.loads(record["body"])
            print(f"Creating Payout for Event Id: {event_details["id"]}")
            create_payout_record(event_details)
        except Exception as exc:
            print(f"Failed sending payout to event - {record} - {exc}")
            failed_records.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": failed_records}


def create_payout_record(event_details):
    with connection.cursor() as cur:
        sql = "INSERT INTO `payouts` (payee_id, event_id, gross_total, net_total, fee) \
              VALUES (%s, %s, %s, %s, %s)"
        cur.execute(
            sql,
            (
                event_details["owner_id"],
                event_details["id"],
                event_details["gross_total"],
                event_details["net_total"],
                event_details["company_fee"],
            ),
        )
