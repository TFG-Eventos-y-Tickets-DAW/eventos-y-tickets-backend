output "send_payouts_fifo_queue_arn" {
  value = aws_sqs_queue.send_payouts_fifo_queue.arn
}

output "send_payouts_fifo_queue_name" {
  value = aws_sqs_queue.send_payouts_fifo_queue.name
}
