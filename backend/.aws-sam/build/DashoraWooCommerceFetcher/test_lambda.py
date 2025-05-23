import json
import unittest
import os
from unittest.mock import patch, MagicMock
from moto import mock_dynamodb, mock_secretsmanager
import boto3

# Set AWS region for tests
os.environ["AWS_REGION"] = "us-east-1"
os.environ["MOCK_AWS_SERVICES"] = "true"

# Import module after setting environment variables
import lambda_function

class TestWooCommerceFetcher(unittest.TestCase):
    
    @mock_dynamodb
    @mock_secretsmanager
    @patch('lambda_function.API')
    def test_lambda_handler(self, mock_api):
        # Create mock DynamoDB and Secrets Manager resources
        dynamodb = boto3.resource('dynamodb')
        # Create test table
        dynamodb.create_table(
            TableName='dashora-metrics',
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
        
        # Create mock secret
        secrets_client = boto3.client('secretsmanager')
        secrets_client.create_secret(
            Name='dashora/woocommerce/example.com',
            SecretString=json.dumps({
                'consumer_key': 'test_key',
                'consumer_secret': 'test_secret'
            })
        )
        
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
        
        # Test event
        event = {
            'domain': 'example.com',
            'days': 7
        }
        
        # Call the handler
        response = lambda_function.lambda_handler(event, {})
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertEqual(body['domain'], 'example.com')
        
        metrics = body['metrics']
        self.assertEqual(metrics['total_sales'], 150.0)
        self.assertEqual(metrics['total_orders'], 2)
        self.assertEqual(metrics['avg_order_value'], 75.0)
        self.assertEqual(len(metrics['top_products']), 2)

if __name__ == '__main__':
    unittest.main() 