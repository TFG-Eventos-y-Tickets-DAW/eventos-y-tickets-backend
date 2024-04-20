resource "aws_sqs_queue" "send_payouts_fifo_queue" {
  name                        = "send-payouts-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.send_payouts_dlq_queue.arn
    maxReceiveCount     = 4
  })

  kms_master_key_id                 = "alias/aws/sqs"
  kms_data_key_reuse_period_seconds = 300
}

resource "aws_sqs_queue" "send_payouts_dlq_queue" {
  name                        = "send-payouts-dlq-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  kms_master_key_id                 = "alias/aws/sqs"
  kms_data_key_reuse_period_seconds = 300
}

resource "aws_sqs_queue_redrive_allow_policy" "send_payouts_queue_redrive_allow_policy" {
  queue_url = aws_sqs_queue.send_payouts_dlq_queue.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.send_payouts_fifo_queue.arn]
  })
}
