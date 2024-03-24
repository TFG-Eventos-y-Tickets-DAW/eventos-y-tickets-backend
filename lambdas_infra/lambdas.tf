module "sign_in_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "sign-in-lambda"
  description   = "Sign In Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/signin"

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

  environment_variables = {
    DB_HOST     = split(":", var.db_host)[0]
    DB_PORT     = var.db_port
    DB_USERNAME = "${var.db_username}-lambda"
  }

  timeout     = 12
  memory_size = 256
}

module "sign_up_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "sign-up-lambda"
  description   = "Sign Up Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/signup"

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

  environment_variables = {
    DB_HOST     = split(":", var.db_host)[0]
    DB_PORT     = var.db_port
    DB_USERNAME = "${var.db_username}-lambda"
  }

  timeout     = 12
  memory_size = 256
}

module "about_me_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "about-me-lambda"
  description   = "About me Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/aboutme"

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
