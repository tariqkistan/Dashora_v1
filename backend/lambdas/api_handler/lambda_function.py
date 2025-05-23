import json
import os
import boto3
import jwt
import time
from decimal import Decimal
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr
import decimal

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-default-secret-key')
JWT_EXPIRATION = 3600  # 1 hour in seconds

# DynamoDB tables
USERS_TABLE = os.environ.get('USERS_TABLE_NAME', 'dashora-users')
DOMAINS_TABLE = os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains')
METRICS_TABLE = os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics')

# Helper class for DynamoDB decimal serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handle_login(event):
    """Handle login requests"""
    try:
        # Log incoming event for debugging
        print(f"LOGIN REQUEST EVENT: {json.dumps(event)}")
        
        # Parse request body
        body = json.loads(event.get('body', '{}') or '{}')
        print(f"Parsed body: {json.dumps(body)}")
        
        email = body.get('email')
        password = body.get('password')
        
        print(f"Email: {email}, Password length: {len(password) if password else 0}")
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Email and password are required'
                })
            }
        
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        users_table = dynamodb.Table(USERS_TABLE)
        print(f"DynamoDB table name: {USERS_TABLE}")
        
        # Check if in development mode (allow test login)
        is_dev_mode = os.environ.get('STAGE') == 'dev'
        print(f"Development mode: {is_dev_mode}")
        
        # Query for user with matching email
        if not is_dev_mode:
            response = users_table.scan(
                FilterExpression=Attr('email').eq(email)
            )
            
            if response['Count'] == 0:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        'error': 'Invalid credentials'
                    })
                }
                
            user = response['Items'][0]
            
            # Validate password (in a real app, use proper password hashing)
            if user.get('password') != password:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        'error': 'Invalid credentials'
                    })
                }
                
            user_id = user.get('user_id')
        else:
            # In development mode, allow any login
            user_id = 'test-user'
        
        # Generate JWT token
        now = int(time.time())
        token_payload = {
            'user_id': user_id,
            'email': email,
            'iat': now,
            'exp': now + JWT_EXPIRATION
        }
        
        print(f"Creating token with payload: {json.dumps(token_payload)}")
        print(f"Using JWT_SECRET: {JWT_SECRET[:3]}...{JWT_SECRET[-3:]} (length: {len(JWT_SECRET)})")
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
        
        print(f"Token generated successfully: {token[:10]}...")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email
                }
            })
        }
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in login handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"Login error: {str(e)}"
            })
        }

def handle_get_domains(event, user_id):
    """Handle get domains request"""
    try:
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        domains_table = dynamodb.Table(DOMAINS_TABLE)
        print(f"Querying domains for user_id: {user_id}")
        
        # Check if in development mode
        is_dev_mode = os.environ.get('STAGE') == 'dev'
        print(f"Development mode: {is_dev_mode}")
        
        if is_dev_mode and user_id == 'test-user':
            # In development mode, return mock domains
            print("Using mock domains data for test user")
            domains = [
                {
                    'domain': 'example.com',
                    'name': 'Example Store',
                    'woocommerce_enabled': True,
                    'ga_enabled': True
                },
                {
                    'domain': 'test-store.com',
                    'name': 'Test Store',
                    'woocommerce_enabled': True,
                    'ga_enabled': False
                }
            ]
        else:
            # Query domains for the authenticated user
            response = domains_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            
            domains = []
            for item in response['Items']:
                domains.append({
                    'domain': item.get('domain_id'),
                    'name': item.get('name', ''),
                    'woocommerce_enabled': item.get('woocommerce_enabled', False),
                    'ga_enabled': item.get('ga_enabled', False)
                })
        
        print(f"Found {len(domains)} domains")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'domains': domains
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in get domains handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"Domain fetch error: {str(e)}"
            })
        }

