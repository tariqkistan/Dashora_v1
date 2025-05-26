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
        
        domains = []
        
        # Always query real domains from database first
        try:
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        for item in response['Items']:
            domains.append({
                'domain': item.get('domain_id'),
                'name': item.get('name', ''),
                'woocommerce_enabled': item.get('woocommerce_enabled', False),
                'ga_enabled': item.get('ga_enabled', False)
            })
            
            print(f"Found {len(domains)} real domains from database")
        except Exception as e:
            print(f"Error querying real domains: {str(e)}")
        
        # In development mode, add mock domains if no real domains exist
        if is_dev_mode and user_id == 'test-user' and len(domains) == 0:
            print("Adding mock domains data for test user (no real domains found)")
            domains.extend([
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
            ])
        
        print(f"Returning {len(domains)} total domains")
        
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
        
        print(f"All headers: {headers}")
        print(f"Auth header found: {auth_header}")
        print(f"Auth header type: {type(auth_header)}")
        
        if not auth_header:
            print("No Authorization header found")
            return None
        
        # Handle both Bearer token and raw token formats
        if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
            print(f"Extracted Bearer token: {token[:10]}...")
        else:
            # If it's just the raw token
            token = auth_header
            print(f"Using raw token: {token[:10]}...")
        
        # Validate token format - JWT tokens should have 3 parts separated by dots
        token_parts = token.split('.')
        if len(token_parts) != 3:
            print(f"Invalid token format - expected 3 parts, got {len(token_parts)}")
            print(f"Token parts: {token_parts}")
            return None
        
        print(f"Token parts: header={token_parts[0][:10]}..., payload={token_parts[1][:10]}..., signature={token_parts[2][:10]}...")
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
            print(f"Invalid token error: {str(e)}")
            print(f"Token being decoded: {token}")
            return None
    except Exception as e:
            print(f"Unexpected error decoding token: {str(e)}")
            print(f"Token being decoded: {token}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
        print(f"User ID: {user_id}")
        print(f"Consumer key: {consumer_key[:10]}..." if consumer_key else "None")
        print(f"Consumer secret: {consumer_secret[:10]}..." if consumer_secret else "None")
        
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
        print(f"Checking if domain exists: user_id={user_id}, domain_id={domain}")
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
        )
        
        print(f"Domain existence check: Count={response['Count']}")
        if response['Count'] > 0:
            print(f"Existing domain data: {response['Items'][0]}")
        
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
        
        # Store WooCommerce credentials in domain record
        try:
            from datetime import datetime
            print(f"Storing WooCommerce credentials for user_id={user_id}, domain_id={domain}")
            
            # Update domain with WooCommerce credentials
            update_response = domains_table.update_item(
                Key={
                    'user_id': user_id,
                    'domain_id': domain
                },
                UpdateExpression='SET wc_consumer_key = :key, wc_consumer_secret = :secret, woocommerce_enabled = :enabled, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':key': consumer_key,
                    ':secret': consumer_secret,
                    ':enabled': True,
                    ':updated_at': int(datetime.utcnow().timestamp())
                },
                ReturnValues='ALL_NEW'
            )
            
            print(f"WooCommerce credentials stored successfully for domain: {domain}")
            print(f"Updated item: {update_response.get('Attributes', {})}")
        except Exception as e:
            print(f"Error storing WooCommerce credentials: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # Continue with the connection test even if storage fails
        
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
            
            # Explicitly set headers to avoid any authorization header issues
            headers = {
                'User-Agent': 'Dashora/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Make the request using query string authentication instead of headers
            print(f"Testing WooCommerce connection to {test_url}")
            test_response = requests.get(test_url, params=params, headers=headers, timeout=30)
            
            if test_response.status_code == 200:
                print("WooCommerce connection successful")
                
                # Get store information
                store_info_url = f"{store_url}/wp-json/wc/v3/products"
                store_response = requests.get(store_info_url, params={**params, 'per_page': 5}, headers=headers, timeout=30)
                store_data = store_response.json()
                product_count = len(store_data)
                
                # Get recent orders
                orders_url = f"{store_url}/wp-json/wc/v3/orders"
                order_response = requests.get(orders_url, params={**params, 'per_page': 1}, headers=headers, timeout=30)
                order_data = order_response.json()
                last_order_date = order_data[0]['date_created'] if order_data else None
                
                # Create store name from domain if not provided in response
                store_name = domain.split('.')[0].capitalize()
                
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
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'error': f"Error testing WooCommerce connection: {str(e)}"
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
    """Handle WooCommerce integration details request with time filtering"""
    try:
        # Parse path parameters
        path_params = event.get('pathParameters', {}) or {}
        domain = path_params.get('domain')
        
        # Parse query parameters for time filtering
        query_params = event.get('queryStringParameters') or {}
        time_period = query_params.get('period', 'all')  # all, today, week, month
        
        print(f"WooCommerce details request for domain: {domain}, period: {time_period}")
        print(f"User ID: {user_id}")
        print(f"Path params: {path_params}")
        print(f"Query params: {query_params}")
        
        if not domain:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({'error': 'Domain parameter is required'})
            }
        
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        domains_table = dynamodb.Table(DOMAINS_TABLE)
        
        # Get domain data
        print(f"Querying DynamoDB for user_id: {user_id}, domain_id: {domain}")
        response = domains_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
        )
        
        print(f"DynamoDB query response: Count={response['Count']}")
        if response['Count'] > 0:
            print(f"Domain data found: {response['Items'][0]}")
        else:
            # Let's also try to scan all domains for this user to see what's available
            scan_response = domains_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            print(f"All domains for user {user_id}: {[item.get('domain_id') for item in scan_response['Items']]}")
        
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
        print(f"Domain data retrieved: {domain_data}")
        
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
        
        print(f"WooCommerce credentials found: key={bool(consumer_key)}, secret={bool(consumer_secret)}")
        
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
            from datetime import datetime, timedelta
            import concurrent.futures
            
            # Format the URL correctly
            store_url = f"https://{domain}"
            
            # Parameters for WooCommerce API with authentication in query string
            params = {
                'consumer_key': consumer_key,
                'consumer_secret': consumer_secret
            }
            
            # Explicitly set headers to avoid any authorization header issues
            headers = {
                'User-Agent': 'Dashora/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            print(f"Fetching WooCommerce data for {store_url}")
            
            # Initialize default values
            total_orders = 0
            current_revenue = 0.0
            daily_revenue = 0.0
            weekly_revenue = 0.0
            monthly_revenue = 0.0
            daily_orders = 0
            weekly_orders = 0
            monthly_orders = 0
            currency = 'ZAR'
            recent_orders_count = 0
            top_products = []
            store_currency = currency
            store_country = 'Unknown'
            
            # Calculate date ranges for filtering
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)
            
            print(f"Date ranges - Today: {today_start}, Week: {week_start}, Month: {month_start}")
            
            # Function to make API calls with timeout
            def make_api_call(url, call_params, timeout=15):
                try:
                    response = requests.get(url, params=call_params, headers=headers, timeout=timeout)
                    if response.status_code == 200:
                        return response
                    else:
                        print(f"API call failed with status {response.status_code}: {url}")
                        return None
                except Exception as e:
                    print(f"API call error for {url}: {str(e)}")
                    return None
            
            # 1. Get total number of orders (quick call)
            orders_url = f"{store_url}/wp-json/wc/v3/orders"
            orders_params = {**params, 'per_page': 1, 'status': 'any'}
            orders_response = make_api_call(orders_url, orders_params)
            
            if orders_response:
                total_orders = int(orders_response.headers.get('X-WP-Total', 0))
                print(f"Total orders: {total_orders}")
            
            # 2. Get current revenue (completed orders) - limit to 100 for better time analysis
            revenue_params = {
                **params, 
                'per_page': 100,  # Increased to get more orders for time analysis
                'status': 'completed',
                'orderby': 'date',
                'order': 'desc'
            }
            revenue_response = make_api_call(orders_url, revenue_params)
            
            if revenue_response:
                try:
                    orders_data = revenue_response.json()
                    for order in orders_data:
                        # Sum up the total from completed orders
                        order_total = float(order.get('total', 0))
                        current_revenue += order_total
                        recent_orders_count += 1
                        
                        # Parse order date for time filtering
                        order_date_str = order.get('date_created', '')
                        if order_date_str:
                            try:
                                # Parse WooCommerce date format (ISO 8601)
                                order_date = datetime.fromisoformat(order_date_str.replace('Z', '+00:00'))
                                order_date_utc = order_date.replace(tzinfo=None)  # Convert to naive UTC
                                
                                # Check if order falls within time periods
                                if order_date_utc >= today_start:
                                    daily_revenue += order_total
                                    daily_orders += 1
                                
                                if order_date_utc >= week_start:
                                    weekly_revenue += order_total
                                    weekly_orders += 1
                                
                                if order_date_utc >= month_start:
                                    monthly_revenue += order_total
                                    monthly_orders += 1
                                    
                            except Exception as date_error:
                                print(f"Error parsing order date {order_date_str}: {str(date_error)}")
                        
                        # Get currency from first order
                        if currency == 'ZAR' and order.get('currency'):
                            currency = order.get('currency')
                    
                    print(f"Revenue calculated - Total: {current_revenue}, Daily: {daily_revenue}, Weekly: {weekly_revenue}, Monthly: {monthly_revenue}")
                    print(f"Orders counted - Total: {recent_orders_count}, Daily: {daily_orders}, Weekly: {weekly_orders}, Monthly: {monthly_orders}")
                except Exception as e:
                    print(f"Error processing orders data: {str(e)}")
            
            # 3. Get top selling products - limit to 20 for speed
            products_url = f"{store_url}/wp-json/wc/v3/products"
            products_params = {
                **params,
                'per_page': 20,  # Reduced from 50 for faster response
                'orderby': 'popularity',
                'order': 'desc'
            }
            products_response = make_api_call(products_url, products_params)
            
            if products_response:
                try:
                    products_data = products_response.json()
                    
                    # Sort products by total_sales (if available) or use the order from API
                    sorted_products = sorted(
                        products_data, 
                        key=lambda x: int(x.get('total_sales', 0)), 
                        reverse=True
                    )
                    
                    # Get top 3 products
                    for i, product in enumerate(sorted_products[:3]):
                        top_products.append({
                            'name': product.get('name', 'Unknown Product'),
                            'total_sales': int(product.get('total_sales', 0)),
                            'price': float(product.get('price', 0)),
                            'image': product.get('images', [{}])[0].get('src', '') if product.get('images') else '',
                            'sku': product.get('sku', ''),
                            'stock_status': product.get('stock_status', 'unknown')
                        })
                    
                    print(f"Top {len(top_products)} selling products retrieved")
                except Exception as e:
                    print(f"Error processing products data: {str(e)}")
            
            # 4. Get store currency and basic info (optional, skip if taking too long)
            try:
                settings_url = f"{store_url}/wp-json/wc/v3/settings/general"
                settings_response = make_api_call(settings_url, params, timeout=10)
                
                if settings_response:
                    settings_data = settings_response.json()
                    for setting in settings_data:
                        if setting.get('id') == 'woocommerce_currency':
                            store_currency = setting.get('value', currency)
                        elif setting.get('id') == 'woocommerce_default_country':
                            store_country = setting.get('value', 'Unknown')
            except Exception as e:
                print(f"Error getting store settings (non-critical): {str(e)}")
                store_currency = currency  # Use currency from orders
            
            # Prepare the response with all the data including time-based metrics
            woocommerce_data = {
                'store_name': domain_data.get('name', domain.split('.')[0].capitalize()),
                'connected': True,
                'total_orders': total_orders,
                'current_revenue': {
                    'amount': round(current_revenue, 2),
                    'currency': store_currency,
                    'from_orders': recent_orders_count
                },
                'daily_revenue': {
                    'amount': round(daily_revenue, 2),
                    'currency': store_currency,
                    'orders': daily_orders
                },
                'weekly_revenue': {
                    'amount': round(weekly_revenue, 2),
                    'currency': store_currency,
                    'orders': weekly_orders
                },
                'monthly_revenue': {
                    'amount': round(monthly_revenue, 2),
                    'currency': store_currency,
                    'orders': monthly_orders
                },
                'top_products': top_products,
                'store_info': {
                    'currency': store_currency,
                    'country': store_country,
                    'domain': domain
                },
                'time_period': time_period,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            print(f"WooCommerce data compiled successfully")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps(woocommerce_data, default=str)
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
        
        current_time = int(datetime.utcnow().timestamp())
        
        if response['Count'] > 0:
            # Domain exists, update it instead of returning error
            print(f"Domain {domain} already exists for user {user_id}, updating...")
            
            domains_table.update_item(
                Key={
                    'user_id': user_id,
                    'domain_id': domain
                },
                UpdateExpression='SET #name = :name, woocommerce_enabled = :wc_enabled, ga_enabled = :ga_enabled, updated_at = :updated_at',
                ExpressionAttributeNames={
                    '#name': 'name'  # 'name' is a reserved keyword in DynamoDB
                },
                ExpressionAttributeValues={
                    ':name': name,
                    ':wc_enabled': woocommerce_enabled,
                    ':ga_enabled': ga_enabled,
                    ':updated_at': current_time
                }
            )
            
            print(f"Domain {domain} updated for user {user_id}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
                },
                'body': json.dumps({
                    'success': True,
                    'domain_id': domain,
                    'message': 'Domain updated successfully'
                })
            }
        
        # Add new domain to DynamoDB
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

