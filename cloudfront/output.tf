output "react_web_cf_domain" {
  value = aws_cloudfront_distribution.react_web_s3_bucket.domain_name
}

output "react_web_cf_hosted_zone_id" {
  value = aws_cloudfront_distribution.react_web_s3_bucket.hosted_zone_id
}
