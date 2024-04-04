output "event_pagination_dynamodb_table_arn" {
  value = aws_dynamodb_table.event_pagination_dynamodb_table.arn
}

output "event_pagination_dynamodb_table_name" {
  value = aws_dynamodb_table.event_pagination_dynamodb_table.name
}
