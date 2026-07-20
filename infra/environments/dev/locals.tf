locals {
  name_prefix          = "${var.project_name}-${var.environment}"
  function_name        = "${local.name_prefix}-api"
  lambda_zip_path      = abspath(var.lambda_artifact_path)
  lambda_log_group     = "/aws/lambda/${local.function_name}"
  api_access_log_group = "/aws/apigateway/${local.name_prefix}-http-api"

  alarm_names = {
    lambda_errors    = "${local.name_prefix}-lambda-errors"
    lambda_throttles = "${local.name_prefix}-lambda-throttles"
    lambda_duration  = "${local.name_prefix}-lambda-duration"
    api_5xx          = "${local.name_prefix}-api-5xx"
  }
}
