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

output "authorizer_lambda_invoke_arn" {
  value = module.authorizer_lambda.lambda_function_invoke_arn
}
