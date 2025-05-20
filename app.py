import json
import os
import boto3
from datetime import datetime, timedelta
import jwt

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
metrics_table = dynamodb.Table(os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics'))
domains_table = dynamodb.Table(os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains'))
users_table = dynamodb.Table(os.environ.get('USERS_TABLE_NAME', 'dashora-users'))

# JWT secret from environment variable
JWT_SECRET = os.environ.get('JWT_SECRET', 'da5h0raAn4lyt1csS3cretK3y2024Pr0duct10n')

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('user_id')
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return None

def get_user_domains(user_id):
    """Get domains associated with a user"""
    try:
        response = users_table.get_item(
            Key={
                'user_id': user_id
            }
        )
        user = response.get('Item', {})
        return user.get('domains', [])
    except Exception as e:
        print(f"Error getting user domains: {str(e)}")
        return []

def lambda_handler(event, context):
    """API Gateway Lambda handler"""
    try:
        print("Event:", json.dumps(event))  # Debug log
        
        # Get the HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
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
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization'
                },
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Handle OPTIONS requests (CORS)
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,POST',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization'
                },
                'body': ''
            }
        
        # Get user's domains
        user_domains = get_user_domains(user_id)
        print(f"User domains: {user_domains}")  # Debug log
        
        # Handle GET requests
        if http_method == 'GET':
            # List domains
            if path == '/domains':
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
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'domains': domains_data})
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