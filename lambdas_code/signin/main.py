import json
import bcrypt

from common.http_utils import generic_server_error, http_error_response
from common.rds_conn import create_rds_connection
from common.jwt_utils import create_jwt_token, get_jwt_secret
from common.schema import is_valid_schema_request
from common.api_json_schemas import SIGN_IN_SCHEMA

connection = create_rds_connection()
jwt_secret = get_jwt_secret()


@is_valid_schema_request(SIGN_IN_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}

    try:
        return find_and_authenticate_user(body)
    except Exception as exc:
        print(exc)
        return generic_server_error()


def find_and_authenticate_user(body):
    email = body.get("email")
    body_password = body.get("password")

    with connection.cursor() as cur:
        select_sql = "SELECT `id`, `first_name`, `last_name`, `email`, `password`, `is_anonymous` FROM `users` WHERE `email`=%s AND `is_anonymous`=%s"
        cur.execute(select_sql, (email, False))
        result = cur.fetchone()

    if result is None:
        return http_error_response(
            status_code=200,
            error_type="INCORRECT_CREDENTIALS",
            error_detail="The email or password provided is incorrect.",
        )

    hashed_password = result.get("password")

    if not is_correct_password(hashed_password, body_password):
        return http_error_response(
            status_code=200,
            error_type="INCORRECT_CREDENTIALS",
            error_detail="The email or password provided is incorrect.",
        )

    data_to_encode = {
        "firstName": result["first_name"],
        "lastName": result["last_name"],
        "email": result["email"],
        "isAnonymous": result["is_anonymous"],
        "userId": result["id"],
    }

    jwt_token = create_jwt_token(data_to_encode, jwt_secret)

    return {
        "accessToken": jwt_token,
        "firstName": result["first_name"],
        "lastName": result["last_name"],
        "email": result["email"],
        "userId": result["id"],
    }


def is_correct_password(hashed_password: str, body_password: str):
    return bcrypt.checkpw(
        bytes(body_password, "utf-8"), bytes(hashed_password, "utf-8")
    )
