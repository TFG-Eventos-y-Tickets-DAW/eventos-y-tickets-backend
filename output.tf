output "api_gateway_endpoint" {
  value = module.api_gateway.api_gateway_endpoint
}

output "aurora_mysql_db_endpoint" {
  value = module.rds.db_aurora_endpoint
}
