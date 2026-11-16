variable "aws_region" {
  description = "Deployment region. No AWS resources are created during validation or mock tests."
  type        = string
  default     = "us-east-1"
}
variable "service_name" {
  type    = string
  default = "customer-feedback-api-demo"
  validation {
    condition     = can(regex("^[A-Za-z][A-Za-z0-9_-]{3,39}$", var.service_name))
    error_message = "Use a 4-40 character service name starting with a letter."
  }
}
variable "image_identifier" {
  description = "Existing public ECR image URI with a versioned tag (publish the built image separately)."
  type        = string
  validation {
    condition     = can(regex("^public\\.ecr\\.aws/[^ ]+:[^ ]+$", var.image_identifier)) && !endswith(var.image_identifier, ":latest")
    error_message = "Provide a public ECR image with an immutable version tag, not :latest."
  }
}
variable "read_api_key_secret_arn" {
  description = "Existing Secrets Manager secret ARN containing only a random read key of at least 24 characters; never pass the secret value to Terraform."
  type        = string
  validation {
    condition     = can(regex("^arn:aws[a-z-]*:secretsmanager:[a-z0-9-]+:[0-9]{12}:secret:.+$", var.read_api_key_secret_arn))
    error_message = "Provide an existing Secrets Manager secret ARN."
  }
}
