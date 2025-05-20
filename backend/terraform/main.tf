provider "aws" {
  region = var.aws_region
}

# Lambda execution role
resource "aws_iam_role" "lambda_role" {
  name = "dashora-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

# DynamoDB access policy
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "dashora-dynamodb-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.metrics.arn,
          "${aws_dynamodb_table.metrics.arn}/index/*"
        ]
      }
    ]
  })
}

# Secrets Manager access policy
resource "aws_iam_role_policy" "secrets_access" {
  name = "dashora-secrets-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/dashora/*"
        ]
      }
    ]
  })
}

# SQS queue for metrics processing
resource "aws_sqs_queue" "metrics_queue" {
  name                      = "dashora-metrics-queue"
  delay_seconds             = 0
  max_message_size         = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 0
  visibility_timeout_seconds = 30
}

# SQS access policy
resource "aws_iam_role_policy" "sqs_access" {
  name = "dashora-sqs-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [aws_sqs_queue.metrics_queue.arn]
      }
    ]
  })
}

# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "dashora-alerts"
}

# SNS access policy
resource "aws_iam_role_policy" "sns_access" {
  name = "dashora-sns-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [aws_sns_topic.alerts.arn]
      }
    ]
  })
}

# Lambda functions
resource "aws_lambda_function" "woocommerce_fetcher" {
  filename         = "../../build/woocommerce_fetcher.zip"
  function_name    = "dashora-woocommerce-fetcher"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      METRICS_QUEUE_URL = aws_sqs_queue.metrics_queue.url
      ALERT_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }
}

resource "aws_lambda_function" "ga_fetcher" {
  filename         = "../../build/ga_fetcher.zip"
  function_name    = "dashora-ga-fetcher"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      METRICS_QUEUE_URL = aws_sqs_queue.metrics_queue.url
      ALERT_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }
}

resource "aws_lambda_function" "metrics_processor" {
  filename         = "../../build/metrics_processor.zip"
  function_name    = "dashora-metrics-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      DYNAMODB_TABLE   = aws_dynamodb_table.metrics.name
      ALERT_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }
}

resource "aws_lambda_function" "api_handler" {
  filename         = "../../build/api_handler.zip"
  function_name    = "dashora-api-handler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.metrics.name
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "dashora-api"
}

resource "aws_api_gateway_resource" "metrics" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "metrics"
}

resource "aws_api_gateway_method" "get_metrics" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.metrics.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = aws_api_gateway_method.get_metrics.http_method
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.api_handler.invoke_arn
  integration_http_method = "POST"
}

# CloudWatch Event rules for fetchers
resource "aws_cloudwatch_event_rule" "fetchers" {
  name                = "dashora-metrics-fetchers"
  description         = "Trigger metrics fetchers every 5 minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "woocommerce_fetcher" {
  rule      = aws_cloudwatch_event_rule.fetchers.name
  target_id = "WooCommerceFetcher"
  arn       = aws_lambda_function.woocommerce_fetcher.arn
}

resource "aws_cloudwatch_event_target" "ga_fetcher" {
  rule      = aws_cloudwatch_event_rule.fetchers.name
  target_id = "GAFetcher"
  arn       = aws_lambda_function.ga_fetcher.arn
}

# Lambda permissions for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch_woocommerce" {
  statement_id  = "AllowCloudWatchInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.woocommerce_fetcher.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.fetchers.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_ga" {
  statement_id  = "AllowCloudWatchInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ga_fetcher.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.fetchers.arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# Output values
output "api_endpoint" {
  value = "${aws_api_gateway_rest_api.api.execution_arn}/prod/metrics"
}

output "metrics_queue_url" {
  value = aws_sqs_queue.metrics_queue.url
}

output "alert_topic_arn" {
  value = aws_sns_topic.alerts.arn
} 