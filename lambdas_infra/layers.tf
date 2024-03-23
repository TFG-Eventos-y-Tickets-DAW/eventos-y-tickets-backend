module "lambda_req_mysql_jwt_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer        = true
  layer_name          = "python-req-mysql-jwt"
  description         = "Reusable Python Libraries, requests, mysql"
  compatible_runtimes = ["python3.12"]

  source_path = "lambdas_code/layers/shared"
}
