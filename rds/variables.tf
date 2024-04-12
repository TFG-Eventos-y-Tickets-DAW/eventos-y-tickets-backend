variable "environment" {
  type = string
}

variable "db_password" {
  type = string
}

variable "rds_sg_id" {
  type = string
}

variable "db_private_subnets" {
  type = list(string)
}

variable "db_subnet_group_name" {
  type = string
}

variable "private_subnets_cidr_blocks" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "lambdas_sg_group_id" {
  type = string
}
