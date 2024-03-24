import json

from common.error_types import INTERNAL_SERVER_ERROR


def http_error_response(status_code, error_type, error_detail):
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "body": json.dumps({"error_type": error_type, "error_detail": error_detail}),
        "headers": {"content-type": "application/json"},
    }


def generic_server_error():
    return {
        "isBase64Encoded": False,
        "statusCode": 500,
        "body": json.dumps(
            {
                "error_type": INTERNAL_SERVER_ERROR,
                "error_detail": "The server encountered an internal error, please try again later.",
            }
        ),
        "headers": {"content-type": "application/json"},
    }
