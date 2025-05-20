import os
import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# Set environment variables 
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['METRICS_TABLE_NAME'] = 'dashora-metrics-v2'
os.environ['DOMAINS_TABLE_NAME'] = 'dashora-domains-v2'
os.environ['USERS_TABLE_NAME'] = 'dashora-users-v2'
os.environ['JWT_SECRET'] = 'da5h0raAn4lyt1csS3cretK3y2024Pr0duct10n'

# Mock functions for testing
def mock_verify_token(token):
    """Mock JWT verification that always returns test-user"""
    if token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzQ3NzUxMTA5LCJpYXQiOjE3NDc2NjQ3MDksInN1YiI6InRlc3QtdXNlciJ9.5hL4f07L0R65CYaAW2rQtvsCfQ6MWgqrBQzXhav3mQw":
        return "test-user"
    return None

def mock_get_user_domains(user_id):
    """Mock function to return domains for test user"""
    if user_id == "test-user":
        return ["example.com"]
    return []

def mock_get_latest_metrics(domain, days=7):
    """Mock function to return test metrics data"""
    if domain == "example.com":
        current_time = datetime.now()
        metrics = []
        for i in range(days):
            metric_time = current_time - timedelta(days=i)
            metrics.append({
                'domain': domain,
                'timestamp': int(metric_time.timestamp()),
                'pageviews': 100 + i * 10,
                'visitors': 50 + i * 5,
                'orders': 5 + i,
                'revenue': 100.0 + i * 25.0
            })
        return metrics
    return []

def lambda_handler(event, context):
    """Mock Lambda handler for testing"""
    try:
        print("Event:", json.dumps(event))  # Debug log
        
        # Get the HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        days = int(query_params.get('days', '7'))  # Default to 7 days
        
        # Get authorization header
        headers = event.get('headers', {}) or {}
        auth_header = headers.get('Authorization', '')
        
        # Extract token if it exists
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        # Verify token and get user ID
        user_id = mock_verify_token(token) if token else None
        print(f"User ID: {user_id}")  # Debug log
        
        # Handle unauthenticated requests
        if not user_id:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Get user's domains
        user_domains = mock_get_user_domains(user_id)
        print(f"User domains: {user_domains}")  # Debug log
        
        # Handle GET requests
        if http_method == 'GET':
            # Root path - return basic info
            if path == '/':
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'message': 'Dashora Analytics API',
                        'version': '1.0.0',
                        'user_id': user_id
                    })
                }
            
            # List domains
            elif path == '/domains':
                domains_data = []
                for domain_name in user_domains:
                    domains_data.append({
                        'domain': domain_name,
                        'name': 'Example Store',
                        'woocommerce_enabled': True,
                        'ga_enabled': True
                    })
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'domains': domains_data})
                }
            
            # Get metrics for a specific domain
            elif path.startswith('/metrics/'):
                # Extract domain from path
                domain = path.split('/metrics/')[-1]  # More reliable extraction
                print(f"Requested domain: {domain}")  # Debug log
                print(f"User domains: {user_domains}")  # Debug log
                print(f"Domain in user_domains: {domain in user_domains}")  # Debug log
                
                # Check if user has access to this domain
                if domain not in user_domains:
                    print(f"Access denied: {domain} not in {user_domains}")  # Debug log
                    return {
                        'statusCode': 403,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Access denied to this domain'})
                    }
                
                # Get metrics for the domain
                metrics_data = mock_get_latest_metrics(domain, days)
                print(f"Metrics data: {json.dumps(metrics_data, default=str)}")  # Debug log
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'domain': domain,
                        'days': days,
                        'metrics': metrics_data
                    })
                }
            
            # Handle unknown paths
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Not found'})
            }
        
        # Handle other HTTP methods
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    except Exception as e:
        print(f"Error handling API request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def main():
    # Test metrics endpoint
    metrics_event = {
        'httpMethod': 'GET',
        'path': '/metrics/example.com',
        'queryStringParameters': {
            'days': '7'
        },
        'headers': {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzQ3NzUxMTA5LCJpYXQiOjE3NDc2NjQ3MDksInN1YiI6InRlc3QtdXNlciJ9.5hL4f07L0R65CYaAW2rQtvsCfQ6MWgqrBQzXhav3mQw'
        }
    }
    
    # Test domains endpoint
    domains_event = {
        'httpMethod': 'GET',
        'path': '/domains',
        'queryStringParameters': {},
        'headers': {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzQ3NzUxMTA5LCJpYXQiOjE3NDc2NjQ3MDksInN1YiI6InRlc3QtdXNlciJ9.5hL4f07L0R65CYaAW2rQtvsCfQ6MWgqrBQzXhav3mQw'
        }
    }
    
    # Test unauthorized request
    unauthorized_event = {
        'httpMethod': 'GET',
        'path': '/metrics/example.com',
        'queryStringParameters': {
            'days': '7'
        },
        'headers': {
            'Authorization': 'Bearer invalid-token'
        }
    }
    
    # Run the tests
    print("Test 1: Fetching Metrics")
    metrics_response = lambda_handler(metrics_event, {})
    print(f"Status Code: {metrics_response['statusCode']}")
    metrics_body = json.loads(metrics_response['body'])
    print(f"Domain: {metrics_body.get('domain')}")
    metrics = metrics_body.get('metrics', {})
    print(f"Revenue: ${metrics.get('revenue')}")
    print(f"Orders: {metrics.get('orders')}")
    print(f"Sessions: {metrics.get('visitors')}")
    print()
    
    print("Test 2: Listing Domains")
    domains_response = lambda_handler(domains_event, {})
    print(f"Status Code: {domains_response['statusCode']}")
    domains_body = json.loads(domains_response['body'])
    print(f"Number of domains: {len(domains_body.get('domains', []))}")
    for domain in domains_body.get('domains', []):
        print(f"- {domain.get('domain')}: {domain.get('name')}")
    print()
    
    print("Test 3: Unauthorized Request")
    unauth_response = lambda_handler(unauthorized_event, {})
    print(f"Status Code: {unauth_response['statusCode']}")
    unauth_body = json.loads(unauth_response['body'])
    print(f"Error: {unauth_body.get('error')}")
    
    # Print overall results
    print("\nTEST RESULTS:")
    if metrics_response['statusCode'] == 200 and domains_response['statusCode'] == 200 and unauth_response['statusCode'] == 401:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    main() 