def handle_get_metrics(event, user_id):
    """Handle get metrics request"""
    try:
        # Parse path parameters
        path_params = event.get('pathParameters', {}) or {}
        domain = path_params.get('domain')
        print(f"Metrics request for domain: {domain}")
        
        if not domain:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain parameter is required'
                })
            }
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        period = query_params.get('period', '30d')  # Default to 30 days
        print(f"Period requested: {period}")
        
        # Calculate time range based on period
        end_time = int(datetime.utcnow().timestamp())
        
        if period == '7d':
            days = 7
        elif period == '14d':
            days = 14
        elif period == '90d':
            days = 90
        else:  # Default to 30 days
            days = 30
            
        start_time = int((datetime.utcnow() - timedelta(days=days)).timestamp())
        print(f"Time range: {start_time} to {end_time}")
        
        # Check if in development mode
        is_dev_mode = os.environ.get('STAGE') == 'dev'
        print(f"Development mode: {is_dev_mode}")
        
        if is_dev_mode and user_id == 'test-user':
            # Generate mock metrics data for test user
            print("Generating mock metrics data")
            metrics = []
            
            # Generate data points for each day in the requested range
            current_time = start_time
            while current_time < end_time:
                # Create random metrics
                import random
                pageviews = random.randint(100, 2000)
                visitors = random.randint(50, 500)
                orders = random.randint(5, 50)
                revenue = round(orders * random.uniform(20, 100), 2)
                
                metrics.append({
                    'domain': domain,
                    'timestamp': current_time,
                    'pageviews': pageviews,
                    'visitors': visitors,
                    'orders': orders,
                    'revenue': revenue
                })
                
                # Move to next day
                current_time += 86400  # seconds in a day
        else:
            # Connect to DynamoDB
            dynamodb = boto3.resource('dynamodb')
            metrics_table = dynamodb.Table(METRICS_TABLE)
            
            # Create domain_id 
            domain_id = f"{domain}"
            print(f"Looking up domain_id: {domain_id}")
            
            # Query metrics for domain and time range
            response = metrics_table.query(
                KeyConditionExpression=Key('domain_id').eq(domain_id) & 
                                    Key('timestamp').between(str(start_time), str(end_time))
            )
            
            metrics = []
            for item in response['Items']:
                metrics.append({
                    'domain': domain,
                    'timestamp': int(item.get('timestamp')),
                    'pageviews': item.get('pageviews', 0),
                    'visitors': item.get('visitors', 0),
                    'orders': item.get('orders', 0),
                    'revenue': item.get('revenue', 0)
                })
        
        print(f"Found {len(metrics)} metrics records")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'metrics': metrics
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in get metrics handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"Metrics fetch error: {str(e)}"
            })
        }

def verify_token(event):
    """Verify JWT token from Authorization header"""
    try:
        # Get Authorization header
        headers = event.get('headers', {}) or {}
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        print(f"Auth header found: {auth_header}")
        
        if not auth_header:
            print("No Authorization header found")
            return None
        
        # Handle both Bearer token and raw token formats
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # If it's just the raw token
            token = auth_header
        
        print(f"Extracted token: {token[:10]}...")
        print(f"Using JWT_SECRET: {JWT_SECRET[:3]}...{JWT_SECRET[-3:]} (length: {len(JWT_SECRET)})")
        
        # Verify token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            print(f"Token decoded successfully: {payload}")
            
            # Check if token is expired
            if payload.get('exp', 0) < time.time():
                print("Token is expired")
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            print("Token signature has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {str(e)}")
            return None
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error verifying token: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return None

def handle_woocommerce_connect(event, user_id):
    """Handle WooCommerce connection request"""
    try:
        # Parse path parameters and request body
        path_params = event.get('pathParameters', {}) or {}
        domain = path_params.get('domain')
        
        body = json.loads(event.get('body', '{}'))
        consumer_key = body.get('consumer_key')
        consumer_secret = body.get('consumer_secret')
        store_domain = body.get('domain', domain)
        
        print(f"WooCommerce connect request for domain: {domain}")
        print(f"Store domain: {store_domain}")
        
        if not domain or not consumer_key or not consumer_secret:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain, consumer key and consumer secret are required'
                })
            }
        
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        domains_table = dynamodb.Table(DOMAINS_TABLE)
        
        # First, verify that the domain exists and belongs to the user
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
        )
        
        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain not found or does not belong to this user'
                })
            }
        
        # Test the WooCommerce API connection
        try:
            import requests
            from datetime import datetime, timedelta
            
            # Format the URL correctly
            if not store_domain.startswith('http'):
                store_url = f"https://{store_domain}"
            else:
                store_url = store_domain
            
            # Test URL - get basic store info
            test_url = f"{store_url}/wp-json/wc/v3/system_status"
            
            # Parameters for WooCommerce API with authentication in query string
            params = {
                'consumer_key': consumer_key,
                'consumer_secret': consumer_secret,
                'per_page': 1
            }
            
            # Make the request using query string authentication instead of headers
            print(f"Testing WooCommerce connection to {test_url}")
            test_response = requests.get(test_url, params=params)
            
            if test_response.status_code == 200:
                print("WooCommerce connection successful")
                
                # Get store information
                store_info_url = f"{store_url}/wp-json/wc/v3/products"
                store_response = requests.get(store_info_url, params={**params, 'per_page': 5})
                store_data = store_response.json()
                product_count = len(store_data)
                
                # Get recent orders
                orders_url = f"{store_url}/wp-json/wc/v3/orders"
                order_response = requests.get(orders_url, params={**params, 'per_page': 1})
                order_data = order_response.json()
                last_order_date = order_data[0]['date_created'] if order_data else None
                
                # Create store name from domain if not provided in response
                store_name = domain.split('.')[0].capitalize()
                
                # Store API credentials in DynamoDB
                domains_table.update_item(
                    Key={
                        'user_id': user_id,
                        'domain_id': domain
                    },
                    UpdateExpression="set wc_consumer_key = :key, wc_consumer_secret = :secret, woocommerce_enabled = :enabled",
                    ExpressionAttributeValues={
                        ':key': consumer_key,
                        ':secret': consumer_secret,
                        ':enabled': True
                    }
                )
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        'success': True,
                        'message': 'WooCommerce connection successful',
                        'store_name': store_name,
                        'product_count': product_count,
                        'last_order_date': last_order_date
                    }, default=str)
                }
            else:
                print(f"WooCommerce connection failed: {test_response.status_code} - {test_response.text}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        'error': f"WooCommerce connection failed: {test_response.text}"
                    })
                }
        except Exception as e:
            import traceback
            print(f"Error testing WooCommerce connection: {str(e)}")
            print(traceback.format_exc())
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': f"WooCommerce connection error: {str(e)}"
                })
            }
        
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in WooCommerce connect handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"WooCommerce connection error: {str(e)}"
            })
        }

