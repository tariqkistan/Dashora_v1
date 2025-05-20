import json
import os
import boto3
from datetime import datetime, timedelta

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
metrics_table = dynamodb.Table(os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics'))
domains_table = dynamodb.Table(os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains'))

def get_domain_config(domain):
    """Retrieve domain configuration from the domains table"""
    try:
        response = domains_table.get_item(
            Key={
                'domain': domain
            }
        )
        return response.get('Item')
    except Exception as e:
        print(f"Error retrieving domain configuration: {str(e)}")
        return None

def get_latest_metrics(domain, source, days=7):
    """Retrieve the latest metrics for a domain and source"""
    try:
        # Calculate time range
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Query the metrics table
        response = metrics_table.query(
            KeyConditionExpression='domain = :domain AND timestamp BETWEEN :start_time AND :end_time',
            FilterExpression='source = :source',
            ExpressionAttributeValues={
                ':domain': domain,
                ':start_time': start_time,
                ':end_time': end_time,
                ':source': source
            },
            ScanIndexForward=False,  # Sort in descending order (newest first)
            Limit=1
        )
        
        if response.get('Items'):
            return response['Items'][0]
        return None
    except Exception as e:
        print(f"Error retrieving latest metrics: {str(e)}")
        return None

def compute_combined_metrics(domain, woocommerce_metrics, ga_metrics):
    """Compute combined metrics from WooCommerce and Google Analytics data"""
    combined = {
        'domain': domain,
        'timestamp': int(datetime.now().timestamp()),
        'woocommerce': woocommerce_metrics.get('metrics', {}) if woocommerce_metrics else {},
        'google_analytics': ga_metrics.get('metrics', {}) if ga_metrics else {},
        'combined': {}
    }
    
    # Calculate combined e-commerce metrics
    wc_data = combined['woocommerce']
    ga_data = combined['google_analytics']
    
    # Basic combined metrics
    combined['combined'] = {
        'total_revenue': wc_data.get('total_sales', 0),
        'total_orders': wc_data.get('total_orders', 0),
        'avg_order_value': wc_data.get('avg_order_value', 0),
        'total_users': ga_data.get('total_users', 0),
        'total_sessions': ga_data.get('total_sessions', 0),
        'total_page_views': ga_data.get('total_page_views', 0),
        'conversion_rate': 0,
        'top_products': wc_data.get('top_products', []),
        'traffic_by_device': ga_data.get('by_device', {}),
        'traffic_by_country': ga_data.get('by_country', {}),
        'trend_data': {}
    }
    
    # Calculate conversion rate
    if ga_data.get('total_sessions', 0) > 0:
        conversion_rate = (wc_data.get('total_orders', 0) / ga_data.get('total_sessions', 0)) * 100
        combined['combined']['conversion_rate'] = round(conversion_rate, 2)
    
    # Add time-series data if available
    if ga_data.get('by_date') and isinstance(ga_data['by_date'], dict):
        combined['combined']['trend_data'] = ga_data['by_date']
    
    return combined

def store_combined_metrics(combined_metrics):
    """Store the combined metrics in DynamoDB"""
    try:
        metrics_table.put_item(
            Item={
                'domain': combined_metrics['domain'],
                'timestamp': combined_metrics['timestamp'],
                'source': 'combined',
                'metrics': combined_metrics['combined'],
                'woocommerce': combined_metrics['woocommerce'],
                'google_analytics': combined_metrics['google_analytics'],
                'ttl': int((datetime.now() + timedelta(days=90)).timestamp())
            }
        )
        return True
    except Exception as e:
        print(f"Error storing combined metrics: {str(e)}")
        return False

def lambda_handler(event, context):
    """Lambda function handler"""
    try:
        # Extract domain from the event
        domain = event.get('domain')
        days = int(event.get('days', 7))
        
        if not domain:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Domain parameter is required'})
            }
        
        # Get domain configuration
        domain_config = get_domain_config(domain)
        if not domain_config:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Domain {domain} not configured'})
            }
        
        # Get latest metrics for WooCommerce and Google Analytics
        woocommerce_metrics = get_latest_metrics(domain, 'woocommerce', days)
        ga_metrics = get_latest_metrics(domain, 'google_analytics', days)
        
        # Compute combined metrics
        combined_metrics = compute_combined_metrics(domain, woocommerce_metrics, ga_metrics)
        
        # Store combined metrics
        success = store_combined_metrics(combined_metrics)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'domain': domain,
                'timestamp': combined_metrics['timestamp'],
                'success': success,
                'metrics': combined_metrics['combined']
            })
        }
    
    except Exception as e:
        print(f"Error processing metrics: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 