data "aws_acm_certificate" "eventngreet_cert" {
  domain   = "www.eventngreet.com"
  statuses = ["ISSUED"]
}
