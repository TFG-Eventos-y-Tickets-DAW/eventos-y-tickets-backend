module "authorizer_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "authorizer-lambda"
  description   = "Authorizer Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/authorizer"

  publish = true

  allowed_triggers = {
    APIGateway = {
      service    = "apigateway"
      source_arn = "${var.api_gateway_execution_arn}/*/*/*"
    }
  }

  vpc_subnet_ids         = var.vpc_private_subnets_ids
  vpc_security_group_ids = [var.lambda_sg_id]
  attach_network_policy  = true

  layers = [
    module.lambda_req_mysql_jwt_layer.lambda_layer_arn,
    module.lambda_common_code.lambda_layer_arn
  ]

  timeout     = 12
  memory_size = 256
}
