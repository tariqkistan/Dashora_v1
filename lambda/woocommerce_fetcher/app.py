import json
import os
import boto3
import requests
from datetime import datetime, timedelta
from base64 import b64encode

# Environment variables
DOMAINS_TABLE_NAME = os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
domains_table = dynamodb.Table(DOMAINS_TABLE_NAME)

def lambda_handler(event, context):
    """
    Fetches WooCommerce data for all domains registered in the DynamoDB domains table.
    This function is triggered on a schedule (e.g., hourly).
    """
    try:
        # Get all domains with WooCommerce configuration
        response = domains_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('woocommerce_config').exists()
        )
        
        domains = response.get('Items', [])
        results = []
        
        for domain in domains:
            try:
                # Extract WooCommerce credentials and settings
                wc_config = domain.get('woocommerce_config', {})
                domain_name = domain.get('domain_id')
                
                if not wc_config or not domain_name:
                    continue
                
                # Extract WooCommerce API credentials
                api_url = wc_config.get('api_url')
                consumer_key = wc_config.get('consumer_key')
                consumer_secret = wc_config.get('consumer_secret')
                
                if not all([api_url, consumer_key, consumer_secret]):
                    print(f"Incomplete WooCommerce configuration for domain: {domain_name}")
                    continue
                
                # Get sales data for past day
                yesterday = datetime.utcnow() - timedelta(days=1)
                yesterday_str = yesterday.strftime('%Y-%m-%dT00:00:00')
                
                # Fetch orders data from WooCommerce API
                orders_url = f"{api_url}/wp-json/wc/v3/orders"
                auth_string = b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
                
                params = {
                    'after': yesterday_str,
                    'per_page': 100
                }
                
                headers = {
                    'Authorization': f'Basic {auth_string}'
                }
                
                response = requests.get(orders_url, params=params, headers=headers)
                response.raise_for_status()
                
                orders = response.json()
                
                # Calculate metrics
                total_sales = sum(float(order.get('total', 0)) for order in orders)
                order_count = len(orders)
                
                # Get product data
                products_url = f"{api_url}/wp-json/wc/v3/products"
                response = requests.get(products_url, params={'per_page': 100}, headers=headers)
                response.raise_for_status()
                
                products = response.json()
                
                # Prepare WooCommerce metrics data
                wc_data = {
                    'domain_id': domain_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'woocommerce': {
                        'total_sales': total_sales,
                        'order_count': order_count,
                        'average_order_value': total_sales / order_count if order_count > 0 else 0,
                        'product_count': len(products)
                    }
                }
                
                results.append(wc_data)
                print(f"Successfully fetched WooCommerce data for {domain_name}")
                
            except Exception as e:
                print(f"Error fetching WooCommerce data for domain {domain.get('domain_id')}: {str(e)}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Successfully processed {len(results)} domains",
                'data': results
            })
        }
        
    except Exception as e:
        print(f"Error in WooCommerce fetcher: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error in WooCommerce fetcher: {str(e)}"
            })
        } 