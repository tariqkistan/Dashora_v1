import os
import sys
import json
import importlib.util
import argparse
from datetime import datetime

def import_lambda_function(path):
    """Import a Lambda function module from a file path"""
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def invoke_lambda(lambda_path, event_path=None, env_vars=None):
    """Invoke a Lambda function locally"""
    # Set environment variables
    if env_vars:
        for key, value in env_vars.items():
            os.environ[key] = value
    
    # Import the Lambda function
    lambda_module = import_lambda_function(lambda_path)
    
    # Load the event data
    if event_path and os.path.exists(event_path):
        with open(event_path, 'r') as f:
            event = json.load(f)
    else:
        # Default event
        event = {
            'domain': 'example.com',
            'days': 7
        }
    
    # Create a dummy context
    class DummyContext:
        def __init__(self):
            self.function_name = "local-test"
            self.function_version = "$LATEST"
            self.invoked_function_arn = "arn:aws:lambda:local:123456789012:function:local-test"
            self.memory_limit_in_mb = 128
            self.aws_request_id = "12345678-1234-1234-1234-123456789012"
            self.log_group_name = "/aws/lambda/local-test"
            self.log_stream_name = datetime.now().strftime("%Y/%m/%d/[$LATEST]%H%M%S")
            self.identity = None
            self.client_context = None
            self.remaining_time_in_millis = 300000
    
    context = DummyContext()
    
    # Invoke the Lambda function
    print(f"Invoking Lambda function with event: {json.dumps(event, indent=2)}")
    print("---")
    
    result = lambda_module.lambda_handler(event, context)
    
    print("---")
    print("Lambda function result:")
    print(json.dumps(result, indent=2))
    
    return result

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run AWS Lambda functions locally")
    parser.add_argument("lambda_name", help="Name of the Lambda function to run (woocommerce, ga, processor, or api)")
    parser.add_argument("--event", help="Path to the event JSON file")
    parser.add_argument("--env", help="Path to the environment variables JSON file")
    
    args = parser.parse_args()
    
    # Map Lambda names to their file paths
    lambda_paths = {
        "woocommerce": os.path.join("lambdas", "woocommerce_fetcher", "lambda_function.py"),
        "ga": os.path.join("lambdas", "ga_fetcher", "lambda_function.py"),
        "processor": os.path.join("lambdas", "metrics_processor", "lambda_function.py"),
        "api": os.path.join("lambdas", "api_handler", "lambda_function.py")
    }
    
    if args.lambda_name not in lambda_paths:
        print(f"Unknown Lambda function: {args.lambda_name}")
        print(f"Available functions: {', '.join(lambda_paths.keys())}")
        sys.exit(1)
    
    lambda_path = lambda_paths[args.lambda_name]
    
    # Load environment variables
    env_vars = None
    if args.env and os.path.exists(args.env):
        with open(args.env, 'r') as f:
            env_vars = json.load(f)
    
    # Set default environment variables for testing
    if not env_vars:
        env_vars = {
            "METRICS_TABLE_NAME": "dashora-metrics-local",
            "DOMAINS_TABLE_NAME": "dashora-domains-local",
            "USERS_TABLE_NAME": "dashora-users-local",
            "AWS_REGION": "us-east-1",
            "MOCK_AWS_SERVICES": "true"
        }
    
    # Invoke the Lambda function
    try:
        invoke_lambda(lambda_path, args.event, env_vars)
    except Exception as e:
        print(f"Error invoking Lambda: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 