output "service_url" {
  description = "AWS-managed HTTPS endpoint; no endpoint exists until an authorized apply succeeds."
  value       = "https://${aws_apprunner_service.feedback.service_url}"
}
