resource "aws_vpc_endpoint" "s3_gateway_endpoint" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.us-east-1.s3"

  vpc_endpoint_type = "Gateway"
  route_table_ids   = module.vpc.private_route_table_ids
}

resource "aws_vpc_endpoint" "dynamodb_gateway_endpoint" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.us-east-1.dynamodb"

  vpc_endpoint_type = "Gateway"
  route_table_ids   = module.vpc.private_route_table_ids
}
