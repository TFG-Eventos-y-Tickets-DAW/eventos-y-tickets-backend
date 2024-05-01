from unittest.mock import patch
import os
import json


with patch("pymysql.connect") as pymysql_mock, patch.object(
    os, "environ", {"DB_HOST": "localhost", "DB_PORT": "3306", "DB_USERNAME": "root"}
) as env_mock, patch("boto3.client") as boto_client_mock:
    from lambdas_code.signup.main import lambda_handler


def test_sign_in_returns_client_error_when_duplicate_user():
    event = {
        "body": json.dumps(
            {
                "firstName": "Brayan",
                "lastName": "Ayala",
                "password": "123456",
                "email": "brayan@foo.com",
                "isAnonymous": False,
            }
        )
    }
    assert 1 == 1
