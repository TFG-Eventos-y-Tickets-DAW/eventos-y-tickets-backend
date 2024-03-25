from common.jwt_utils import (
    get_jwt_secret,
    decode_jwt_token,
)

jwt_secret = get_jwt_secret()


def lambda_handler(event, _):
    headers = event.get("headers", {})
    jwt_token = headers.get("authorization", "").split(" ")[
        -1
    ]  # Get Token (Bearer <token>)

    return decode_jwt_token(jwt_token, jwt_secret)
