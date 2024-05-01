from unittest.mock import patch
from datetime import datetime
from common.http_utils import http_error_response
from common.jwt_utils import (
    create_jwt_token,
    decode_jwt_token,
    expired_invalid_jwt_http_response,
    get_jwt_secret,
)


@patch("boto3.client")
def test_get_jwt_secret_retrieves_ssm_parameter_jwt_secret(boto_client_mock):
    expected_jwt_secret = "my-jwt-secret!"
    ssm_client_mock = boto_client_mock.return_value
    ssm_client_mock.get_parameter.return_value = {
        "Parameter": {"Value": expected_jwt_secret}
    }

    retrieved_jwt_secret = get_jwt_secret()

    assert expected_jwt_secret == retrieved_jwt_secret
    ssm_client_mock.get_parameter.assert_called_once_with(
        Name="/jwt/creds/secret", WithDecryption=True
    )


@patch("boto3.client")
def test_get_jwt_secret_returns_empty_string_when_no_parameter_found(boto_client_mock):
    expected_jwt_secret = ""
    ssm_client_mock = boto_client_mock.return_value
    ssm_client_mock.get_parameter.return_value = {}

    retrieved_jwt_secret = get_jwt_secret()

    assert expected_jwt_secret == retrieved_jwt_secret
    ssm_client_mock.get_parameter.assert_called_once_with(
        Name="/jwt/creds/secret", WithDecryption=True
    )


@patch("jwt.encode")
def test_create_jwt_token_creates_expiration_and_calls_jwt_encoder(jwt_encode_mock):
    expected_encoded_jwt = "eyJhbGciOi..."
    jwt_secret = "mysecret!"
    jwt_encode_mock.return_value = expected_encoded_jwt

    data = {"userId": 1, "firstName": "Brayan"}

    encoded_token = create_jwt_token(data, jwt_secret)

    assert encoded_token == expected_encoded_jwt
    jwt_encode_mock.assert_called_once_with(data, jwt_secret, algorithm="HS256")

    assert "exp" in data
    assert type(data["exp"]) is datetime


@patch("jwt.decode")
def test_decode_jwt_token_calls_jwt_decoder_with_provided_token_and_secret(
    jwt_decode_mock,
):
    token = "eyJhbGciOi..."
    jwt_secret = "mysecret!"
    expected_data = {"userId": 1, "firstName": "Brayan"}
    jwt_decode_mock.return_value = expected_data

    decoded_token = decode_jwt_token(token, jwt_secret)

    assert decoded_token == expected_data
    jwt_decode_mock.assert_called_once_with(token, jwt_secret, algorithms="HS256")


@patch("jwt.decode")
def test_decode_jwt_token_returns_empty_dict_on_exception(
    jwt_decode_mock,
):
    token = "eyJhbGciOi..."
    jwt_secret = "mysecret!"
    expected_data = {}
    jwt_decode_mock.side_effect = Exception("error decoding!")

    decoded_token = decode_jwt_token(token, jwt_secret)

    assert decoded_token == expected_data
    jwt_decode_mock.assert_called_once_with(token, jwt_secret, algorithms="HS256")


def test_expired_invalid_jwt_http_response():
    http_res = expired_invalid_jwt_http_response()

    assert http_res == http_error_response(
        status_code=401,
        error_type="INVALID_JWT_TOKEN",
        error_detail="The token provided is not valid or has expired.",
    )
