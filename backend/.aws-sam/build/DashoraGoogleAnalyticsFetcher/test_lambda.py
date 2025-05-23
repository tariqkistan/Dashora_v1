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

class TestGoogleAnalyticsFetcher(unittest.TestCase):
    
    @mock_dynamodb
    @mock_secretsmanager
    @patch('lambda_function.BetaAnalyticsDataClient')
    @patch('lambda_function.service_account.Credentials')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_lambda_handler(self, mock_json_dump, mock_open, mock_credentials, mock_client):
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
            Name='dashora/google-analytics/example.com',
            SecretString=json.dumps({
                'property_id': '123456789',
                'service_account_key': {'key': 'value'}
            })
        )
        
        # Mock the Google Analytics API response
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create mock response
        mock_response = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.dimension_values = [
            MagicMock(value='20230101'),
            MagicMock(value='desktop'),
            MagicMock(value='US')
        ]
        mock_row1.metric_values = [
            MagicMock(value='100'),  # users
            MagicMock(value='150'),  # sessions
            MagicMock(value='500'),  # page views
            MagicMock(value='10'),   # conversions
            MagicMock(value='1000')  # revenue
        ]
        
        mock_row2 = MagicMock()
        mock_row2.dimension_values = [
            MagicMock(value='20230102'),
            MagicMock(value='mobile'),
            MagicMock(value='UK')
        ]
        mock_row2.metric_values = [
            MagicMock(value='50'),   # users
            MagicMock(value='75'),   # sessions
            MagicMock(value='200'),  # page views
            MagicMock(value='5'),    # conversions
            MagicMock(value='500')   # revenue
        ]
        
        mock_response.rows = [mock_row1, mock_row2]
        mock_client_instance.run_report.return_value = mock_response
        
        # Test event
        event = {
            'domain': 'example.com',
            'days': 7
        }
        
        # Mock file operations
        mock_open.return_value.__enter__.return_value = MagicMock()
        
        # Call the handler
        response = lambda_function.lambda_handler(event, {})
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertEqual(body['domain'], 'example.com')
        
        metrics = body['metrics']
        self.assertEqual(metrics['total_users'], 150)
        self.assertEqual(metrics['total_sessions'], 225)
        self.assertEqual(metrics['total_page_views'], 700)
        self.assertEqual(metrics['total_conversions'], 15)
        self.assertEqual(metrics['total_revenue'], 1500.0)
        
        # Check that we have data by date, device, and country
        self.assertEqual(len(metrics['by_date']), 2)
        self.assertEqual(len(metrics['by_device']), 2)
        self.assertEqual(len(metrics['by_country']), 2)

if __name__ == '__main__':
    unittest.main() 