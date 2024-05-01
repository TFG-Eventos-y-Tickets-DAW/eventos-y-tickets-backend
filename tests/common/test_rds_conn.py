from unittest.mock import patch
from common.rds_conn import create_rds_connection
import os
import pymysql.cursors


@patch.object(
    os, "environ", {"DB_HOST": "localhost", "DB_PORT": "3306", "DB_USERNAME": "root"}
)
@patch("boto3.client")
@patch("pymysql.connect")
def test_creates_rds_connection_calls_pymysql_with_correct_parameters(
    pymysq_connect_mock,
    boto3_client_mock,
):
    boto3_client_mock.return_value.generate_db_auth_token.return_value = "secret!"
    ssl = {"ca": "/opt/python/us-east-1-bundle.pem"}

    create_rds_connection()

    pymysq_connect_mock.assert_called_once_with(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USERNAME"],
        password="secret!",
        database="eventosytickets",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        ssl=ssl,
    )
