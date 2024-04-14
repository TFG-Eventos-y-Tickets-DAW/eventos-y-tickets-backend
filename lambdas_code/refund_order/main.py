from common.constants.event_statuses import PUBLISHED_ID
from common.constants.order_statuses import COMPLETED_ID, ORDER_STATUS_NAME_BY_ID, REFUNDED, REFUNDED_ID
from common.error_types import INVALID_REQUEST
from common.event_utils import get_user_id_from_jwt
from common.http_utils import generic_server_error, http_error_response
from common.jwt_utils import get_jwt_secret
from common.rds_conn import create_rds_connection

connection = create_rds_connection()
jwt_secret = get_jwt_secret()


def lambda_handler(event, _):
    order_id = event.get("pathParameters", {}).get("id")
    if not order_id:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="Please provide a valid order id.",
        )

    order_details = retrieve_order_details(order_id)
    if not order_details:
        return http_error_response(
            status_code=404,
            error_type="NOT_FOUND",
            error_detail="The order id provided doesn't exist.",
        )

    headers = event.get("headers", {})
    current_user_id = get_user_id_from_jwt(headers, jwt_secret)
    if current_user_id != order_details["owner_id"]:
        return http_error_response(
            status_code=401,
            error_type="PERMISSION_DENIED",
            error_edtail="You are not allowed to refund this order, only the event owner can do it.",
        )

    if order_details["event_status_id"] != PUBLISHED_ID:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="The event associated to the order has already finished."
        )

    if order_details["order_status_id"] != COMPLETED_ID:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail=f"The status of this order is not refundable. - {ORDER_STATUS_NAME_BY_ID.get(order_details["order_status_id"])}"
        )

    try:
        create_order_reversal_record(order_id, order_details["event_id"], order_details["total"])
        update_order_status_in_database(order_id, REFUNDED_ID)
        connection.commit()
    except Exception as exc:
        print(f"An error ocurred while refunding the order {order_id} - {exc}")
        return generic_server_error()

    return {"status": REFUNDED, "orderId": order_id, "total": order_details["total"]}


def retrieve_order_details(order_id):
    with connection.cursor() as cur:
        sql = "SELECT o.id, e.id as event_id, e.owner_id, o.status_id as order_status_id, e.status_id as event_status_id, o.total, o.quantity FROM orders o JOIN events e ON o.event_id = e.id WHERE o.id = %s"
        cur.execute(sql, (order_id,))
        result = cur.fetchone()

    return result


def create_order_reversal_record(order_id, event_id, total):
    with connection.cursor() as cur:
        sql = "INSERT INTO `order_reversals` (`order_id`, `event_id`, `total`) VALUES (%s, %s, %s)"
        cur.execute(sql, (order_id, event_id, total))


def update_order_status_in_database(order_id, status_id):
    with connection.cursor() as cur:
        sql = "UPDATE `orders` SET `status_id` = %s WHERE id = %s"
        cur.execute(
            sql,
            (status_id, order_id),
        )
