output "db_username" {
  value = "eventosytickets"
}

output "db_port" {
  value = module.aurora_db.cluster_port
}

output "db_aurora_endpoint" {
  value = module.aurora_db.cluster_endpoint
}

output "db_instance_resource_id" {
  value = module.aurora_db.cluster_resource_id
}
