resource "aws_lambda_event_source_mapping" "finalize_event_mapping_event_lifecycle_dynamodb_stream" {
  event_source_arn  = var.event_lifecycle_dynamodb_stream_arn
  function_name     = module.finalize_event_lambda.lambda_function_name
  starting_position = "LATEST"

  batch_size = 20
  enabled    = true

  maximum_retry_attempts             = 3
  maximum_batching_window_in_seconds = 1
  bisect_batch_on_function_error     = true

  filter_criteria {
    filter {
      pattern = jsonencode({
        "userIdentity" : {
          "type" : ["Service"],
          "principalId" : ["dynamodb.amazonaws.com"]
        }
      })
    }
  }
}

resource "aws_lambda_event_source_mapping" "send_payouts_event_mapping_sqs_queue" {
  event_source_arn = var.send_payouts_fifo_queue_arn
  function_name    = module.send_payouts_lambda.lambda_function_name

  enabled    = true
  batch_size = 10

  maximum_batching_window_in_seconds = 0
  function_response_types            = ["ReportBatchItemFailures"]
}
