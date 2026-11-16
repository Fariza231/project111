resource "aws_iam_role" "runtime" {
  name = "${var.service_name}-runtime"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "tasks.apprunner.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy" "read_key" {
  name = "read-one-feedback-key"
  role = aws_iam_role.runtime.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = var.read_api_key_secret_arn
    }]
  })
}
resource "aws_apprunner_auto_scaling_configuration_version" "single_instance" {
  auto_scaling_configuration_name = "${var.service_name}-single-instance"
  min_size                        = 1
  max_size                        = 1
  max_concurrency                 = 20
}
resource "aws_apprunner_service" "feedback" {
  service_name                   = var.service_name
  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.single_instance.arn
  source_configuration {
    auto_deployments_enabled = false
    image_repository {
      image_identifier      = var.image_identifier
      image_repository_type = "ECR_PUBLIC"
      image_configuration {
        port = "8080"
        runtime_environment_variables = {
          NODE_ENV = "production"
          PORT     = "8080"
        }
        runtime_environment_secrets = {
          READ_API_KEY = var.read_api_key_secret_arn
        }
      }
    }
  }
  instance_configuration {
    cpu               = "256"
    memory            = "512"
    instance_role_arn = aws_iam_role.runtime.arn
  }
  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 3
  }
  depends_on = [aws_iam_role_policy.read_key]
}
