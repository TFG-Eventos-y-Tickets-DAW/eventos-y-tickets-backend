output "api_gateway_execution_arn" {
  value = module.api_gateway.apigatewayv2_api_execution_arn
}

output "api_gateway_endpoint" {
  value = module.api_gateway.apigatewayv2_api_api_endpoint
}
