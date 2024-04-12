module "aurora_db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name                        = "eventosytickets-mysqlv2"
  engine                      = "aurora-mysql"
  database_name               = "eventosytickets"
  engine_mode                 = "provisioned"
  engine_version              = "8.0"
  storage_encrypted           = true
  master_username             = "root"
  master_password             = var.db_password
  manage_master_user_password = false

  vpc_id               = var.vpc_id
  db_subnet_group_name = var.db_subnet_group_name
  security_group_rules = {
    vpc_ingress = {
      cidr_blocks = var.private_subnets_cidr_blocks
    }
    lambdas_ingress = {
      source_security_group_id = var.lambdas_sg_group_id
    }
    bastion_host_access = {
      source_security_group_id = "sg-0581ab2b0dc5e4f32"
    }
  }

  monitoring_interval = 60
  apply_immediately   = true
  skip_final_snapshot = true

  serverlessv2_scaling_configuration = {
    min_capacity = 0.5 # Minimum ACUs - 1GB
    max_capacity = 2   # up to 4GB
  }

  instance_class = "db.serverless"
  instances = {
    one = {}
  }

  iam_database_authentication_enabled = true
}
