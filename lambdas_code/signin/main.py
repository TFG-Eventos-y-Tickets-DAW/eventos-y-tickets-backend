import requests
import os
import boto3

rds_client = boto3.client("rds")
auth_token = rds_client.generate_db_auth_token(
    os.environ["DB_HOST"], int(os.environ["DB_PORT"]), os.environ["DB_USERNAME"]
)

print("Auth Token: ", auth_token)


def lambda_handler(event, context):
    print("Received event: ", event)
    res = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    return res.json()
