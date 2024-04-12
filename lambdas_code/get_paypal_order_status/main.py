from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response
from common.paypal.client import PayPalClient

paypal_client = PayPalClient(None)


def lambda_handler(event, _):
    paypal_order_id = event.get("pathParameters", {}).get("id")

    if not paypal_order_id:
        return http_error_response(
            status_code=400,
            error_type=INVALID_REQUEST,
            error_detail="Please specify a valid paypal order id.",
        )

    status, status_code, err_msg = paypal_client.get_order_status(paypal_order_id)

    if err_msg:
        return http_error_response(
            status_code=status_code, error_type=status, error_detail=err_msg
        )

    return {"status": status}
