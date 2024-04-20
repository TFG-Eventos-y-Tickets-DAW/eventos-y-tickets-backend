data "aws_route53_zone" "eventngreet_route_53_hosted_zone" {
  name = "eventngreet.com."
}

resource "aws_route53_record" "react_app_cf_origin_record" {
  zone_id = data.aws_route53_zone.eventngreet_route_53_hosted_zone.zone_id
  name    = "eventngreet.com"
  type    = "A"

  alias {
    name                   = var.react_web_cf_domain
    zone_id                = var.react_web_cf_hosted_zone_id
    evaluate_target_health = true
  }
}
