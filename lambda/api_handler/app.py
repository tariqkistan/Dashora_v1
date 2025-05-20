import json
import os
import boto3
import jwt
from datetime import datetime, timedelta
from decimal import Decimal
import re

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

# Environment variables
METRICS_TABLE_NAME = os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics-v2')
DOMAINS_TABLE_NAME = os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains-v2')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'dashora-users-v2')
JWT_SECRET = os.environ.get('JWT_SECRET', 'da5h0raAn4lyt1csS3cretK3y2024Pr0duct10n')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
metrics_table = dynamodb.Table(METRICS_TABLE_NAME)
domains_table = dynamodb.Table(DOMAINS_TABLE_NAME)
users_table = dynamodb.Table(USERS_TABLE_NAME)

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        print(f"Verifying token: {token}")  # Debug log
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('user_id')
        print(f"Token verified successfully. User ID: {user_id}")  # Debug log
        return user_id
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return None

def get_user_domains(user_id):
    """Get domains associated with a user"""
    try:
        print(f"Getting domains for user: {user_id}")  # Debug log
        response = users_table.get_item(
            Key={
                'user_id': user_id
            }
        )
        user = response.get('Item', {})
        domains = user.get('domains', [])
        print(f"Found domains for user: {domains}")  # Debug log
        return domains
    except Exception as e:
        print(f"Error getting user domains: {str(e)}")
        return []

def get_latest_metrics(domain, days=7):
    """Get latest metrics for a domain"""
    try:
        print(f"Getting metrics for domain: {domain}, days: {days}")  # Debug log
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        response = metrics_table.query(
            KeyConditionExpression='domain = :domain AND #ts BETWEEN :start_time AND :end_time',
            ExpressionAttributeNames={
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues={
                ':domain': domain,
                ':start_time': start_time,
                ':end_time': end_time
            },
            ScanIndexForward=False  # Get newest first
        )
        metrics = response.get('Items', [])
        print(f"Found {len(metrics)} metrics records")  # Debug log
        return metrics
    except Exception as e:
        print(f"Error getting metrics: {str(e)}")
        return []

def create_response(status_code, body):
    """Create API Gateway response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    """API Gateway Lambda handler"""
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
        user_id = verify_token(token) if token else None
        print(f"User ID: {user_id}")  # Debug log
        
        # Handle unauthenticated requests
        if not user_id:
            return create_response(401, {'error': 'Unauthorized'})
        
        # Handle OPTIONS requests (CORS)
        if http_method == 'OPTIONS':
            return create_response(200, {})
        
        # Get user's domains
        user_domains = get_user_domains(user_id)
        print(f"User domains: {user_domains}")  # Debug log
        
        # Handle GET requests
        if http_method == 'GET':
            # Root path - return basic info
            if path == '/':
                return create_response(200, {
                    'message': 'Dashora Analytics API',
                    'version': '1.0.0',
                    'user_id': user_id
                })
            
            # List domains
            elif path == '/domains':
                domains_data = []
                for domain_name in user_domains:
                    try:
                        response = domains_table.get_item(
                            Key={
                                'domain': domain_name
                            }
                        )
                        domain_item = response.get('Item')
                        if domain_item:
                            domains_data.append(domain_item)
                    except Exception as e:
                        print(f"Error getting domain {domain_name}: {str(e)}")
                
                return create_response(200, {'domains': domains_data})
            
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
                    return create_response(403, {'error': 'Access denied to this domain'})
                
                # Get metrics for the domain
                metrics_data = get_latest_metrics(domain, days)
                print(f"Metrics data: {json.dumps(metrics_data, default=str)}")  # Debug log
                
                return create_response(200, {
                    'domain': domain,
                    'days': days,
                    'metrics': metrics_data
                })
            
            # Handle unknown paths
            return create_response(404, {'error': 'Not found'})
        
        # Handle other HTTP methods
        return create_response(405, {'error': 'Method not allowed'})
    
    except Exception as e:
        print(f"Error handling API request: {str(e)}")
        return create_response(500, {'error': str(e)}) 