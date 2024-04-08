# Pagination Table
resource "aws_dynamodb_table" "event_pagination_dynamodb_table" {
  name           = "EventPagination"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "tokenId"

  attribute {
    name = "tokenId"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

# Order/Checkout Sessions Table
resource "aws_dynamodb_table" "order_sessions_dynamodb_table" {
  name           = "OrderSessions"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "orderId"
  range_key      = "eventId"

  attribute {
    name = "orderId"
    type = "S"
  }

  attribute {
    name = "eventId"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}
