# Dashora Analytics Dashboard Deployment Script

# Set variables
$STACK_NAME = "dashora-analytics"
$REGION = "us-east-1"  # Change to your desired region
$JWT_SECRET = "da5h0raAn4lyt1csS3cretK3y2024Pr0duct10n"  # Change this to a secure value

Write-Host "Starting deployment of Dashora Analytics Dashboard..."

# Install dependencies for Lambda functions
Write-Host "Installing dependencies for Lambda functions..."

# WooCommerce Fetcher
Write-Host "Installing WooCommerce Fetcher dependencies..."
cd lambda/woocommerce_fetcher
pip install -r requirements.txt -t .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing WooCommerce Fetcher dependencies"
    exit 1
}
cd ../..

# Google Analytics Fetcher
Write-Host "Installing Google Analytics Fetcher dependencies..."
cd lambda/ga_fetcher
pip install -r requirements.txt -t .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing Google Analytics Fetcher dependencies"
    exit 1
}
cd ../..

# Metrics Processor
Write-Host "Installing Metrics Processor dependencies..."
cd lambda/metrics_processor
pip install -r requirements.txt -t .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing Metrics Processor dependencies"
    exit 1
}
cd ../..

# API Handler
Write-Host "Installing API Handler dependencies..."
cd lambda/api_handler
pip install -r requirements.txt -t .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing API Handler dependencies"
    exit 1
}
cd ../..

# Package and deploy using SAM
Write-Host "Packaging and deploying the application..."
sam build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error during SAM build"
    exit 1
}

sam deploy --stack-name $STACK_NAME `
          --region $REGION `
          --capabilities CAPABILITY_IAM `
          --parameter-overrides JwtSecret=$JWT_SECRET `
          --no-confirm-changeset
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error during SAM deploy"
    exit 1
}

# Get API endpoint
$API_ENDPOINT = aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text

Write-Host "Deployment completed successfully!"
Write-Host "API Endpoint:"
Write-Host $API_ENDPOINT
Write-Host "Use this endpoint in your frontend application" 