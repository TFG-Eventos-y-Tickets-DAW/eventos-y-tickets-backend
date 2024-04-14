data "aws_iam_policy_document" "allow_rds_connection_json_policy" {
  statement {
    actions = [
      "rds-db:connect"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "allow_rds_connection_policy" {
  name        = "rds-allow-connection"
  description = "Allow RDS connection policy"
  policy      = data.aws_iam_policy_document.allow_rds_connection_json_policy.json
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_sign_in_lambda" {
  role       = module.sign_in_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_sign_up_lambda" {
  role       = module.sign_up_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_create_event_lambda" {
  role       = module.create_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_update_event_lambda" {
  role       = module.update_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_get_event_lambda" {
  role       = module.get_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_my_events_lambda" {
  role       = module.my_events_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_public_events_lambda" {
  role       = module.public_events_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_delete_event_lambda" {
  role       = module.delete_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_get_public_event_lambda" {
  role       = module.get_public_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_create_order_lambda" {
  role       = module.create_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_pay_order_lambda" {
  role       = module.pay_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_capture_paypal_order_lambda" {
  role       = module.capture_paypal_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_abandon_order_lambda" {
  role       = module.abandon_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_list_orders_lambda" {
  role       = module.list_orders_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_rds_attachment_refund_order_lambda" {
  role       = module.refund_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_rds_connection_policy.arn
}

data "aws_ssm_parameter" "jwt_secret_sign_parameter" {
  name = "/jwt/creds/secret"
}

data "aws_iam_policy_document" "allow_jwt_secret_parameter_store_json_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter"
    ]
    resources = [
      data.aws_ssm_parameter.jwt_secret_sign_parameter.arn
    ]
  }
}

resource "aws_iam_policy" "allow_jwt_secret_parameter_store_policy" {
  name        = "allow-jwt-secret-parameter"
  description = "Allow retrieval of JWT secret"
  policy      = data.aws_iam_policy_document.allow_jwt_secret_parameter_store_json_policy.json
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_sign_in_lambda" {
  role       = module.sign_in_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_about_me_lambda" {
  role       = module.about_me_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_authorizer_lambda" {
  role       = module.authorizer_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_create_event_lambda" {
  role       = module.create_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_my_events_lambda" {
  role       = module.my_events_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_update_event_lambda" {
  role       = module.update_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_delete_event_lambda" {
  role       = module.delete_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_create_order_lambda" {
  role       = module.create_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_list_orders_lambda" {
  role       = module.list_orders_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_jwt_secret_parameter_attachment_refund_order_lambda" {
  role       = module.refund_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_jwt_secret_parameter_store_policy.arn
}

data "aws_iam_policy_document" "allow_generate_presigned_s3_url_json_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject"
    ]
    resources = ["${var.event_images_bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "allow_generate_presigned_s3_policy" {
  name        = "allow-s3-presigned-policy"
  description = "Allow generating post presigned url"
  policy      = data.aws_iam_policy_document.allow_generate_presigned_s3_url_json_policy.json
}

resource "aws_iam_role_policy_attachment" "allow_generate_presigned_s3_attachment_generate_presigned_lambda" {
  role       = module.generate_presigned_url_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_generate_presigned_s3_policy.arn
}


data "aws_iam_policy_document" "allow_event_pagitation_dynamodb_access_json_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]
    resources = [var.event_pagination_dynamodb_table_arn]
  }
}

resource "aws_iam_policy" "allow_event_pagitation_dynamodb_access_policy" {
  name        = "allow-event-pagination-dynamodb-table"
  description = "Allow access to Event Pagination DynamoDB Table"
  policy      = data.aws_iam_policy_document.allow_event_pagitation_dynamodb_access_json_policy.json
}

resource "aws_iam_role_policy_attachment" "allow_event_pagitation_dynamodb_access_policy_attachment_public_events_lambda" {
  role       = module.public_events_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_event_pagitation_dynamodb_access_policy.arn
}

data "aws_iam_policy_document" "allow_order_sessions_dynamodb_access_json_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
    ]
    resources = [
      var.order_sessions_dynamodb_table_arn,
      "${var.order_sessions_dynamodb_table_arn}/index/*" # Including indexes
    ]
  }
}

resource "aws_iam_policy" "allow_order_sessions_dynamodb_access_policy" {
  name        = "allow-order-sessions-dynamodb-table"
  description = "Allow access to Order Sessions DynamoDB Table"
  policy      = data.aws_iam_policy_document.allow_order_sessions_dynamodb_access_json_policy.json
}

resource "aws_iam_role_policy_attachment" "allow_order_sessions_dynamodb_access_policy_attachment_create_order_lambda" {
  role       = module.create_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_order_sessions_dynamodb_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_order_sessions_dynamodb_access_policy_attachment_pay_order_lambda" {
  role       = module.pay_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_order_sessions_dynamodb_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_order_sessions_dynamodb_access_policy_attachment_get_public_event_lambda" {
  role       = module.get_public_event_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_order_sessions_dynamodb_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_order_sessions_dynamodb_access_policy_attachment_capture_paypal_order_lambda" {
  role       = module.capture_paypal_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_order_sessions_dynamodb_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_order_sessions_dynamodb_access_policy_attachment_abandon_order_lambda" {
  role       = module.abandon_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_order_sessions_dynamodb_access_policy.arn
}

data "aws_ssm_parameter" "paypal_api_user" {
  name = "/paypal/api/username"
}

data "aws_ssm_parameter" "paypal_api_password" {
  name = "/paypal/api/password"
}

data "aws_iam_policy_document" "allow_paypal_secrets_parameter_store_json_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter"
    ]
    resources = [
      data.aws_ssm_parameter.paypal_api_user.arn,
      data.aws_ssm_parameter.paypal_api_password.arn
    ]
  }
}

resource "aws_iam_policy" "allow_paypal_secrets_parameter_store_policy" {
  name        = "allow_paypal_secrets_parameter_store_policy"
  description = "Allow PayPal Secrets SSM"
  policy      = data.aws_iam_policy_document.allow_paypal_secrets_parameter_store_json_policy.json
}

resource "aws_iam_role_policy_attachment" "allow_paypal_secrets_parameter_attachment_pay_order_lambda" {
  role       = module.pay_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_paypal_secrets_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_paypal_secrets_parameter_attachment_get_paypal_order_lambda" {
  role       = module.get_paypal_order_status_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_paypal_secrets_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_paypal_secrets_parameter_attachment_capture_paypal_order_lambda" {
  role       = module.capture_paypal_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_paypal_secrets_parameter_store_policy.arn
}

resource "aws_iam_role_policy_attachment" "allow_paypal_secrets_parameter_attachment_refund_order_lambda" {
  role       = module.refund_order_lambda.lambda_role_name
  policy_arn = aws_iam_policy.allow_paypal_secrets_parameter_store_policy.arn
}
