
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
  memory_size = 2048
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
  memory_size = 2048
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
  memory_size = 328
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
    DB_HOST                    = split(":", var.db_host)[0]
    DB_PORT                    = var.db_port
    DB_USERNAME                = "${var.db_username}-lambda"
    EVENT_LIFECYCLE_TABLE_NAME = var.event_lifecycle_dynamodb_table_name
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
    DB_HOST                    = split(":", var.db_host)[0]
    DB_PORT                    = var.db_port
    DB_USERNAME                = "${var.db_username}-lambda"
    EVENT_LIFECYCLE_TABLE_NAME = var.event_lifecycle_dynamodb_table_name
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
  memory_size = 512
}

module "delete_event_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "delete-event-lambda"
  description   = "Delete Event Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/delete_event"

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
    DB_HOST                    = split(":", var.db_host)[0]
    DB_PORT                    = var.db_port
    DB_USERNAME                = "${var.db_username}-lambda"
    EVENT_LIFECYCLE_TABLE_NAME = var.event_lifecycle_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "get_public_event_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "get-public-event-lambda"
  description   = "Get Public Event details Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/get_public_event"

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
    DB_HOST                   = split(":", var.db_host)[0]
    DB_PORT                   = var.db_port
    DB_USERNAME               = "${var.db_username}-lambda"
    ORDER_SESSIONS_TABLE_NAME = var.order_sessions_dynamodb_table_name
    EVENT_VIEWS_TABLE_NAME    = var.event_views_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "create_order_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "create-order-lambda"
  description   = "Create Order Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/create_order"

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
    DB_HOST                   = split(":", var.db_host)[0]
    DB_PORT                   = var.db_port
    DB_USERNAME               = "${var.db_username}-lambda"
    ORDER_SESSIONS_TABLE_NAME = var.order_sessions_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "pay_order_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "pay-order-lambda"
  description   = "Pay Order Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/pay_order"

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
    DB_HOST                   = split(":", var.db_host)[0]
    DB_PORT                   = var.db_port
    DB_USERNAME               = "${var.db_username}-lambda"
    ORDER_SESSIONS_TABLE_NAME = var.order_sessions_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "get_paypal_order_status_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "get-paypal-order-status-lambda"
  description   = "Get PayPal Order Status"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/get_paypal_order_status"

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
  memory_size = 512
}

module "capture_paypal_order_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "capture-paypal-order-lambda"
  description   = "Capture PayPal Order"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/capture_paypal_order"

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
    DB_HOST                   = split(":", var.db_host)[0]
    DB_PORT                   = var.db_port
    DB_USERNAME               = "${var.db_username}-lambda"
    ORDER_SESSIONS_TABLE_NAME = var.order_sessions_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "abandon_order_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "abandon-order-lambda"
  description   = "Abandon Order"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/abandon_order"

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
    DB_HOST                   = split(":", var.db_host)[0]
    DB_PORT                   = var.db_port
    DB_USERNAME               = "${var.db_username}-lambda"
    ORDER_SESSIONS_TABLE_NAME = var.order_sessions_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "list_orders_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "list-orders-lambda"
  description   = "List Orders from Event"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/list_orders"

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
    DB_HOST                = split(":", var.db_host)[0]
    DB_PORT                = var.db_port
    DB_USERNAME            = "${var.db_username}-lambda"
    EVENT_VIEWS_TABLE_NAME = var.event_views_dynamodb_table_name
  }

  timeout     = 12
  memory_size = 256
}

module "refund_order_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "refund-order-lambda"
  description   = "Refund Order"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/refund_order"

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

module "my_tickets_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "my-tickets-lambda"
  description   = "My Tickets"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/my_tickets"

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

module "finalize_event_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "finalize-event-lambda"
  description   = "Finalize Event"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/finalize_event"

  publish = true

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

module "prepare_payouts_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "prepare-payouts-lambda"
  description   = "Prepare Event Payouts"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/prepare_payouts"

  publish = true

  vpc_subnet_ids         = var.vpc_private_subnets_ids
  vpc_security_group_ids = [var.lambda_sg_id]
  attach_network_policy  = true

  layers = [
    module.lambda_req_mysql_jwt_layer.lambda_layer_arn,
    module.lambda_common_code.lambda_layer_arn
  ]

  environment_variables = {
    DB_HOST            = split(":", var.db_host)[0]
    DB_PORT            = var.db_port
    DB_USERNAME        = "${var.db_username}-lambda"
    PAYOUTS_QUEUE_NAME = var.send_payouts_fifo_queue_name
  }

  timeout     = 300
  memory_size = 512
}

module "send_payouts_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  function_name = "send-payouts-lambda"
  description   = "Send Event Payouts"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/send_payouts"

  publish = true

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

  timeout     = 30
  memory_size = 512
}
