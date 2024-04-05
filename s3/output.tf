output "event_images_bucket_arn" {
  value = aws_s3_bucket.event_images_bucket.arn
}

output "event_images_bucket_name" {
  value = aws_s3_bucket.event_images_bucket.bucket
}

output "allow_full_access_to_react_bucket_policy_arn" {
  value = aws_iam_policy.allow_full_access_to_react_bucket_json_policy.arn
}
