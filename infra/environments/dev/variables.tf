variable "aws_region" {
  description = "AWS Region for the development environment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project identifier used for names and tags."
  type        = string
  default     = "ownership-scanner"
}

variable "environment" {
  description = "Deployment environment identifier."
  type        = string
  default     = "dev"

  validation {
    condition     = var.environment == "dev"
    error_message = "This configuration is restricted to the dev environment."
  }
}

variable "lambda_artifact_path" {
  description = "Path to the verified Lambda ZIP, relative to this Terraform root or absolute."
  type        = string
  default     = "../../../dist/ownership-scanner-lambda.zip"
}

variable "enable_budget" {
  description = "Whether to create a monthly AWS cost budget."
  type        = bool
  default     = false
}

variable "budget_limit_usd" {
  description = "Monthly development budget limit in USD."
  type        = number
  default     = 5

  validation {
    condition     = var.budget_limit_usd > 0
    error_message = "budget_limit_usd must be greater than zero."
  }
}

variable "budget_notification_email" {
  description = "Email address for budget notifications when enable_budget is true."
  type        = string
  default     = ""
  sensitive   = true
}