def handle_woocommerce_disconnect(event, user_id):
    """Handle WooCommerce disconnection request"""
    try:
        # Parse path parameters
        path_params = event.get('pathParameters', {}) or {}
        domain = path_params.get('domain')
        
        print(f"WooCommerce disconnect request for domain: {domain}")
        
        if not domain:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain parameter is required'
                })
            }
        
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        domains_table = dynamodb.Table(DOMAINS_TABLE)
        
        # First, verify that the domain exists and belongs to the user
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
        )
        
        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain not found or does not belong to this user'
                })
            }
        
        # Remove WooCommerce credentials and disable it
        domains_table.update_item(
            Key={
                'user_id': user_id,
                'domain_id': domain
            },
            UpdateExpression="set woocommerce_enabled = :enabled remove wc_consumer_key, wc_consumer_secret",
            ExpressionAttributeValues={
                ':enabled': False
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'success': True,
                'message': 'WooCommerce connection removed'
            })
        }
        
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in WooCommerce disconnect handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"WooCommerce disconnection error: {str(e)}"
            })
        }

def handle_woocommerce_details(event, user_id):
    """Handle WooCommerce integration details request"""
    try:
        # Parse path parameters
        path_params = event.get('pathParameters', {}) or {}
        domain = path_params.get('domain')
        
        print(f"WooCommerce details request for domain: {domain}")
        
        if not domain:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain parameter is required'
                })
            }
        
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        domains_table = dynamodb.Table(DOMAINS_TABLE)
        
        # Get domain data
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
        )
        
        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain not found or does not belong to this user'
                })
            }
        
        domain_data = response['Items'][0]
        
        # Check if WooCommerce is enabled
        if not domain_data.get('woocommerce_enabled', False):
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'WooCommerce not enabled for this domain'
                })
            }
        
        # Get WooCommerce credentials
        consumer_key = domain_data.get('wc_consumer_key')
        consumer_secret = domain_data.get('wc_consumer_secret')
        
        if not consumer_key or not consumer_secret:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'WooCommerce credentials not found'
                })
            }
        
        # Test the WooCommerce API connection to get store details
        try:
            import requests
            
            # Format the URL correctly
            store_url = f"https://{domain}"
            
            # Parameters for WooCommerce API with authentication in query string
            params = {
                'consumer_key': consumer_key,
                'consumer_secret': consumer_secret,
                'per_page': 5
            }
            
            # Get store information
            products_url = f"{store_url}/wp-json/wc/v3/products"
            products_response = requests.get(products_url, params=params)
            
            if products_response.status_code == 200:
                products = products_response.json()
                product_count = len(products)
                
                # Get recent orders
                orders_url = f"{store_url}/wp-json/wc/v3/orders"
                orders_params = {
                    'consumer_key': consumer_key,
                    'consumer_secret': consumer_secret,
                    'per_page': 1
                }
                orders_response = requests.get(orders_url, params=orders_params)
                
                if orders_response.status_code == 200:
                    orders = orders_response.json()
                    if orders:
                        last_order_date = orders[0].get('date_created')
                else:
                    last_order_date = None
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        'store_name': domain_data.get('name'),
                        'product_count': product_count,
                        'last_order_date': last_order_date,
                        'connected': True
                    }, default=str)
                }
            else:
                # API connection failed
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                    },
                    'body': json.dumps({
                        'error': f"WooCommerce API connection failed: {products_response.text}"
                    })
                }
        except Exception as e:
            import traceback
            print(f"Error fetching WooCommerce details: {str(e)}")
            print(traceback.format_exc())
            
            # Return basic connection info without live store details
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'store_name': domain_data.get('name'),
                    'connected': True
                })
            }
        
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in WooCommerce details handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"Error getting WooCommerce details: {str(e)}"
            })
        }

