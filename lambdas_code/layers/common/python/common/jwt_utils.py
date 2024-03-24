import boto3
import jwt
from datetime import datetime, timezone, timedelta
from common.http_utils import http_error_response

TOKEN_EXPIRATION_IN_DAYS = 7


def get_jwt_secret():
    ssm = boto3.client("ssm")
    parameter = ssm.get_parameter(Name="/jwt/creds/secret", WithDecryption=True)
    return parameter.get("Parameter", {}).get("Value", "")


def create_jwt_token(data, secret):
    data["exp"] = datetime.now(tz=timezone.utc) + timedelta(
        days=TOKEN_EXPIRATION_IN_DAYS
    )
    return jwt.encode(data, secret, algorithm="HS256")


def decode_jwt_token(token, secret):
    return jwt.decode(token, secret, algorithms="HS256")


def expired_invalid_jwt_http_response():
    return http_error_response(
        status_code=401,
        error_type="INVALID_JWT_TOKEN",
        error_detail="The token provided is not valid or has expired.",
    )
