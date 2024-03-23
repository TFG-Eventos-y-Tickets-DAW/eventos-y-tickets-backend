output "db_endpoint" {
  value = var.environment == "prod" ? "" : module.db[0].db_instance_endpoint
}

output "db_username" {
  value = var.environment == "prod" ? "" : module.db[0].db_instance_username
}

output "db_instance_resource_id" {
  value = var.environment == "prod" ? "" : module.db[0].db_instance_resource_id
}

output "db_port" {
  value = var.environment == "prod" ? "" : module.db[0].db_instance_port
}
