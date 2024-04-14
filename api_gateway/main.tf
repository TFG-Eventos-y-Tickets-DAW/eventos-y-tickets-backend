module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = "eventos_y_tickets_rest_api_v2"
  description   = "Eventos y Tickets REST API"
  protocol_type = "HTTP"

  create_api_domain_name = false
  create_vpc_link        = false

  cors_configuration = {
    allow_headers = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
    allow_methods = ["*"]
    allow_origins = ["*"] # TODO: only allow certain origins
  }

  # Routes and integrations
  integrations = {
    "POST /api/v1/user/signin" = {
      lambda_arn             = var.sign_in_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/user/signup" = {
      lambda_arn             = var.sign_up_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "GET /api/v1/user/me" = {
      lambda_arn             = var.about_me_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "GET /api/v1/event/get_presigned_url" = {
      lambda_arn             = var.generate_presigned_url_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "POST /api/v1/event/create" = {
      lambda_arn             = var.create_event_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "PUT /api/v1/event/{id}" = {
      lambda_arn             = var.update_event_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "GET /api/v1/event/{id}" = {
      lambda_arn             = var.get_event_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "GET /api/v1/event/public/{id}" = {
      lambda_arn             = var.get_public_event_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "DELETE /api/v1/event/{id}" = {
      lambda_arn             = var.delete_event_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "GET /api/v1/event/my_events" = {
      lambda_arn             = var.my_events_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "POST /api/v1/events" = {
      lambda_arn             = var.public_events_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/order/create" = {
      lambda_arn             = var.create_order_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/order/{id}/pay" = {
      lambda_arn             = var.pay_order_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "GET /api/v1/order/paypal/{id}" = {
      lambda_arn             = var.get_paypal_order_status_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/order/paypal/capture" = {
      lambda_arn             = var.capture_paypal_order_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/order/abandon" = {
      lambda_arn             = var.abandon_order_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/orders/list/{eventId}" = {
      lambda_arn             = var.list_orders_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }

    "POST /api/v1/order/{id}/refund" = {
      lambda_arn             = var.refund_order_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000

      authorization_type = "CUSTOM"
      authorizer_key     = "lambda-authorizer"
    }
  }

  authorizers = {
    "lambda-authorizer" = {
      authorizer_type                   = "REQUEST"
      authorizer_uri                    = var.authorizer_lambda_invoke_arn
      identity_sources                  = ["$request.header.Authorization"]
      authorizer_payload_format_version = "2.0"
      name                              = "lambda-authorizer"
      enable_simple_responses           = true
    }
  }
}
