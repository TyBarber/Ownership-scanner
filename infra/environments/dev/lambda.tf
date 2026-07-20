resource "aws_cloudwatch_log_group" "lambda" {
  name              = local.lambda_log_group
  retention_in_days = 14
}

resource "aws_lambda_function" "api" {
  function_name = local.function_name
  description   = "Ownership Scanner read-only development API"
  role          = aws_iam_role.lambda.arn
  handler       = "ownership_scanner.lambda_handler.handler"
  runtime       = "python3.12"
  architectures = ["x86_64"]

  filename         = local.lambda_zip_path
  source_code_hash = fileexists(local.lambda_zip_path) ? filebase64sha256(local.lambda_zip_path) : null

  memory_size                    = 256
  timeout                        = 10
  reserved_concurrent_executions = 5

  environment {
    variables = {
      OWNERSHIP_DATA_DIR = "/var/task/data"
    }
  }

  lifecycle {
    precondition {
      condition     = fileexists(local.lambda_zip_path)
      error_message = "Lambda artifact is missing. Run: python scripts/build_lambda_artifact.py"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy.lambda_logging,
  ]
}
