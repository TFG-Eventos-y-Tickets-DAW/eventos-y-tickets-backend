from common.constants.event_statuses import PUBLISHED
from common.constants.order_statuses import COMPLETED_ID
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key


def is_payout_instrument_valid(payout_instrument, is_free_event, desired_event_status):
    """
    When creating/updating an event, a payout instrument is optional
    so, an empty payout_instrument is valid.
    If a payout instrument is specified, then it should be
    iban + swift/bic OR a PayPal Email, but not both.
    """
    if (
        not payout_instrument
        and desired_event_status != PUBLISHED
        and not is_free_event
    ):
        return True

    iban = payout_instrument.get("iban", "")
    swiftbic = payout_instrument.get("swiftbic", "")
    paypal_email = payout_instrument.get("paypalEmail", "")

    if (iban != "" or swiftbic != "") and paypal_email != "":
        return False

    if (iban != "" and swiftbic == "") or (iban == "" and swiftbic != ""):
        return False

    return True


def is_prevalidate_request(body):
    return bool(body.get("preValidate"))


def is_valid_event_from_path(event_id, connection):
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


def has_all_necessary_publish_event_data(body, is_free_event):
    """
    This function will perform checks on body received
    to ensure that all necessary event data is filled
    before publishing the event.
    The event must have configured:
       - startsAt and endsAt fields set
       - country field set
       - payout instrument information set
       - category field set
    """
    tickets = body.get("tickets")
    starts_at = body.get("startsAt")
    ends_at = body.get("endsAt")
    country = body.get("country")
    category = body.get("category")
    address = body.get("address")

    if (
        not tickets
        or not starts_at
        or not ends_at
        or not country
        or not category
        or not address
    ):
        # Required fields to publish not set
        return False

    payout_instrument = body.get("payoutInstrument")

    if not is_free_event and not payout_instrument:
        return False

    return True


def are_tickets_properly_configured(body, tickets):
    ticket_price = tickets.get("price", 0)
    ticket_quantity = tickets.get("quantity")

    if ticket_quantity is not None and ticket_quantity <= 0:
        return False, "Ticket quantity must be greater than 0."

    if ticket_price < 0:
        return False, "Ticket price can't be negative."

    currency = body.get("currency")
    country = body.get("country")

    if ticket_price > 0 and not currency:
        return False, "Paid tickets should have a currency set."
    if ticket_price > 0 and not country:
        return False, "Paid tickets should have a country set."

    return True, ""


def is_valid_event_date_configuration(body):
    starts_at = body.get("startsAt")
    ends_at = body.get("endsAt")

    if starts_at is not None and ends_at is None:
        return False, "Please define an end date."
    if starts_at is None and ends_at is not None:
        return False, "Please define a start date."

    if starts_at is not None and ends_at is not None:
        starts_at_datetime = datetime.strptime(
            starts_at, "%Y-%m-%d %H:%M:%S"
        ).astimezone(timezone.utc)
        ends_at_datetime = datetime.strptime(ends_at, "%Y-%m-%d %H:%M:%S").astimezone(
            timezone.utc
        )
        now_datetime = datetime.now(timezone.utc)

        if now_datetime >= starts_at_datetime or now_datetime >= ends_at_datetime:
            return False, "The event start/end date cannot be in the past."

        if starts_at_datetime >= ends_at_datetime:
            return (
                False,
                "The event start date cannot be greater or equal than the event end date.",
            )

    return True, ""


def has_paid_tickets_with_payout_instrument_assigned(
    tickets, payout_instrument, desired_event_status
):
    if not tickets and not payout_instrument and desired_event_status != PUBLISHED:
        # It's ok to don't have this fields defined in DRAFT events
        return True

    ticket_price = tickets.get("price", 0)
    if ticket_price > 0 and not payout_instrument:
        # If tickets are paid, then a payout instrument is mandatory, independently if the event is draft
        return False

    return True


def retrieve_tickets_details_by_event_id(event_id, connection, order_sessions_table):
    with connection.cursor() as cur:
        select_sql = "SELECT `id`, `quantity`, `price`, `type_id` FROM `tickets` WHERE `event_id`=%s"
        cur.execute(select_sql, (event_id,))
        ticket_details = cur.fetchone()

        select_sql = "SELECT COUNT(*) as orders_sold FROM `orders` WHERE `event_id`=%s AND `status_id` = %s"
        cur.execute(select_sql, (event_id, COMPLETED_ID))
        order_details = cur.fetchone()

        select_sql = "SELECT COUNT(*) as orders_refunded FROM `order_reversals` WHERE `event_id`=%s"
        cur.execute(select_sql, (event_id,))
        order_refund_details = cur.fetchone()

        # We also take into consideration active Order Sessions for the event
        response = order_sessions_table.query(
            IndexName="EventIdIndex",
            KeyConditionExpression=Key("eventId").eq(str(event_id)),
        )
        active_order_sessions_count = response.get("Count", 0)

        ticket_details["quantityAvailable"] = (
            ticket_details["quantity"]
            - active_order_sessions_count
            - order_details["orders_sold"]
            + order_refund_details["orders_refunded"]
        )

    return ticket_details
