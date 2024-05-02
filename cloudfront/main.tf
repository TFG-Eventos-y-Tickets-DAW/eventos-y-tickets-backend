resource "aws_cloudfront_distribution" "react_web_s3_bucket" {
  origin {
    domain_name              = var.react_app_s3_domain_name
    origin_id                = local.react_s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.cf_s3_origin_access_control.id
  }

  origin {
    domain_name              = var.event_images_s3_domain_name
    origin_id                = local.event_images_s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.cf_s3_origin_access_control.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "React App CF distribution"
  default_root_object = "index.html"

  default_cache_behavior {
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400

    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.react_s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
  }

  ordered_cache_behavior {
    path_pattern     = "/images/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.event_images_s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  viewer_certificate {
    acm_certificate_arn = data.aws_acm_certificate.eventngreet_cert.arn
    ssl_support_method  = "sni-only"
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "ES", "HN"]
    }
  }

  custom_error_response {
    error_code            = 404
    response_page_path    = "/index.html"
    error_caching_min_ttl = 300
    response_code         = 200
  }
  custom_error_response {
    error_code            = 403
    response_page_path    = "/index.html"
    error_caching_min_ttl = 300
    response_code         = 200
  }

  aliases = [
    "eventngreet.com",
    "www.eventngreet.com",
  ]
}
