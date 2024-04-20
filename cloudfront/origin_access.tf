resource "aws_cloudfront_origin_access_control" "cf_s3_origin_access_control" {
  name                              = "cf_s3_origin_access_control"
  description                       = "S3 CF policy"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
