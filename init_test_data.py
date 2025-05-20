import boto3
import time
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
domains_table = dynamodb.Table('dashora-domains-v2')
users_table = dynamodb.Table('dashora-users-v2')
metrics_table = dynamodb.Table('dashora-metrics-v2')

def init_test_data():
    try:
        # Create test domain
        domains_table.put_item(
            Item={
                'domain': 'example.com',
                'name': 'Example Store',
                'created_at': int(time.time()),
                'woocommerce_config': {
                    'api_url': 'https://example.com/wp-json/wc/v3',
                    'consumer_key': 'test_key',
                    'consumer_secret': 'test_secret'
                },
                'ga_config': {
                    'view_id': '123456789',
                    'property_id': 'UA-123456789-1'
                }
            }
        )
        print("Test domain created successfully")
        
        # Associate domain with test user (overwrite existing domains)
        users_table.put_item(
            Item={
                'user_id': 'test-user',
                'created_at': int(time.time()),
                'domains': ['example.com']
            }
        )
        print("Domain associated with test user")
        
        # Add some test metrics
        current_time = datetime.now()
        for i in range(7):
            metric_time = current_time - timedelta(days=i)
            timestamp = int(metric_time.timestamp())
            metrics_table.put_item(
                Item={
                    'domain': 'example.com',
                    'timestamp': Decimal(str(timestamp)),
                    'pageviews': Decimal(str(100 + i * 10)),
                    'visitors': Decimal(str(50 + i * 5)),
                    'orders': Decimal(str(5 + i)),
                    'revenue': Decimal(str(100.0 + i * 25.0))
                }
            )
        print("Test metrics added")
        
        # Verify the domain was created
        response = domains_table.get_item(
            Key={
                'domain': 'example.com'
            }
        )
        print("\nVerifying domain data:")
        print("-" * 50)
        print(response.get('Item'))
        
        # Verify user data
        response = users_table.get_item(
            Key={
                'user_id': 'test-user'
            }
        )
        print("\nVerifying user data:")
        print("-" * 50)
        print(response.get('Item'))
        
        # Verify metrics data
        response = metrics_table.query(
            KeyConditionExpression='#d = :domain',
            ExpressionAttributeNames={
                '#d': 'domain'
            },
            ExpressionAttributeValues={
                ':domain': 'example.com'
            }
        )
        print("\nVerifying metrics data:")
        print("-" * 50)
        print(response.get('Items'))
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    init_test_data() 