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

  # Adding eventId GSI so we can query in a efficient way 
  # how many order sessions are for one event
  global_secondary_index {
    name               = "EventIdIndex"
    hash_key           = "eventId"
    write_capacity     = 5
    read_capacity      = 5
    projection_type    = "INCLUDE"
    non_key_attributes = ["ttl"]
  }
}

# Event Lifecycle Table
resource "aws_dynamodb_table" "event_lifecycle_dynamodb_table" {
  name           = "EventLifecycle"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  stream_enabled   = true
  stream_view_type = "KEYS_ONLY"
}


# Event Views Table
resource "aws_dynamodb_table" "event_views_dynamodb_table" {
  name           = "EventViews"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }
}
