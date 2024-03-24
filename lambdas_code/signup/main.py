import json
import bcrypt

from common.http_utils import generic_server_error, http_error_response
from common.rds_conn import create_rds_connection
from common.schema import is_valid_schema_request
from common.api_json_schemas import SIGN_UP_SCHEMA

connection = create_rds_connection()


@is_valid_schema_request(SIGN_UP_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    if is_duplicate_user(body):
        return http_error_response(
            status_code=400,
            error_type="USER_ALREADY_EXISTS",
            error_detail="A user already exists with given email and anonymous flag.",
        )

    try:
        return create_new_user_in_db(body)
    except Exception as exc:
        print(exc)
        return generic_server_error()


def create_new_user_in_db(body):
    first_name = body.get("firstName")
    last_name = body.get("lastName")
    email = body.get("email")
    password = encrypt_password(body.get("password"))
    is_anonymous = body.get("isAnonymous")

    with connection.cursor() as cur:
        sql = "INSERT INTO `users` (`first_name`, `last_name`, `email`, `password`, `is_anonymous`) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(sql, (first_name, last_name, email, password, is_anonymous))

        connection.commit()

        select_sql = "SELECT `id`, `first_name`, `last_name`, `email`, `is_anonymous` FROM `users` WHERE `email`=%s AND `is_anonymous`=%s"
        cur.execute(select_sql, (email, is_anonymous))

        return cur.fetchone()


def is_duplicate_user(body):
    email = body.get("email")
    is_anonymous = body.get("isAnonymous")

    with connection.cursor() as cur:
        select_sql = "SELECT `id`, `first_name`, `last_name`, `email`, `is_anonymous` FROM `users` WHERE `email`=%s AND `is_anonymous`=%s"
        cur.execute(select_sql, (email, is_anonymous))
        if cur.fetchone() is not None:
            return True
    return False


def encrypt_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(bytes(password, "utf-8"), salt)
