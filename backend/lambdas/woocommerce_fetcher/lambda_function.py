import json
import os
import boto3
from datetime import datetime, timedelta
from woocommerce import API

# Set AWS region if not already set
if 'AWS_REGION' not in os.environ:
    os.environ['AWS_REGION'] = 'us-east-1'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics'))

# Initialize Secrets Manager client
secrets_client = boto3.client('secretsmanager')

def get_woocommerce_credentials(domain):
    """Retrieve WooCommerce API credentials from AWS Secrets Manager"""
    secret_name = f"dashora/woocommerce/{domain}"
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return {
            'url': f"https://{domain}",
            'consumer_key': secret['consumer_key'],
            'consumer_secret': secret['consumer_secret'],
            'version': 'wc/v3'
        }
    except Exception as e:
        print(f"Error retrieving WooCommerce credentials: {str(e)}")
        raise

def get_woocommerce_data(domain, start_date, end_date):
    """Fetch data from WooCommerce API"""
    credentials = get_woocommerce_credentials(domain)
    
    # Initialize WooCommerce API client
    wcapi = API(
        url=credentials['url'],
        consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        version=credentials['version']
    )
    
    # Fetch orders
    orders_params = {
        'after': start_date.isoformat(),
        'before': end_date.isoformat(),
        'per_page': 100  # Maximum allowed by WooCommerce API
    }
    orders = wcapi.get("orders", params=orders_params).json()
    
    # Calculate metrics
    total_sales = sum(float(order.get('total', 0)) for order in orders)
    total_orders = len(orders)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Get product data for top products
    products_params = {
        'orderby': 'popularity',
        'order': 'desc',
        'per_page': 5
    }
    top_products = wcapi.get("products", params=products_params).json()
    
    return {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'top_products': [
            {
                'id': product.get('id'),
                'name': product.get('name'),
                'price': product.get('price'),
                'sales': product.get('total_sales', 0)
            }
            for product in top_products
        ]
    }

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
        
        # Fetch WooCommerce data
        woocommerce_data = get_woocommerce_data(domain, start_date, end_date)
        
        # Store metrics in DynamoDB
        timestamp = int(datetime.now().timestamp())
        table.put_item(
            Item={
                'domain': domain,
                'timestamp': timestamp,
                'source': 'woocommerce',
                'metrics': woocommerce_data,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'ttl': int((datetime.now() + timedelta(days=90)).timestamp())
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'domain': domain,
                'timestamp': timestamp,
                'metrics': woocommerce_data
            })
        }
    
    except Exception as e:
        print(f"Error processing WooCommerce data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 