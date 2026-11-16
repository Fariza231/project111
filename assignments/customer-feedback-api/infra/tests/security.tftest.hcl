mock_provider "aws" {}
variables {
  image_identifier        = "public.ecr.aws/example/customer-feedback-api:v1.0.0"
  read_api_key_secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:feedback-read-key-example"
}
run "secure_demo_configuration" {
  command = plan
  assert {
    condition     = aws_apprunner_service.feedback.source_configuration[0].auto_deployments_enabled == false
    error_message = "Deployment must be explicit rather than automatically following a mutable image tag."
  }
  assert {
    condition     = aws_apprunner_service.feedback.source_configuration[0].image_repository[0].image_configuration[0].runtime_environment_secrets["READ_API_KEY"] == var.read_api_key_secret_arn
    error_message = "Use a secret ARN reference, not a plaintext key in runtime variables."
  }
  assert {
    condition     = aws_apprunner_auto_scaling_configuration_version.single_instance.max_size == 1
    error_message = "In-memory storage cannot safely serve multiple independent replicas."
  }
  assert {
    condition     = aws_apprunner_service.feedback.health_check_configuration[0].path == "/health"
    error_message = "Health checks must not need access to customer feedback or a read key."
  }
  assert {
    condition     = jsondecode(aws_iam_role_policy.read_key.policy).Statement[0].Resource == var.read_api_key_secret_arn
    error_message = "The runtime role must be scoped to the specified secret."
  }
}
