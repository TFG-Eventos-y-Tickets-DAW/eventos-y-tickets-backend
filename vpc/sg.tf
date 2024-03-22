resource "aws_security_group" "lambdas_sg" {
  name        = "Lambdas Security Group"
  description = "Shared SG across lambdas"

  vpc_id = module.vpc.vpc_id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}
