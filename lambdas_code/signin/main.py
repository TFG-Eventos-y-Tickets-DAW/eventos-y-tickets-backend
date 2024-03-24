import requests
import os
import boto3
import pymysql.cursors


rds_client = boto3.client("rds")
auth_token = rds_client.generate_db_auth_token(
    os.environ["DB_HOST"], int(os.environ["DB_PORT"]), os.environ["DB_USERNAME"]
)
ssl = {"ca": "/opt/python/us-east-1-bundle.pem"}
connection = pymysql.connect(
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USERNAME"],
    password=auth_token,
    database="eventosytickets",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    ssl=ssl,
)


def lambda_handler(event, context):
    print("Received event: ", event)
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM `users` WHERE `email`=%s"
        cursor.execute(sql, ("foo@bar.com",))
        result = cursor.fetchone()
        print(result)

    res = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    return res.json()
