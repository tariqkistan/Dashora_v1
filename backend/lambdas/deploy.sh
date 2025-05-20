#!/bin/bash

# Create a temporary directory for building
mkdir -p build

# Function to package and deploy a Lambda function
deploy_function() {
    func_name=$1
    handler_file=$2
    
    echo "Deploying $func_name..."
    
    # Create function directory in build
    mkdir -p "build/$func_name"
    
    # Copy function code
    cp "$func_name/$handler_file" "build/$func_name/"
    
    # Install dependencies
    pip install -r requirements.txt -t "build/$func_name/"
    
    # Create deployment package
    cd "build/$func_name"
    zip -r "../$func_name.zip" .
    cd ../..
    
    # Update Lambda function
    aws lambda update-function-code \
        --function-name "dashora-$func_name" \
        --zip-file "fileb://build/$func_name.zip"
}

# Deploy each function
deploy_function "woocommerce_fetcher" "main.py"
deploy_function "ga_fetcher" "main.py"
deploy_function "metrics_processor" "main.py"
deploy_function "api_handler" "main.py"

# Clean up
rm -rf build

echo "Deployment complete!" 