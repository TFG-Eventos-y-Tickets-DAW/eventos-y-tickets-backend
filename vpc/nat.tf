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
