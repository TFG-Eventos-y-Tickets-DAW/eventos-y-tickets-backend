from common.http_utils import generic_server_error
from common.jwt_utils import (
    expired_invalid_jwt_http_response,
    get_jwt_secret,
    decode_jwt_token,
)
import jwt

jwt_secret = get_jwt_secret()


def lambda_handler(event, _):
    headers = event.get("headers", {})
    jwt_token = headers.get("authorization", "").split(" ")[
        -1
    ]  # Get Token (Bearer <token>)

    try:
        return decode_jwt_token(jwt_token, jwt_secret)
    except (
        jwt.exceptions.ExpiredSignatureError,
        jwt.exceptions.InvalidTokenError,
        jwt.exceptions.InvalidKeyError,
        jwt.exceptions.DecodeError,
    ):
        return expired_invalid_jwt_http_response()
    except Exception as exc:
        print(exc)
        return generic_server_error()
