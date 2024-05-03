from common.constants.order_statuses import ABANDONED, ABANDONED_ID
from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response
from common.paypal.client import PayPalClient
from common.rds_conn import create_rds_connection


paypal_client = PayPalClient(None)
connection = create_rds_connection()
connection.autocommit(True)


def lambda_handler(event, _):
    paypal_order_id = event.get("pathParameters", {}).get("paypal_id")
    order_id = event.get("pathParameters", {}).get("order_id")

    if not paypal_order_id:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="Please specify a valid paypal order id.",
        )

    order_status = retrieve_order_status(order_id)
    if order_status == ABANDONED_ID:
        return {"status": ABANDONED}

    status, status_code, err_msg = paypal_client.get_order_status(paypal_order_id)

    if err_msg:
        return http_error_response(
            status_code=status_code, error_type=status, error_detail=err_msg
        )

    return {"status": status}


def retrieve_order_status(order_id):
    with connection.cursor() as cur:
        sql = "SELECT status_id FROM orders WHERE id = %s"
        cur.execute(sql, (order_id,))
        res = cur.fetchone()

    return res.get("status_id")
