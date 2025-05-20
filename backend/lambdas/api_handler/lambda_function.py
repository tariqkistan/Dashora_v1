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

# Initialize Secrets Manager client
secrets_client = boto3.client('secretsmanager')

def get_jwt_secret():
    """Retrieve JWT secret from AWS Secrets Manager"""
    secret_name = "dashora/jwt-secret"
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret['jwt_secret']
    except Exception as e:
        print(f"Error retrieving JWT secret: {str(e)}")
        # Fallback to environment variable if secrets manager fails
        return os.environ.get('JWT_SECRET', 'dashora-default-secret')

def verify_token(token):
    """Verify JWT token and return user ID if valid"""
    try:
        jwt_secret = get_jwt_secret()
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        return None

def get_user_domains(user_id):
    """Get domains associated with a user"""
    try:
        user = users_table.get_item(
            Key={
                'user_id': user_id
            }
        ).get('Item')
        
        if not user:
            return []
        
        return user.get('domains', [])
    except Exception as e:
        print(f"Error getting user domains: {str(e)}")
        return []

def get_domain_metrics(domain, source=None, days=7):
    """Get metrics for a specific domain"""
    try:
        # Calculate time range
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Base query
        query_params = {
            'KeyConditionExpression': 'domain = :domain AND timestamp BETWEEN :start_time AND :end_time',
            'ExpressionAttributeValues': {
                ':domain': domain,
                ':start_time': start_time,
                ':end_time': end_time
            },
            'ScanIndexForward': False  # Sort in descending order (newest first)
        }
        
        # Add source filter if specified
        if source:
            query_params['FilterExpression'] = 'source = :source'
            query_params['ExpressionAttributeValues'][':source'] = source
        
        # Query metrics table
        response = metrics_table.query(**query_params)
        
        return response.get('Items', [])
    except Exception as e:
        print(f"Error getting domain metrics: {str(e)}")
        return []

def get_latest_metrics(domain, days=7):
    """Get the latest metrics for a domain from all sources"""
    try:
        # Get the latest combined metrics
        combined_metrics = get_domain_metrics(domain, 'combined', days)
        
        if combined_metrics:
            return combined_metrics[0]
        
        # If no combined metrics, get individual metrics
        woocommerce_metrics = get_domain_metrics(domain, 'woocommerce', days)
        ga_metrics = get_domain_metrics(domain, 'google_analytics', days)
        
        # Return whatever metrics are available
        result = {
            'domain': domain,
            'timestamp': int(datetime.now().timestamp()),
            'metrics': {}
        }
        
        if woocommerce_metrics:
            result['woocommerce'] = woocommerce_metrics[0].get('metrics', {})
        
        if ga_metrics:
            result['google_analytics'] = ga_metrics[0].get('metrics', {})
        
        return result
    except Exception as e:
        print(f"Error getting latest metrics: {str(e)}")
        return {'domain': domain, 'error': str(e)}

def lambda_handler(event, context):
    """API Gateway Lambda handler"""
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Get authorization header
        headers = event.get('headers', {}) or {}
        auth_header = headers.get('Authorization', '')
        
        # Extract token if it exists
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        # Verify token and get user ID
        user_id = verify_token(token) if token else None
        
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
        
        # Handle GET requests
        if http_method == 'GET':
            # List domains
            if path == '/domains':
                domains_data = []
                for domain_name in user_domains:
                    domain_item = domains_table.get_item(
                        Key={
                            'domain': domain_name
                        }
                    ).get('Item')
                    if domain_item:
                        domains_data.append(domain_item)
                
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
                domain = path.split('/')[-1]
                days = int(query_params.get('days', 7))
                
                # Check if user has access to this domain
                if domain not in user_domains:
                    return {
                        'statusCode': 403,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Access denied to this domain'})
                    }
                
                # Get metrics
                metrics = get_latest_metrics(domain, days)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(metrics)
                }
            
            # Handle unknown paths
            else:
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