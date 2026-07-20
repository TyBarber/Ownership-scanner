output "api_endpoint" {
  description = "Base URL of the development HTTP API."
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "api_id" {
  description = "API Gateway HTTP API identifier."
  value       = aws_apigatewayv2_api.api.id
}

output "lambda_function_name" {
  description = "Lambda function name."
  value       = aws_lambda_function.api.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN."
  value       = aws_lambda_function.api.arn
}

output "lambda_log_group_name" {
  description = "CloudWatch log group for Lambda logs."
  value       = aws_cloudwatch_log_group.lambda.name
}

output "api_access_log_group_name" {
  description = "CloudWatch log group for API access logs."
  value       = aws_cloudwatch_log_group.api_access.name
}

output "alarm_names" {
  description = "CloudWatch alarm names."
  value       = values(local.alarm_names)
}

output "region" {
  description = "AWS Region for the development environment."
  value       = var.aws_region
}

output "environment" {
  description = "Deployment environment."
  value       = var.environment
}
