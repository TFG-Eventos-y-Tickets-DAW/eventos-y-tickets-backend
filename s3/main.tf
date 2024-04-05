resource "aws_s3_bucket" "event_images_bucket" {
  bucket = "eventos-y-tickets-event-images"
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership_event_images" {
  bucket = aws_s3_bucket.event_images_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.event_images_bucket.id

  rule {
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.event_images_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_access_from_everyone_policy" {
  bucket = aws_s3_bucket.event_images_bucket.id
  policy = data.aws_iam_policy_document.allow_access_from_everyone.json
}

resource "aws_s3_bucket_cors_configuration" "event_images_bucket_cors_conf" {
  bucket = aws_s3_bucket.event_images_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "GET"]
    allowed_origins = ["*"]
  }
}

data "aws_iam_policy_document" "allow_access_from_everyone" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.event_images_bucket.arn,
      "${aws_s3_bucket.event_images_bucket.arn}/*",
    ]
  }
}
