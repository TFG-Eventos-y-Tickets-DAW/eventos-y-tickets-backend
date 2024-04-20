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
  policy = jsonencode(
    {
      "Version" : "2008-10-17",
      "Id" : "PolicyForCloudFrontPrivateContent",
      "Statement" : [
        {
          "Sid" : "AllowCloudFrontServicePrincipal",
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "cloudfront.amazonaws.com"
          },
          "Action" : "s3:GetObject",
          "Resource" : "arn:aws:s3:::event-n-greet-react-web/*",
          "Condition" : {
            "StringEquals" : {
              "AWS:SourceArn" : "arn:aws:cloudfront::058264200211:distribution/E1DEIFIEABRIU6"
            }
          }
        }
      ]
    }
  )
}

resource "aws_s3_bucket_website_configuration" "react_app_website_hosting_conf" {
  bucket = aws_s3_bucket.react_app_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

data "aws_iam_policy_document" "allow_full_access_to_react_bucket_json" {
  statement {
    actions = [
      "s3:*"
    ]

    resources = [
      aws_s3_bucket.react_app_bucket.arn,
      "${aws_s3_bucket.react_app_bucket.arn}/*",
    ]
  }

  statement {
    actions = [
      "cloudfront:CreateInvalidation"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "allow_full_access_to_react_bucket_json_policy" {
  name   = "allow_react_bucket_full_access"
  policy = data.aws_iam_policy_document.allow_full_access_to_react_bucket_json.json
}
