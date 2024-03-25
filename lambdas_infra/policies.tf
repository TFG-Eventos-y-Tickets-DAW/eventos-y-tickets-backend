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
