output "event_pagination_dynamodb_table_arn" {
  value = aws_dynamodb_table.event_pagination_dynamodb_table.arn
}

output "event_pagination_dynamodb_table_name" {
  value = aws_dynamodb_table.event_pagination_dynamodb_table.name
}

output "order_sessions_dynamodb_table_arn" {
  value = aws_dynamodb_table.order_sessions_dynamodb_table.arn
}

output "order_sessions_dynamodb_table_name" {
  value = aws_dynamodb_table.order_sessions_dynamodb_table.name
}

output "event_lifecycle_dynamodb_table_arn" {
  value = aws_dynamodb_table.event_lifecycle_dynamodb_table.arn
}

output "event_lifecycle_dynamodb_table_name" {
  value = aws_dynamodb_table.event_lifecycle_dynamodb_table.name
}

output "event_lifecycle_dynamodb_stream_arn" {
  value = aws_dynamodb_table.event_lifecycle_dynamodb_table.stream_arn
}

output "event_views_dynamodb_table_arn" {
  value = aws_dynamodb_table.event_views_dynamodb_table.arn
}

output "event_views_dynamodb_table_name" {
  value = aws_dynamodb_table.event_views_dynamodb_table.name
}
