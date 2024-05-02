import boto3
import os

from uuid import uuid4
from common.http_utils import generic_server_error

s3_client = boto3.client("s3")
S3_BUCKET = os.environ["MEDIA_BUCKET_NAME"]


def lambda_handler(event, _):
    extension = event.get("queryStringParameters", {}).get("extension", "png")

    try:
        image_id = str(uuid4())
        presigned_url_post_details = s3_client.generate_presigned_post(
            S3_BUCKET,
            f"images/{image_id}.{extension}",
            Fields={"Content-Type": f"image/{extension}"},
            Conditions=[["starts-with", "$Content-Type", "image/"]],
            ExpiresIn=3600,
        )
        potential_event_image_src = (
            f"https://eventngreet.com/images/{image_id}.{extension}"
        )
        return {
            "presignedPostData": presigned_url_post_details,
            "potentialEventImgSrc": potential_event_image_src,
        }
    except:
        return generic_server_error()
