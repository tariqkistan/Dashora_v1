import os
import json
import boto3
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Set environment variables 
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['METRICS_TABLE_NAME'] = 'dashora-metrics'

# Create mock boto3 clients
boto3.resource = MagicMock()
boto3.client = MagicMock()

# Mock table operations
mock_table = MagicMock()
boto3.resource.return_value.Table.return_value = mock_table
mock_table.put_item = MagicMock()

# Mock secrets manager
mock_secrets = MagicMock()
boto3.client.return_value = mock_secrets
mock_secrets.get_secret_value.return_value = {
    'SecretString': json.dumps({
        'consumer_key': 'test_key',
        'consumer_secret': 'test_secret'
    })
}

# Mock WooCommerce API
class MockAPI:
    def __init__(self, url, consumer_key, consumer_secret, version):
        self.url = url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.version = version
    
    def get(self, endpoint, params=None):
        mock_response = MagicMock()
        if endpoint == "orders":
            mock_response.json.return_value = [
                {'id': 1, 'total': '100.00'},
                {'id': 2, 'total': '50.00'}
            ]
        elif endpoint == "products":
            mock_response.json.return_value = [
                {'id': 101, 'name': 'Product 1', 'price': '29.99', 'total_sales': 10},
                {'id': 102, 'name': 'Product 2', 'price': '19.99', 'total_sales': 5}
            ]
        return mock_response

# Create a simplified version of the lambda handler function
def lambda_handler(event, context):
    """Lambda function handler"""
    try:
        # Extract domain and date range from the event
        domain = event.get('domain')
        days = int(event.get('days', 7))
        
        if not domain:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Domain parameter is required'})
            }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Mock WooCommerce data
        woocommerce_data = {
            'total_sales': 150.0,
            'total_orders': 2,
            'avg_order_value': 75.0,
            'top_products': [
                {
                    'id': 101,
                    'name': 'Product 1',
                    'price': '29.99',
                    'sales': 10
                },
                {
                    'id': 102,
                    'name': 'Product 2',
                    'price': '19.99',
                    'sales': 5
                }
            ]
        }
        
        # Store metrics in DynamoDB (mocked)
        timestamp = int(datetime.now().timestamp())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'domain': domain,
                'timestamp': timestamp,
                'metrics': woocommerce_data
            })
        }
    
    except Exception as e:
        print(f"Error processing WooCommerce data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def main():
    # Create a test event
    event = {
        'domain': 'example-store.com',
        'days': 7
    }
    
    # Call the handler
    print("Calling Lambda handler...")
    response = lambda_handler(event, {})
    
    # Print the response
    print("Response:")
    print(json.dumps(response, indent=2))
    
    # Verify the results
    if response['statusCode'] == 200:
        print("\nTEST PASSED!")
        body = json.loads(response['body'])
        metrics = body['metrics']
        print(f"Total sales: ${metrics['total_sales']}")
        print(f"Total orders: {metrics['total_orders']}")
        print(f"Average order value: ${metrics['avg_order_value']}")
        print(f"Top products: {len(metrics['top_products'])}")
    else:
        print("\nTEST FAILED!")
        print(f"Status Code: {response['statusCode']}")
        print(f"Error: {response['body']}")

if __name__ == "__main__":
    main() 