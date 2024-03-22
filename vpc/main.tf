module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "eventos-y-tickets-vpc"
  cidr = "10.0.0.0/16"

  azs              = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  private_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  database_subnets = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

## NAT
module "fck-nat" {
  source = "github.com/RaJiska/terraform-aws-fck-nat?ref=main"

  name      = "my-fck-nat"
  vpc_id    = module.vpc.vpc_id
  subnet_id = module.vpc.public_subnets[0]

  instance_type = "t4g.small"

  update_route_table = true
  route_tables_ids = {
    "rtb-private-1" = module.vpc.private_route_table_ids[0]
    "rtb-private-2" = module.vpc.private_route_table_ids[1]
    "rtb-private-3" = module.vpc.private_route_table_ids[2]
  }

  # Disabled in prod (temp)
  count = var.environment == "prod" ? 0 : 1
}
