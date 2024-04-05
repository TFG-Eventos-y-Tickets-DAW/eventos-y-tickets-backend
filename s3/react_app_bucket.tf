resource "aws_s3_bucket" "react_app_bucket" {
  bucket = "event-n-greet-react-web"
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership_react_app" {
  bucket = aws_s3_bucket.react_app_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "react_bucket_encrypt" {
  bucket = aws_s3_bucket.react_app_bucket.id

  rule {
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "react_bucket_public_access" {
  bucket = aws_s3_bucket.react_app_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_access_from_everyone_policy_react_app" {
  bucket = aws_s3_bucket.react_app_bucket.id
  policy = data.aws_iam_policy_document.allow_access_from_everyone_react_app.json
}


data "aws_iam_policy_document" "allow_access_from_everyone_react_app" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.react_app_bucket.arn,
      "${aws_s3_bucket.react_app_bucket.arn}/*",
    ]
  }
}
