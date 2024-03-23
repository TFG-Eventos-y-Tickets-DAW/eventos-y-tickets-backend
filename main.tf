module "api_gateway" {
  source = "./api_gateway"

  sign_in_lambda_arn = module.lambdas.sign_in_lambda_arn
}

module "lambdas" {
  source = "./lambdas_infra"

  api_gateway_execution_arn = module.api_gateway.api_gateway_execution_arn
  vpc_private_subnets_ids   = module.vpc.vpc_private_subnets_ids
  lambda_sg_id              = module.vpc.lambda_sg_id
}

module "vpc" {
  source = "./vpc"

  environment = var.environment
}

module "rds" {
  source = "./rds"

  environment          = var.environment
  db_password          = var.db_password
  db_private_subnets   = module.vpc.vpc_private_db_subnets_ids
  db_subnet_group_name = module.vpc.vpc_private_db_subnet_group_name
  rds_sg_id            = module.vpc.rds_sg_id
}
