output "event_images_bucket_arn" {
  value = aws_s3_bucket.event_images_bucket.arn
}

output "event_images_bucket_name" {
  value = aws_s3_bucket.event_images_bucket.bucket
}
