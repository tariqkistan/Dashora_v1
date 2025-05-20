# Dashora Backend

This directory contains the AWS Lambda functions for the Dashora multi-site analytics dashboard.

## Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- AWS SAM CLI (optional, for local testing)

## Setup Instructions

### 1. Install Python

Download and install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### 2. Set up the Python environment

Run the setup script:

```powershell
# Navigate to the backend directory
cd backend

# Run the setup script
.\setup.ps1
```

Or manually:

```powershell
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure AWS credentials

```powershell
aws configure
```

Enter your AWS Access Key ID, Secret Access Key, default region (e.g., us-east-1), and output format (json).

## Project Structure

- `lambdas/woocommerce/` - Lambda function for fetching WooCommerce data
- `lambdas/google_analytics/` - Lambda function for fetching Google Analytics data
- `lambdas/processor/` - Lambda function for processing and storing data
- `lambdas/api_handler/` - Lambda function for serving data via API Gateway

## Local Testing

```powershell
# Activate the virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1

# Run tests
pytest
```

## Deployment

Instructions for deploying the Lambda functions to AWS will be provided in the Terraform configuration files. 