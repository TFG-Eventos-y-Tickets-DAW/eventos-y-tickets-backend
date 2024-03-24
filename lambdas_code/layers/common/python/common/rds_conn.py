import os
import boto3
import pymysql.cursors


def create_rds_connection():
    # this client will only be created once on lambda startup
    rds_client = boto3.client("rds")
    auth_token = rds_client.generate_db_auth_token(
        os.environ["DB_HOST"], int(os.environ["DB_PORT"]), os.environ["DB_USERNAME"]
    )
    ssl = {"ca": "/opt/python/us-east-1-bundle.pem"}
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USERNAME"],
        password=auth_token,
        database="eventosytickets",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        ssl=ssl,
    )
