import boto3
import os

from uuid import uuid4
from common.http_utils import generic_server_error

s3_client = boto3.client("s3")
S3_BUCKET = os.environ["MEDIA_BUCKET_NAME"]


def lambda_handler(event, _):
    extension = event.get("queryStringParameters", {}).get("extension", "png")

    try:
        return s3_client.generate_presigned_post(
            S3_BUCKET,
            f"{str(uuid4())}.{extension}",
            Fields={"Content-Type": f"image/{extension}"},
            Conditions=[["starts-with", "$Content-Type", "image/"]],
            ExpiresIn=3600,
        )
    except:
        return generic_server_error()
