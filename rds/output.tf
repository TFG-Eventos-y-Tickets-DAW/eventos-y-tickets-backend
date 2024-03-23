output "db_endpoint" {
  value = var.environment == "prod" ? "" : module.db[0].db_instance_endpoint
}
