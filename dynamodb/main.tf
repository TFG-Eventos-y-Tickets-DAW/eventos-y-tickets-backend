resource "aws_dynamodb_table" "event_pagination_dynamodb_table" {
  name           = "EventPagination"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
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
