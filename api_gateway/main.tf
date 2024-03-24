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
    "GET /" = {
      lambda_arn             = var.sign_in_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "POST /api/v1/user/signup" = {
      lambda_arn             = var.sign_up_lambda_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    # "GET /some-route-with-authorizer" = {
    #   integration_type = "HTTP_PROXY"
    #   integration_uri  = "some url"
    #   authorizer_key   = "azure"
    # }
  }

  #   authorizers = {
  #     "azure" = {
  #       authorizer_type  = "JWT"
  #       identity_sources = "$request.header.Authorization"
  #       name             = "azure-auth"
  #       audience         = ["d6a38afd-45d6-4874-d1aa-3c5c558aqcc2"]
  #       issuer           = "https://sts.windows.net/aaee026e-8f37-410e-8869-72d9154873e4/"
  #     }
  #   }
}
