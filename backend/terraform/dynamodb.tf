resource "aws_dynamodb_table" "metrics" {
  name           = "dashora-metrics"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "domain"
  range_key      = "timestamp"

  attribute {
    name = "domain"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "expiry_time"
    enabled        = true
  }

  tags = {
    Environment = "production"
    Project     = "dashora"
  }

  point_in_time_recovery {
    enabled = true
  }
}

# GSI for querying metrics by date range across all domains
resource "aws_dynamodb_table_global_secondary_index" "timestamp_index" {
  name               = "timestamp-index"
  hash_key          = "timestamp"
  projection_type    = "ALL"
  table_name        = aws_dynamodb_table.metrics.name
} 