from common.error_types import INTERNAL_SERVER_ERROR
from common.http_utils import http_error_response, generic_server_error
import json


def test_http_error_response_returns_correct_http_format():
    error_type = "MY_ERROR"
    error_detail = "My error details..."
    status_code = 400
    expected_response = {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "body": json.dumps({"error_type": error_type, "error_detail": error_detail}),
        "headers": {"content-type": "application/json"},
    }

    assert (
        http_error_response(status_code, error_type, error_detail) == expected_response
    )


def test_generic_server_error_returns_correct_http_format():
    error_type = INTERNAL_SERVER_ERROR
    error_detail = "The server encountered an internal error, please try again later."
    status_code = 500
    expected_response = {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "body": json.dumps({"error_type": error_type, "error_detail": error_detail}),
        "headers": {"content-type": "application/json"},
    }

    assert generic_server_error() == expected_response
