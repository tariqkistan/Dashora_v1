# AWS Deployment Guide for Dashora Backend

This guide walks through deploying the serverless backend for Dashora Analytics using AWS SAM.

## Prerequisites

1. AWS CLI installed and configured with appropriate credentials
2. AWS SAM CLI installed
3. Python 3.9 or later
4. Docker (for local testing)

## Deployment Steps

### 1. Build and Package Lambda Functions

```bash
# Navigate to the backend directory
cd backend

# Activate virtual environment (if not already activated)
source venv/Scripts/Activate  # On Windows
# or
source venv/bin/activate  # On Unix/macOS

# Install dependencies
pip install -r lambdas/requirements.txt

# Build the SAM application
sam build
```

### 2. Deploy to AWS

```bash
# Deploy with guided deployment (first time)
sam deploy --guided

# For subsequent deployments
sam deploy
```

During the guided deployment, you'll need to:
- Specify a stack name (e.g., `dashora-backend`)
- Choose an AWS region (e.g., `us-east-1`)
- Provide a JWT secret for authentication
- Confirm deployment changes

### 3. Get API Gateway Endpoint

After deployment completes, SAM will output the API Gateway endpoint URL:

```
------------------------------------------------------
Outputs
------------------------------------------------------
Key                 ApiEndpoint
Description         API Gateway endpoint URL
Value               https://abcdefghij.execute-api.region.amazonaws.com/prod/
```

### 4. Update Vercel Environment Variables

Copy the API Gateway endpoint URL from the deployment output and add it to your Vercel environment variables:

1. Go to the Vercel Dashboard
2. Select your Dashora project
3. Go to Settings > Environment Variables
4. Add the variable `NEXT_PUBLIC_API_URL` with the value from the deployment output

## Lambda Functions

The backend consists of the following Lambda functions:

1. **WooCommerce Fetcher** - Fetches data from WooCommerce stores
2. **Google Analytics Fetcher** - Fetches data from Google Analytics
3. **Metrics Processor** - Processes and stores metrics data
4. **API Handler** - Serves API requests

Each function has its own directory in the `lambdas/` folder.

## Database Tables

The backend uses these DynamoDB tables:

1. **Metrics Table** - Stores processed metrics data
2. **Domains Table** - Stores domain configurations
3. **Users Table** - Stores user information

## Testing Endpoints

After deployment, you can test the API endpoints:

```bash
# Test authentication
curl -X POST https://your-api-endpoint/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Test metrics (with auth token)
curl https://your-api-endpoint/metrics/example.com \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Troubleshooting

If you encounter issues:

1. Check CloudWatch Logs for Lambda function errors
2. Verify that IAM permissions are configured correctly
3. Check that environment variables are set properly
4. Run `sam logs -n FunctionName` to see recent logs 