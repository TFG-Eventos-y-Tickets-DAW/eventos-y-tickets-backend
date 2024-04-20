data "aws_acm_certificate" "eventngreet_cert" {
  domain   = "eventngreet.com"
  statuses = ["ISSUED"]
}
