
#
# Authentication Lambdas
#

module "sign_in_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

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
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

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
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

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

#
# Event lambdas
#

module "generate_presigned_url_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "generate-presigned-url-lambda"
  description   = "Generate S3 Presigned URL Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/generate_presigned_url"

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
    module.lambda_common_code.lambda_layer_arn
  ]

  environment_variables = {
    "MEDIA_BUCKET_NAME" = var.eventos_y_tickets_media_bucket_name
  }

  timeout     = 12
  memory_size = 256
}

module "create_event_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "create-event-lambda"
  description   = "Create Event Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/create_event"

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

module "update_event_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "update-event-lambda"
  description   = "Update Event Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/update_event"

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

module "get_event_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "get-event-lambda"
  description   = "Get Event Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/get_event"

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

module "my_events_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "my_events-lambda"
  description   = "My Events Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/my_events"

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

module "public_events_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "public-events-lambda"
  description   = "Public Events List Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/public_events"

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
    DB_HOST                     = split(":", var.db_host)[0]
    DB_PORT                     = var.db_port
    DB_USERNAME                 = "${var.db_username}-lambda"
    EVENT_PAGINATION_TABLE_NAME = var.event_pagination_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}
