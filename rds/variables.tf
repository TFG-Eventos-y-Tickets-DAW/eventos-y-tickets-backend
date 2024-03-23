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
