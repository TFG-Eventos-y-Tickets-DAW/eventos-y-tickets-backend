output "event_images_bucket_arn" {
  value = aws_s3_bucket.event_images_bucket.arn
}

output "event_images_bucket_name" {
  value = aws_s3_bucket.event_images_bucket.bucket
}

output "allow_full_access_to_react_bucket_policy_arn" {
  value = aws_iam_policy.allow_full_access_to_react_bucket_json_policy.arn
}

output "react_app_s3_domain_name" {
  value = aws_s3_bucket.react_app_bucket.bucket_domain_name
}

output "react_app_s3_website_domain_name" {
  value = aws_s3_bucket.react_app_bucket.website_domain
}