def handle_add_domain(event, user_id):
    """Handle add domain request"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        domain = body.get('domain')
        name = body.get('name')
        woocommerce_enabled = body.get('woocommerce_enabled', False)
        ga_enabled = body.get('ga_enabled', False)
        
        print(f"Add domain request: domain={domain}, name={name}")
        
        if not domain or not name:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain and name are required'
                })
            }
        
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        domains_table = dynamodb.Table(DOMAINS_TABLE)
        
        # Check if domain already exists for this user
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
        )
        
        if response['Count'] > 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': 'Domain already exists'
                })
            }
        
        # Add domain to DynamoDB
        current_time = int(datetime.utcnow().timestamp())
        
        domains_table.put_item(
            Item={
                'user_id': user_id,
                'domain_id': domain,
                'name': name,
                'woocommerce_enabled': woocommerce_enabled,
                'ga_enabled': ga_enabled,
                'created_at': current_time,
                'updated_at': current_time
            }
        )
        
        print(f"Domain {domain} added for user {user_id}")
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'success': True,
                'domain_id': domain,
                'message': 'Domain added successfully'
            })
        }
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in add domain handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"Domain addition error: {str(e)}"
            })
        }

def lambda_handler(event, context):
    """Main Lambda handler function"""
    # Log full event for debugging
    print(f"LAMBDA EVENT: {json.dumps(event)}")
    print(f"LAMBDA CONTEXT: {context}")
    
    # Set default CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE',
        'Access-Control-Max-Age': '86400'
    }
    
    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Get request path and method
        path = event.get('path', '')
        http_method = event.get('httpMethod', '')
        print(f"Request path: {path}, method: {http_method}")
        
        # Handle login request (no auth required)
        if path == '/login' and http_method == 'POST':
            print("Handling login request")
            response = handle_login(event)
            response['headers'] = {**headers, **response.get('headers', {})}
            print(f"Login response status: {response.get('statusCode')}")
            return response
        
        # For all other endpoints, verify token
        payload = verify_token(event)
        
        if not payload:
            print("Token verification failed")
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Unauthorized'
                })
            }
        
        user_id = payload.get('user_id')
        print(f"Authenticated user_id: {user_id}")
        
        # Handle domains request
        if path == '/domains':
            if http_method == 'GET':
                print("Handling get domains request")
                response = handle_get_domains(event, user_id)
                response['headers'] = {**headers, **response.get('headers', {})}
                return response
            elif http_method == 'POST':
                print("Handling add domain request")
                response = handle_add_domain(event, user_id)
                response['headers'] = {**headers, **response.get('headers', {})}
                return response
        
        # Handle metrics request
        if path.startswith('/metrics/') and http_method == 'GET':
            print("Handling metrics request")
            response = handle_get_metrics(event, user_id)
            response['headers'] = {**headers, **response.get('headers', {})}
            return response
        
        # Handle WooCommerce integration endpoints
        if 'integrations/woocommerce' in path:
            # Extract domain from path
            path_parts = path.split('/')
            domain_index = path_parts.index('domains') + 1 if 'domains' in path_parts else -1
            
            if domain_index > 0 and domain_index < len(path_parts):
                # Parse domain name
                domain = path_parts[domain_index]
                print(f"Integration request for domain: {domain}")
                
                # Handle different integration endpoints
                if http_method == 'POST':
                    print("Handling WooCommerce connect request")
                    response = handle_woocommerce_connect(event, user_id)
                    response['headers'] = {**headers, **response.get('headers', {})}
                    return response
                    
                elif http_method == 'DELETE':
                    print("Handling WooCommerce disconnect request")
                    response = handle_woocommerce_disconnect(event, user_id)
                    response['headers'] = {**headers, **response.get('headers', {})}
                    return response
                    
                elif http_method == 'GET':
                    print("Handling WooCommerce details request")
                    response = handle_woocommerce_details(event, user_id)
                    response['headers'] = {**headers, **response.get('headers', {})}
                    return response
        
        # Return 404 for unknown endpoints
        print(f"Unknown endpoint: {path}")
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                'error': 'Not found'
            })
        }
        
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in Lambda handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': f"Server error: {str(e)}"
            })
        } 