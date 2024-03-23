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
