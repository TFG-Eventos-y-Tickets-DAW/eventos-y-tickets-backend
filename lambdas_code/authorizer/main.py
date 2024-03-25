from common.jwt_utils import (
    get_jwt_secret,
    decode_jwt_token,
)
import jwt

jwt_secret = get_jwt_secret()


# Will throw:
# - Forbidden if token is invalid or expired
# - Unauthorized if no Authorization header provided
def lambda_handler(event, _):
    headers = event.get("headers", {})
    jwt_token = headers.get("authorization", "").split(" ")[
        -1
    ]  # Get Token (Bearer <token>)

    try:
        decode_jwt_token(jwt_token, jwt_secret)
        return {"isAuthorized": True}
    except (
        jwt.exceptions.ExpiredSignatureError,
        jwt.exceptions.InvalidTokenError,
        jwt.exceptions.InvalidKeyError,
        jwt.exceptions.DecodeError,
    ):
        return {"isAuthorized": False}
    except Exception as exc:
        print(exc)
        return {"isAuthorized": False}
