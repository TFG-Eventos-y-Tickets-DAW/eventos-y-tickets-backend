module "lambda_req_mysql_jwt_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  create_layer        = true
  layer_name          = "python-req-mysql-jwt"
  description         = "Reusable Python Libraries, requests, mysql"
  compatible_runtimes = ["python3.12"]

  source_path = "lambdas_code/layers/shared"
}

module "lambda_common_code" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.3"

  create_layer        = true
  layer_name          = "python-common-logic-code"
  description         = "All common code, schema, http utils, rds conn, etc."
  compatible_runtimes = ["python3.12"]

  source_path = "lambdas_code/layers/common"
}
