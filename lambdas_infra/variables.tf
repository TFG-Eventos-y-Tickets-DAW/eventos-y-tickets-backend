variable "api_gateway_execution_arn" {
  type = string
}

variable "lambda_sg_id" {
  type = string
}

variable "vpc_private_subnets_ids" {
  type = list(string)
}

variable "db_host" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_port" {
  type = string
}

variable "db_instance_resource_id" {
  type = string
}
