import json
import os
import boto3
import requests
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])

def get_woocommerce_metrics(domain, api_key, api_secret):
    """Fetch metrics from WooCommerce API"""
    base_url = f"https://{domain}/wp-json/wc/v3"
    
    # Get current date and 30 days ago
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Fetch orders
    orders_response = requests.get(
        f"{base_url}/reports/sales",
        params={
            'date_min': start_date.isoformat(),
            'date_max': end_date.isoformat()
        },
        auth=(api_key, api_secret)
    )
    
    if orders_response.status_code != 200:
        raise Exception(f"Failed to fetch WooCommerce metrics: {orders_response.text}")
    
    orders_data = orders_response.json()
    
    # Fetch products
    products_response = requests.get(
        f"{base_url}/reports/products/totals",
        auth=(api_key, api_secret)
    )
    
    if products_response.status_code != 200:
        raise Exception(f"Failed to fetch products data: {products_response.text}")
    
    products_data = products_response.json()
    
    # Compile metrics
    metrics = {
        'domain': domain,
        'timestamp': int(datetime.utcnow().timestamp()),
        'total_sales': float(orders_data.get('total_sales', 0)),
        'average_order_value': float(orders_data.get('average_sales', 0)),
        'total_orders': int(orders_data.get('total_orders', 0)),
        'total_products': sum(item.get('total', 0) for item in products_data),
        'data_source': 'woocommerce',
        'expiry_time': int((datetime.utcnow() + timedelta(days=90)).timestamp())
    }
    
    return metrics

def lambda_handler(event, context):
    """Lambda handler for WooCommerce metrics fetcher"""
    try:
        # Get domains from event or environment
        domains = event.get('domains', os.environ.get('DOMAINS', '').split(','))
        
        all_metrics = []
        for domain in domains:
            # Get credentials from Secrets Manager
            secret_name = f"/dashora/woocommerce/{domain}"
            credentials = get_secret(secret_name)
            
            if not credentials:
                print(f"No credentials found for domain: {domain}")
                continue
                
            metrics = get_woocommerce_metrics(
                domain,
                credentials['api_key'],
                credentials['api_secret']
            )
            all_metrics.append(metrics)
        
        # Send metrics to SQS for processing
        sqs = boto3.client('sqs')
        queue_url = os.environ['METRICS_QUEUE_URL']
        
        for metrics in all_metrics:
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(metrics)
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully fetched metrics for {len(all_metrics)} domains',
                'domains_processed': domains
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        # Send alert to SNS
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['ALERT_TOPIC_ARN'],
            Subject=f'WooCommerce Metrics Fetcher Error',
            Message=f'Error fetching WooCommerce metrics: {str(e)}'
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 