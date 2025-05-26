import json
import os
import boto3
from datetime import datetime, timedelta
import requests
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# DynamoDB table names
METRICS_TABLE = os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics-api')
DOMAINS_TABLE = os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains-api')

print(f"Lambda loading with METRICS_TABLE={METRICS_TABLE}, DOMAINS_TABLE={DOMAINS_TABLE}")

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
metrics_table = dynamodb.Table(METRICS_TABLE)
domains_table = dynamodb.Table(DOMAINS_TABLE)

# Helper function to convert floats to Decimal for DynamoDB
def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(x) for x in obj]
    else:
        return obj

def get_domain_credentials(domain_id):
    """Retrieve domain credentials from DynamoDB"""
    try:
        # First try to get the domain directly
        print(f"Looking up domain: {domain_id}")
        
        # Try different user_ids in case it's not found
        user_ids = ['test-user']
        
        for user_id in user_ids:
            try:
                print(f"Trying with user_id: {user_id}")
                print(f"Looking for key: user_id={user_id}, domain_id={domain_id}")
                
                response = domains_table.get_item(
                    Key={
                        'user_id': user_id,
                        'domain_id': domain_id
                    }
                )
                
                print(f"Response from get_item: {json.dumps(response, default=str)}")
                
                if 'Item' in response:
                    domain_data = response['Item']
                    print(f"Found domain record: {domain_id}")
                    print(f"Domain data: {json.dumps(domain_data, default=str)}")
                    return {
                        'url': f"https://{domain_id}",
                        'wc_consumer_key': domain_data.get('wc_consumer_key'),
                        'wc_consumer_secret': domain_data.get('wc_consumer_secret')
                    }
                else:
                    print(f"No Item found in response for user_id={user_id}, domain_id={domain_id}")
            except Exception as e:
                print(f"Error with get_item for user_id {user_id}: {str(e)}")
                print(f"Exception type: {type(e)}")
                import traceback
                print(traceback.format_exc())
        
        # If not found with direct lookup, fall back to scan
        print(f"Domain not found with direct lookup, trying scan")
        scan_response = domains_table.scan(
            FilterExpression=Key('domain_id').eq(domain_id)
        )
        
        print(f"Scan response count: {scan_response.get('Count', 0)}")
        
        if scan_response['Count'] > 0:
            domain_data = scan_response['Items'][0]
            print(f"Found domain with scan: {domain_id}")
            print(f"Domain data from scan: {json.dumps(domain_data, default=str)}")
            return {
                'url': f"https://{domain_id}",
                'wc_consumer_key': domain_data.get('wc_consumer_key'),
                'wc_consumer_secret': domain_data.get('wc_consumer_secret')
            }
        
            print(f"No credentials found for domain: {domain_id}")
            # For development, return mock credentials
            if os.environ.get('STAGE') == 'dev':
                print("Using mock credentials in development mode")
                return {
                    'url': f"https://{domain_id}",
                    'wc_consumer_key': 'mock_consumer_key',
                    'wc_consumer_secret': 'mock_consumer_secret'
                }
            return None
        
    except Exception as e:
        print(f"Error retrieving domain credentials: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

def fetch_woocommerce_orders(domain, credentials, start_date, end_date):
    """Fetch orders from WooCommerce API"""
    url = f"{credentials['url']}/wp-json/wc/v3/orders"
    
    # Parameters for WooCommerce API
    params = {
        'after': start_date.isoformat(),
        'before': end_date.isoformat(),
        'per_page': 100  # Maximum allowed by WooCommerce API
    }
    
    # Authentication
    auth = (credentials['wc_consumer_key'], credentials['wc_consumer_secret'])
    
    try:
        # Make the API request
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching WooCommerce orders: {str(e)}")
        
        # In development mode, return mock data
        if os.environ.get('STAGE') == 'dev':
            print("Using mock order data in development mode")
            return generate_mock_orders(start_date, end_date)
        raise

def fetch_woocommerce_products(domain, credentials, limit=5):
    """Fetch popular products from WooCommerce API"""
    url = f"{credentials['url']}/wp-json/wc/v3/products"
    
    # Parameters for WooCommerce API
    params = {
        'orderby': 'popularity',
        'order': 'desc',
        'per_page': limit
    }
    
    # Authentication
    auth = (credentials['wc_consumer_key'], credentials['wc_consumer_secret'])
    
    try:
        # Make the API request
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching WooCommerce products: {str(e)}")
        
        # In development mode, return mock data
        if os.environ.get('STAGE') == 'dev':
            print("Using mock product data in development mode")
            return generate_mock_products(limit)
        raise

def generate_mock_orders(start_date, end_date):
    """Generate mock order data for development/testing"""
    import random
    
    days_diff = (end_date - start_date).days
    orders = []
    
    for i in range(random.randint(20, 50)):  # Random number of orders
        # Random date within range
        order_date = start_date + timedelta(days=random.randint(0, days_diff))
        
        # Random order total between $20 and $200
        order_total = round(random.uniform(20, 200), 2)
        
        orders.append({
            'id': i + 1000,
            'date_created': order_date.isoformat(),
            'total': str(order_total),
            'status': random.choice(['completed', 'processing', 'on-hold']),
            'currency': 'USD'
        })
    
    return orders

def generate_mock_products(limit=5):
    """Generate mock product data for development/testing"""
    products = [
        {
            'id': 101,
            'name': 'Premium T-Shirt',
            'price': '29.99',
            'total_sales': 156
        },
        {
            'id': 102,
            'name': 'Slim Fit Jeans',
            'price': '49.99',
            'total_sales': 132
        },
        {
            'id': 103,
            'name': 'Winter Jacket',
            'price': '89.99',
            'total_sales': 89
        },
        {
            'id': 104,
            'name': 'Running Shoes',
            'price': '79.99',
            'total_sales': 76
        },
        {
            'id': 105,
            'name': 'Smartwatch',
            'price': '199.99',
            'total_sales': 65
        }
    ]
    
    return products[:limit]

def calculate_metrics(orders, products):
    """Calculate metrics from WooCommerce data"""
    # Calculate sales metrics
    total_orders = len(orders)
    total_sales = sum(float(order.get('total', 0)) for order in orders)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Format top products data
    top_products = [
        {
            'id': product.get('id'),
            'name': product.get('name'),
            'price': product.get('price'),
            'sales': product.get('total_sales', 0)
        }
        for product in products
    ]
    
    # Convert the metrics to Decimal for DynamoDB
    return {
        'total_sales': Decimal(str(total_sales)),
        'total_orders': total_orders,  # Integer, no conversion needed
        'avg_order_value': Decimal(str(avg_order_value)),
        'top_products': float_to_decimal(top_products)
    }

def lambda_handler(event, context):
    """Lambda function handler"""
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Check if it's a scheduled event or direct invocation
        if 'domain' in event:
            domains = [event['domain']]
        else:
            # Scheduled event - process all domains with WooCommerce enabled
            print("Scheduled event - processing all domains with WooCommerce enabled")
            response = domains_table.scan(
                FilterExpression=Key('woocommerce_enabled').eq(True)
            )
            domains = [item['domain_id'] for item in response.get('Items', [])]
            
            # In development mode, use mock domains if none found
            if not domains and os.environ.get('STAGE') == 'dev':
                print("No domains found, using mock domains in development mode")
                domains = ['example.com', 'test-store.com']
        
        print(f"Processing domains: {domains}")
        results = []
        
        for domain in domains:
            try:
                # Calculate date range (last 7 days by default)
                days = int(event.get('days', 7)) if 'days' in event else 7
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                print(f"Fetching data for domain {domain} from {start_date} to {end_date}")
                
                # Get domain credentials
                credentials = get_domain_credentials(domain)
                if not credentials:
                    print(f"Skipping domain {domain} - no credentials found")
                    continue
                
                # Fetch WooCommerce data
                orders = fetch_woocommerce_orders(domain, credentials, start_date, end_date)
                products = fetch_woocommerce_products(domain, credentials)
                
                # Calculate metrics
                metrics = calculate_metrics(orders, products)
                
                # Store metrics in DynamoDB
                timestamp = int(datetime.now().timestamp())
                metrics_table.put_item(
                    Item={
                        'domain_id': domain,
                        'timestamp': str(timestamp),
                        'source': 'woocommerce',
                        'pageviews': 0,  # Will be updated by GA fetcher
                        'visitors': 0,   # Will be updated by GA fetcher
                        'orders': metrics['total_orders'],
                        'revenue': metrics['total_sales'],
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'wc_data': {
                            'avg_order_value': metrics['avg_order_value'],
                            'top_products': metrics['top_products']
                        },
                        'ttl': int((datetime.now() + timedelta(days=90)).timestamp())
                    }
                )
                
                result = {
                    'domain': domain,
                    'timestamp': timestamp,
                    'metrics': json.loads(json.dumps(metrics, default=str))  # Convert Decimal to string for JSON
                }
                results.append(result)
                print(f"Successfully processed domain {domain}")
            
            except Exception as e:
                print(f"Error processing domain {domain}: {str(e)}")
                # Continue processing other domains
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Processed {len(results)} domains",
                'results': results
            }, default=str)  # Use default=str to handle Decimal serialization
        }
    
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 