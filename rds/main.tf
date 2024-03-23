module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "eventosyticketsdb"

  engine            = "mysql"
  engine_version    = "8.0.35"
  instance_class    = "db.t4g.micro"
  allocated_storage = 20 # 20 GB

  db_name                     = "eventosytickets"
  username                    = "eventosytickets"
  password                    = var.db_password
  port                        = "3306"
  multi_az                    = false
  manage_master_user_password = false

  iam_database_authentication_enabled = true
  vpc_security_group_ids              = [var.rds_sg_id]

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  # DB subnet group
  db_subnet_group_name   = var.db_subnet_group_name
  create_db_subnet_group = false

  # Database Deletion Protection
  deletion_protection = true

  # Paremeter Group
  family = "mysql8.0"

  parameters = [
    {
      name  = "character_set_client"
      value = "utf8mb4"
    },
    {
      name  = "character_set_server"
      value = "utf8mb4"
    }
  ]

  # Option Group
  major_engine_version = "8.0"

  options = [
    {
      option_name = "MARIADB_AUDIT_PLUGIN"

      option_settings = [
        {
          name  = "SERVER_AUDIT_EVENTS"
          value = "CONNECT"
        },
        {
          name  = "SERVER_AUDIT_FILE_ROTATIONS"
          value = "37"
        },
      ]
    },
  ]

  # Disabled in prod (temp)
  count = var.environment == "prod" ? 0 : 1
}
