import json
import os
import boto3
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

# Set AWS region if not already set
if 'AWS_REGION' not in os.environ:
    os.environ['AWS_REGION'] = 'us-east-1'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics'))

# Initialize Secrets Manager client
secrets_client = boto3.client('secretsmanager')

def get_ga_credentials(domain):
    """Retrieve Google Analytics credentials from AWS Secrets Manager"""
    secret_name = f"dashora/google-analytics/{domain}"
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        # Store the service account key temporarily
        temp_key_file = '/tmp/ga_service_account.json'
        with open(temp_key_file, 'w') as f:
            json.dump(secret['service_account_key'], f)
            
        return {
            'property_id': secret['property_id'],
            'service_account_file': temp_key_file
        }
    except Exception as e:
        print(f"Error retrieving Google Analytics credentials: {str(e)}")
        raise

def get_analytics_data(domain, start_date, end_date):
    """Fetch data from Google Analytics Data API (GA4)"""
    credentials = get_ga_credentials(domain)
    
    # Create credentials from the service account file
    service_account_credentials = service_account.Credentials.from_service_account_file(
        credentials['service_account_file']
    )
    
    # Initialize Google Analytics Data API client
    client = BetaAnalyticsDataClient(credentials=service_account_credentials)
    
    # Define the request
    request = RunReportRequest(
        property=f"properties/{credentials['property_id']}",
        date_ranges=[
            DateRange(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
        ],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="deviceCategory"),
            Dimension(name="country")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="conversions"),
            Metric(name="totalRevenue")
        ]
    )
    
    # Run the report
    response = client.run_report(request)
    
    # Process the response
    metrics = {
        'total_users': 0,
        'total_sessions': 0,
        'total_page_views': 0,
        'total_conversions': 0,
        'total_revenue': 0,
        'by_date': {},
        'by_device': {},
        'by_country': {}
    }
    
    for row in response.rows:
        date_str = row.dimension_values[0].value
        device = row.dimension_values[1].value
        country = row.dimension_values[2].value
        
        users = int(row.metric_values[0].value)
        sessions = int(row.metric_values[1].value)
        page_views = int(row.metric_values[2].value)
        conversions = int(row.metric_values[3].value)
        revenue = float(row.metric_values[4].value)
        
        # Update totals
        metrics['total_users'] += users
        metrics['total_sessions'] += sessions
        metrics['total_page_views'] += page_views
        metrics['total_conversions'] += conversions
        metrics['total_revenue'] += revenue
        
        # Group by date
        if date_str not in metrics['by_date']:
            metrics['by_date'][date_str] = {
                'users': 0, 'sessions': 0, 'page_views': 0, 
                'conversions': 0, 'revenue': 0
            }
        metrics['by_date'][date_str]['users'] += users
        metrics['by_date'][date_str]['sessions'] += sessions
        metrics['by_date'][date_str]['page_views'] += page_views
        metrics['by_date'][date_str]['conversions'] += conversions
        metrics['by_date'][date_str]['revenue'] += revenue
        
        # Group by device
        if device not in metrics['by_device']:
            metrics['by_device'][device] = {
                'users': 0, 'sessions': 0, 'page_views': 0, 
                'conversions': 0, 'revenue': 0
            }
        metrics['by_device'][device]['users'] += users
        metrics['by_device'][device]['sessions'] += sessions
        metrics['by_device'][device]['page_views'] += page_views
        metrics['by_device'][device]['conversions'] += conversions
        metrics['by_device'][device]['revenue'] += revenue
        
        # Group by country
        if country not in metrics['by_country']:
            metrics['by_country'][country] = {
                'users': 0, 'sessions': 0, 'page_views': 0, 
                'conversions': 0, 'revenue': 0
            }
        metrics['by_country'][country]['users'] += users
        metrics['by_country'][country]['sessions'] += sessions
        metrics['by_country'][country]['page_views'] += page_views
        metrics['by_country'][country]['conversions'] += conversions
        metrics['by_country'][country]['revenue'] += revenue
    
    # Clean up temporary file
    if os.path.exists(credentials['service_account_file']):
        os.remove(credentials['service_account_file'])
    
    return metrics

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
        
        # Fetch Google Analytics data
        ga_data = get_analytics_data(domain, start_date, end_date)
        
        # Store metrics in DynamoDB
        timestamp = int(datetime.now().timestamp())
        table.put_item(
            Item={
                'domain': domain,
                'timestamp': timestamp,
                'source': 'google_analytics',
                'metrics': ga_data,
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
                'metrics': ga_data
            })
        }
    
    except Exception as e:
        print(f"Error processing Google Analytics data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 