import json
import os
from datetime import datetime, timedelta
import boto3
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension
)
from google.oauth2 import service_account
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

def get_analytics_metrics(domain, credentials):
    """Fetch metrics from Google Analytics 4"""
    # Initialize GA4 client
    credentials_info = json.loads(credentials['service_account_key'])
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )
    
    client = BetaAnalyticsDataClient(credentials=credentials)
    property_id = credentials['property_id']
    
    # Set date range for last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate")
        ],
        dimensions=[
            Dimension(name="date")
        ]
    )
    
    response = client.run_report(request)
    
    # Process the response
    total_users = 0
    total_page_views = 0
    avg_session_duration = 0
    bounce_rate = 0
    
    for row in response.rows:
        total_users += int(row.metric_values[0].value)
        total_page_views += int(row.metric_values[1].value)
        avg_session_duration += float(row.metric_values[2].value)
        bounce_rate += float(row.metric_values[3].value)
    
    num_days = len(response.rows) or 1
    
    metrics = {
        'domain': domain,
        'timestamp': int(datetime.utcnow().timestamp()),
        'active_users': total_users,
        'page_views': total_page_views,
        'avg_session_duration': avg_session_duration / num_days,
        'bounce_rate': bounce_rate / num_days,
        'data_source': 'google_analytics',
        'expiry_time': int((datetime.utcnow() + timedelta(days=90)).timestamp())
    }
    
    return metrics

def lambda_handler(event, context):
    """Lambda handler for Google Analytics metrics fetcher"""
    try:
        # Get domains from event or environment
        domains = event.get('domains', os.environ.get('DOMAINS', '').split(','))
        
        all_metrics = []
        for domain in domains:
            # Get credentials from Secrets Manager
            secret_name = f"/dashora/google-analytics/{domain}"
            credentials = get_secret(secret_name)
            
            if not credentials:
                print(f"No credentials found for domain: {domain}")
                continue
                
            metrics = get_analytics_metrics(domain, credentials)
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
                'message': f'Successfully fetched GA metrics for {len(all_metrics)} domains',
                'domains_processed': domains
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        # Send alert to SNS
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['ALERT_TOPIC_ARN'],
            Subject=f'Google Analytics Metrics Fetcher Error',
            Message=f'Error fetching GA metrics: {str(e)}'
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 