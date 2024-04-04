from functools import wraps
from jsonschema import validate, exceptions
from common.http_utils import http_error_response
import json

from common.error_types import (
    INVALID_REQUEST,
    INTERNAL_SERVER_ERROR,
)


def is_valid_schema_request(schema: dict):
    def f_wrapper(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                body = json.loads(event.get("body") or "{}")
                validate(instance=body, schema=schema)

                return func(event, context)
            except exceptions.ValidationError as exc:
                affected_field = exc.path[0] if len(exc.path) > 0 else ""
                err_msg = ""

                if affected_field != "":
                    err_msg = f"Field error: `{affected_field}` -> {exc.message}"
                else:
                    err_msg = exc.message

                return http_error_response(
                    status_code=400, error_type=INVALID_REQUEST, error_detail=err_msg
                )
            except Exception as exc:
                print(exc)
                raise exc
                return http_error_response(
                    status_code=500,
                    error_type=INTERNAL_SERVER_ERROR,
                    error_detail="An unknown error happened while validating request.",
                )

        return wrapper

    return f_wrapper
