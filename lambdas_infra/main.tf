module "sign_in_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "sign-in-lambda"
  description   = "Sign In Lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  source_path = "lambdas_code/signin"
}
