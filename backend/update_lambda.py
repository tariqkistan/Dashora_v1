import boto3
import sys
import os

def update_lambda_function(function_name, zip_path):
    """Update Lambda function code with a ZIP file"""
    
    print(f"Updating Lambda function: {function_name}")
    print(f"Using ZIP file: {zip_path}")
    
    # Check if ZIP file exists
    if not os.path.exists(zip_path):
        print(f"Error: ZIP file not found at {zip_path}")
        return False
    
    try:
        # Read the ZIP file contents
        with open(zip_path, 'rb') as file_data:
            zip_bytes = file_data.read()
        
        # Create Lambda client
        lambda_client = boto3.client('lambda')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes,
            Publish=True
        )
        
        print(f"Lambda function updated successfully. Version: {response.get('Version')}")
        print(f"Function ARN: {response.get('FunctionArn')}")
        return True
        
    except Exception as e:
        print(f"Error updating Lambda function: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_lambda.py <function_name> [zip_path]")
        print("Example: python update_lambda.py dashora-api-woocommerce-fetcher lambda_deployment.zip")
        sys.exit(1)
    
    function_name = sys.argv[1]
    zip_path = sys.argv[2] if len(sys.argv) > 2 else "lambda_deployment.zip"
    
    update_lambda_function(function_name, zip_path) 