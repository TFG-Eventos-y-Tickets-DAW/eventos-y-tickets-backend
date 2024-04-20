from common.constants.event_statuses import FINALIZED_ID
from common.constants.order_statuses import COMPLETED_ID
from common.payouts.helpers import calculate_payout_fee_by_total_amount
from common.rds_conn import create_rds_connection
import boto3
import os
import json

connection = create_rds_connection()
connection.autocommit(True)
sqs_resource = boto3.resource("sqs")
payouts_queue = sqs_resource.get_queue_by_name(
    QueueName=os.environ.get("PAYOUTS_QUEUE_NAME", "")
)


def lambda_handler(event, context):
    events = retrieve_events_ready_to_be_paid_out()
    events_with_calculated_payout_total = calculate_payout_total(events)
    sqs_formatted_events = prepare_events_for_sqs(events_with_calculated_payout_total)

    print("Events ready to be paid out: ", sqs_formatted_events)

    for prepared_events in chunker(sqs_formatted_events, 10):
        payouts_queue.send_messages(Entries=prepared_events)

    print("Event Payouts successfully sent!")

    return {}


def calculate_payout_total(events):
    results = []
    for event in events:
        gross_minus_paypal_fee = event["gross_minus_paypal_fee"]
        company_fee = calculate_payout_fee_by_total_amount(
            float(gross_minus_paypal_fee)
        )
        event["company_fee"] = company_fee
        event["net_total"] = round(gross_minus_paypal_fee - company_fee, 2)
        results.append(event)

    return results


def prepare_events_for_sqs(events):
    results = []
    for event in events:
        results.append(
            {
                "Id": str(event["id"]),
                "MessageGroupId": str(event["id"]),
                "MessageBody": json.dumps(event),
            }
        )

    return results


def retrieve_events_ready_to_be_paid_out():
    with connection.cursor() as cur:
        sql = "SELECT e.id, e.owner_id, SUM(o.total) as gross_total, SUM(pj.paypal_fee) AS paypal_fee, \
               (SUM(o.total) - SUM(pj.paypal_fee)) AS gross_minus_paypal_fee \
               FROM events e \
               LEFT JOIN payouts p \
               ON e.id = p.event_id \
               JOIN orders o \
               ON e.id = o.event_id \
               JOIN paypal_journal pj \
               ON pj.order_id = o.id \
               WHERE p.event_id is NULL AND \
               e.status_id = %s AND \
               o.status_id = %s AND \
               pj.paypal_fee IS NOT NULL AND \
               e.ends_at BETWEEN NOW() - interval 1 day AND NOW() \
               GROUP BY e.id, e.owner_id \
               HAVING gross_total > 0"
        cur.execute(sql, (FINALIZED_ID, COMPLETED_ID))
        result = cur.fetchall()
    return result


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
