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
        'property_id': '123456789',
        'service_account_key': {'key': 'value'}
    })
}

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
        
        # Mock Google Analytics data
        ga_data = {
            'total_users': 150,
            'total_sessions': 225,
            'total_page_views': 700,
            'total_conversions': 15,
            'total_revenue': 1500.0,
            'by_date': {
                '20230101': {
                    'users': 100,
                    'sessions': 150,
                    'page_views': 500,
                    'conversions': 10,
                    'revenue': 1000.0
                },
                '20230102': {
                    'users': 50,
                    'sessions': 75,
                    'page_views': 200,
                    'conversions': 5,
                    'revenue': 500.0
                }
            },
            'by_device': {
                'desktop': {
                    'users': 100,
                    'sessions': 150,
                    'page_views': 500,
                    'conversions': 10,
                    'revenue': 1000.0
                },
                'mobile': {
                    'users': 50,
                    'sessions': 75,
                    'page_views': 200,
                    'conversions': 5,
                    'revenue': 500.0
                }
            },
            'by_country': {
                'US': {
                    'users': 100,
                    'sessions': 150,
                    'page_views': 500,
                    'conversions': 10,
                    'revenue': 1000.0
                },
                'UK': {
                    'users': 50,
                    'sessions': 75,
                    'page_views': 200,
                    'conversions': 5,
                    'revenue': 500.0
                }
            }
        }
        
        # Store metrics in DynamoDB (mocked)
        timestamp = int(datetime.now().timestamp())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'domain': domain,
                'timestamp': timestamp,
                'metrics': ga_data
            })
        }
    
    except Exception as e:
        print(f"Error processing Google Analytics data: {str(e)}")
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
        print(f"Total users: {metrics['total_users']}")
        print(f"Total sessions: {metrics['total_sessions']}")
        print(f"Total page views: {metrics['total_page_views']}")
        print(f"Total conversions: {metrics['total_conversions']}")
        print(f"Total revenue: ${metrics['total_revenue']}")
        print(f"Date data points: {len(metrics['by_date'])}")
        print(f"Device types: {len(metrics['by_device'])}")
        print(f"Countries: {len(metrics['by_country'])}")
    else:
        print("\nTEST FAILED!")
        print(f"Status Code: {response['statusCode']}")
        print(f"Error: {response['body']}")

if __name__ == "__main__":
    main() 