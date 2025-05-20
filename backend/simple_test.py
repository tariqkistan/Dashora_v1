import os
import json
import boto3
from moto import mock_dynamodb, mock_secretsmanager
from unittest.mock import patch, MagicMock

# Set AWS environment variables
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["METRICS_TABLE_NAME"] = "dashora-metrics-test"
os.environ["MOCK_AWS_SERVICES"] = "true"

@mock_dynamodb
@mock_secretsmanager
def test_woocommerce():
    print("Setting up test environment...")
    
    # Create mock DynamoDB table
    print("Creating DynamoDB table...")
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName='dashora-metrics-test',
        KeySchema=[
            {'AttributeName': 'domain', 'KeyType': 'HASH'},
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'domain', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'N'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Create mock Secrets Manager secret
    print("Creating Secrets Manager secret...")
    secrets = boto3.client('secretsmanager', region_name='us-east-1')
    secrets.create_secret(
        Name='dashora/woocommerce/example-store.com',
        SecretString=json.dumps({
            'consumer_key': 'test_key',
            'consumer_secret': 'test_secret'
        })
    )
    
    # Import the module after setting up the environment
    print("Importing Lambda function...")
    from lambdas.woocommerce_fetcher import lambda_function
    
    # Create a test event
    event = {
        'domain': 'example-store.com',
        'days': 7
    }
    
    # Patch the WooCommerce API
    with patch('lambdas.woocommerce_fetcher.lambda_function.API') as mock_api:
        # Mock the WooCommerce API response
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        
        # Mock orders
        mock_orders_response = MagicMock()
        mock_orders_response.json.return_value = [
            {'id': 1, 'total': '100.00'},
            {'id': 2, 'total': '50.00'}
        ]
        
        # Mock products
        mock_products_response = MagicMock()
        mock_products_response.json.return_value = [
            {'id': 101, 'name': 'Product 1', 'price': '29.99', 'total_sales': 10},
            {'id': 102, 'name': 'Product 2', 'price': '19.99', 'total_sales': 5}
        ]
        
        # Set up to return different responses for different API calls
        def side_effect(endpoint, **kwargs):
            if endpoint == "orders":
                return mock_orders_response
            elif endpoint == "products":
                return mock_products_response
            return None
        
        mock_api_instance.get.side_effect = side_effect
        
        # Invoke the Lambda function
        print("Invoking Lambda function...")
        response = lambda_function.lambda_handler(event, {})
        
        # Print the response
        print("Lambda function response:")
        print(json.dumps(response, indent=2))
        
        # Additional validation
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            metrics = body['metrics']
            print("\nValidation:")
            print(f"- Total sales: ${metrics['total_sales']}")
            print(f"- Total orders: {metrics['total_orders']}")
            print(f"- Average order value: ${metrics['avg_order_value']}")
            print(f"- Top products count: {len(metrics['top_products'])}")
        
        return response

if __name__ == "__main__":
    print("Starting WooCommerce Lambda test...")
    try:
        test_woocommerce()
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}") 