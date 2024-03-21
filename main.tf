module "api_gateway" {
  source = "./api_gateway"

  sign_in_lambda_arn = module.lambdas.sign_in_lambda_arn
}

module "lambdas" {
  source = "./lambdas_infra"

  api_gateway_execution_arn = module.api_gateway.api_gateway_execution_arn
}
