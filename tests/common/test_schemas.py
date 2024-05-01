from common.error_types import INVALID_REQUEST
from common.http_utils import http_error_response
from common.schema import is_valid_schema_request
import json


MY_JSON_SCHEMA_REQUEST = {
    "type": "object",
    "properties": {
        "firstName": {"type": "string", "minLength": 2},
        "lastName": {"type": "string", "minLength": 2},
    },
    "required": ["firstName", "lastName"],
}


def test_is_valid_schema_requests_execute_function_when_given_valid_request():

    @is_valid_schema_request(MY_JSON_SCHEMA_REQUEST)
    def my_func(event, _):
        return event

    event = {"body": json.dumps({"firstName": "Brayan", "lastName": "Ayala"})}
    context = {}

    res = my_func(event, context)

    assert res == event


def test_is_valid_schema_fails_when_request_is_missing_required_fields():

    @is_valid_schema_request(MY_JSON_SCHEMA_REQUEST)
    def my_func(event, _):
        return event

    event = {"body": json.dumps({"firstName": "Brayan"})}
    context = {}

    res = my_func(event, context)

    assert res == http_error_response(
        status_code=400,
        error_type=INVALID_REQUEST,
        error_detail="'lastName' is a required property",
    )


def test_is_valid_schema_fails_when_request_is_missing_field_constraints():

    @is_valid_schema_request(MY_JSON_SCHEMA_REQUEST)
    def my_func(event, _):
        return event

    event = {"body": json.dumps({"firstName": "a", "lastName": "b"})}
    context = {}

    res = my_func(event, context)

    assert res == http_error_response(
        status_code=400,
        error_type=INVALID_REQUEST,
        error_detail="Field error: `firstName` -> 'a' is too short",
    )
