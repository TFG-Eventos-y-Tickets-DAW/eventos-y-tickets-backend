## Lambda Security Group Config
resource "aws_security_group" "lambdas_sg" {
  name        = "Lambdas Security Group"
  description = "Shared SG across lambdas"

  vpc_id = module.vpc.vpc_id
}

resource "aws_vpc_security_group_egress_rule" "lambda_sg_egress_rule_ipv4" {
  security_group_id = aws_security_group.lambdas_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "lambda_sg_egress_rule_ipv6" {
  security_group_id = aws_security_group.lambdas_sg.id
  ip_protocol       = "-1"
  cidr_ipv6         = "::/0"
}

## RDS Security Group Config
resource "aws_security_group" "rds_sg" {
  name        = "RDS MySQL Security Group"
  description = "Database SG"

  vpc_id = module.vpc.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "rds_sg_ingress_rule" {
  security_group_id            = aws_security_group.rds_sg.id
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.lambdas_sg.id
}

resource "aws_vpc_security_group_egress_rule" "rds_sg_egress_rule_ipv4" {
  security_group_id = aws_security_group.rds_sg.id
  from_port         = 3306
  to_port           = 3306
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "rds_sg_egress_rule_ipv6" {
  security_group_id = aws_security_group.rds_sg.id
  from_port         = 3306
  to_port           = 3306
  ip_protocol       = "tcp"
  cidr_ipv6         = "::/0"
}
