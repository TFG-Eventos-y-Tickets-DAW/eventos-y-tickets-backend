output "vpc_private_subnets_ids" {
  value = module.vpc.private_subnets
}

output "vpc_private_db_subnets_ids" {
  value = module.vpc.database_subnets
}

output "lambda_sg_id" {
  value = aws_security_group.lambdas_sg.id
}
