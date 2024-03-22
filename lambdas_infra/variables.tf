variable "api_gateway_execution_arn" {
  type = string
}

variable "lambda_sg_id" {
  type = string
}

variable "vpc_private_subnets_ids" {
  type = list(string)
}