def handle_delete_domain(event, user_id):
    """Handle delete domain request"""
    try:
        # Parse path parameters
        path_params = event.get('pathParameters', {}) or {}
        domain = path_params.get('domain')
        
        print(f"Delete domain request: domain={domain}, user_id={user_id}")
        
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
        
        # Check if domain exists and belongs to this user
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
        
        # Delete the domain
        domains_table.delete_item(
            Key={
                'user_id': user_id,
                'domain_id': domain
            }
        )
        
        print(f"Domain {domain} deleted for user {user_id}")
        
        # Also clean up any associated metrics data
        try:
            metrics_table = dynamodb.Table(METRICS_TABLE)
            
            # Query all metrics for this domain
            metrics_response = metrics_table.query(
                KeyConditionExpression=Key('domain_id').eq(domain)
            )
            
            # Delete metrics in batches
            with metrics_table.batch_writer() as batch:
                for item in metrics_response['Items']:
                    batch.delete_item(
                        Key={
                            'domain_id': item['domain_id'],
                            'timestamp': item['timestamp']
                        }
                    )
            
            print(f"Cleaned up {len(metrics_response['Items'])} metrics records for domain {domain}")
        except Exception as e:
            print(f"Error cleaning up metrics for domain {domain}: {str(e)}")
            # Continue even if metrics cleanup fails
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Domain deleted successfully'
            })
        }
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error in delete domain handler: {str(e)}")
        print(f"Stack trace: {stack_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
            },
            'body': json.dumps({
                'error': f"Domain deletion error: {str(e)}"
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
            # In development mode, allow test-user to proceed
            is_dev_mode = os.environ.get('STAGE') == 'dev'
            if is_dev_mode:
                print("Development mode: Using fallback test user")
                payload = {'user_id': 'test-user', 'email': 'test@example.com'}
            else:
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
            elif http_method == 'DELETE':
                print("Handling delete domain request")
                response = handle_delete_domain(event, user_id)
                response['headers'] = {**headers, **response.get('headers', {})}
                return response
        
        # Handle test endpoint for debugging
        if path == '/test' and http_method == 'GET':
            print("Handling test request")
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Test endpoint',
                    'user_id': user_id,
                    'headers_received': event.get('headers', {}),
                    'path': path,
                    'method': http_method
                })
            }
        
        # Handle debug endpoint for JWT debugging
        if path == '/debug' and http_method == 'GET':
            print("Handling debug request")
            auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
            token_info = {}
            
            if auth_header:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    token = auth_header
                
                token_parts = token.split('.')
                token_info = {
                    'token_length': len(token),
                    'token_parts_count': len(token_parts),
                    'token_preview': token[:20] + '...' if len(token) > 20 else token,
                    'header_part': token_parts[0] if len(token_parts) > 0 else None,
                    'payload_part': token_parts[1][:20] + '...' if len(token_parts) > 1 and len(token_parts[1]) > 20 else token_parts[1] if len(token_parts) > 1 else None,
                    'signature_part': token_parts[2][:20] + '...' if len(token_parts) > 2 and len(token_parts[2]) > 20 else token_parts[2] if len(token_parts) > 2 else None
                }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Debug endpoint',
                    'auth_header': auth_header,
                    'token_info': token_info,
                    'all_headers': event.get('headers', {}),
                    'jwt_secret_length': len(JWT_SECRET),
                    'stage': os.environ.get('STAGE', 'unknown')
                })
            }
        
        # Handle metrics request
        if path.startswith('/metrics/') and http_method == 'GET':
            print("Handling metrics request")
            response = handle_get_metrics(event, user_id)
            response['headers'] = {**headers, **response.get('headers', {})}
            return response
        
        # Handle individual domain deletion: DELETE /domains/{domain}
        if path.startswith('/domains/') and http_method == 'DELETE':
            print("Handling individual domain delete request")
            response = handle_delete_domain(event, user_id)
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