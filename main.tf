module "api_gateway" {
  source = "./api_gateway"

  sign_in_lambda_arn                = module.lambdas.sign_in_lambda_arn
  sign_up_lambda_arn                = module.lambdas.sign_up_lambda_arn
  about_me_lambda_arn               = module.lambdas.about_me_lambda_arn
  generate_presigned_url_lambda_arn = module.lambdas.generate_presigned_url_lambda_arn
  create_event_lambda_arn           = module.lambdas.create_event_lambda_arn
  update_event_lambda_arn           = module.lambdas.update_event_lambda_arn
  delete_event_lambda_arn           = module.lambdas.delete_event_lambda_arn
  get_event_lambda_arn              = module.lambdas.get_event_lambda_arn
  get_public_event_lambda_arn       = module.lambdas.get_public_event_lambda_arn
  create_order_lambda_arn           = module.lambdas.create_order_lambda_arn
  pay_order_lambda_arn              = module.lambdas.pay_order_lambda_arn
  my_events_lambda_arn              = module.lambdas.my_events_lambda_arn
  public_events_lambda_arn          = module.lambdas.public_events_lambda_arn
  authorizer_lambda_invoke_arn      = module.lambdas.authorizer_lambda_invoke_arn
}

module "lambdas" {
  source = "./lambdas_infra"

  api_gateway_execution_arn           = module.api_gateway.api_gateway_execution_arn
  vpc_private_subnets_ids             = module.vpc.vpc_private_subnets_ids
  lambda_sg_id                        = module.vpc.lambda_sg_id
  db_host                             = module.rds.db_endpoint
  db_username                         = module.rds.db_username
  db_port                             = module.rds.db_port
  db_instance_resource_id             = module.rds.db_instance_resource_id
  eventos_y_tickets_media_bucket_arn  = module.s3.event_images_bucket_arn
  eventos_y_tickets_media_bucket_name = module.s3.event_images_bucket_name

  event_images_bucket_arn              = module.s3.event_images_bucket_arn
  event_pagination_dynamodb_table_arn  = module.dynamodb.event_pagination_dynamodb_table_arn
  event_pagination_dynamodb_table_name = module.dynamodb.event_pagination_dynamodb_table_name
  order_sessions_dynamodb_table_arn    = module.dynamodb.order_sessions_dynamodb_table_arn
  order_sessions_dynamodb_table_name   = module.dynamodb.order_sessions_dynamodb_table_name
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

module "s3" {
  source = "./s3"
}

module "dynamodb" {
  source = "./dynamodb"
}

module "oidc_github" {
  source  = "unfunco/oidc-github/aws"
  version = "1.7.1"

  github_repositories = [
    "TFG-Eventos-y-Tickets-DAW/eventos-y-tickets-frontend"
  ]

  iam_role_name        = "github_oidc"
  iam_role_policy_arns = [module.s3.allow_full_access_to_react_bucket_policy_arn]
}
