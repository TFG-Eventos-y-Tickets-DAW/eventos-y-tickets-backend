output "vpc_private_subnets_ids" {
  value = module.vpc.private_subnets
}

output "vpc_private_db_subnets_ids" {
  value = module.vpc.database_subnets
}

output "lambda_sg_id" {
  value = aws_security_group.lambdas_sg.id
}

output "rds_sg_id" {
  value = aws_security_group.rds_sg.id
}

output "vpc_private_db_subnet_group_name" {
  value = module.vpc.database_subnet_group_name
}

output "private_subnets_cidr_blocks" {
  value = module.vpc.private_subnets_cidr_blocks
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
