output "sign_in_lambda_arn" {
  value = module.sign_in_lambda.lambda_function_arn
}

output "sign_up_lambda_arn" {
  value = module.sign_up_lambda.lambda_function_arn
}

output "about_me_lambda_arn" {
  value = module.about_me_lambda.lambda_function_arn
}

output "generate_presigned_url_lambda_arn" {
  value = module.generate_presigned_url_lambda.lambda_function_arn
}

output "create_event_lambda_arn" {
  value = module.create_event_lambda.lambda_function_arn
}

output "update_event_lambda_arn" {
  value = module.update_event_lambda.lambda_function_arn
}

output "delete_event_lambda_arn" {
  value = module.delete_event_lambda.lambda_function_arn
}

output "get_event_lambda_arn" {
  value = module.get_event_lambda.lambda_function_arn
}

output "get_public_event_lambda_arn" {
  value = module.get_public_event_lambda.lambda_function_arn
}

output "create_order_lambda_arn" {
  value = module.create_order_lambda.lambda_function_arn
}

output "pay_order_lambda_arn" {
  value = module.pay_order_lambda.lambda_function_arn
}

output "get_paypal_order_status_lambda_arn" {
  value = module.get_paypal_order_status_lambda.lambda_function_arn
}

output "capture_paypal_order_lambda_arn" {
  value = module.capture_paypal_order_lambda.lambda_function_arn
}

output "my_events_lambda_arn" {
  value = module.my_events_lambda.lambda_function_arn
}

output "public_events_lambda_arn" {
  value = module.public_events_lambda.lambda_function_arn
}

output "authorizer_lambda_invoke_arn" {
  value = module.authorizer_lambda.lambda_function_invoke_arn
}
