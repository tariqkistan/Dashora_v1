import json
import os
import boto3
import time
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest
)
from google.oauth2 import service_account

# Environment variables
DOMAINS_TABLE_NAME = os.environ.get('DOMAINS_TABLE_NAME', 'dashora-domains')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
domains_table = dynamodb.Table(DOMAINS_TABLE_NAME)

def create_ga_client(service_account_info):
    """Creates a Google Analytics client from service account info"""
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    return BetaAnalyticsDataClient(credentials=credentials)

def lambda_handler(event, context):
    """
    Fetches Google Analytics data for all domains registered in the DynamoDB domains table.
    This function is triggered on a schedule (e.g., hourly).
    """
    try:
        # Get all domains with Google Analytics configuration
        response = domains_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('ga_config').exists()
        )
        
        domains = response.get('Items', [])
        results = []
        
        for domain in domains:
            try:
                # Extract Google Analytics credentials and settings
                ga_config = domain.get('ga_config', {})
                domain_name = domain.get('domain_id')
                
                if not ga_config or not domain_name:
                    continue
                
                # Extract Google Analytics configuration
                property_id = ga_config.get('property_id')
                service_account_info = ga_config.get('service_account_info')
                
                if not property_id or not service_account_info:
                    print(f"Incomplete Google Analytics configuration for domain: {domain_name}")
                    continue
                
                # Load service account info as JSON if it's a string
                if isinstance(service_account_info, str):
                    service_account_info = json.loads(service_account_info)
                
                # Initialize Google Analytics client
                client = create_ga_client(service_account_info)
                
                # Set date range for past day
                yesterday = datetime.utcnow() - timedelta(days=1)
                yesterday_str = yesterday.strftime('%Y-%m-%d')
                
                # Create report request for key metrics
                request = RunReportRequest(
                    property=f"properties/{property_id}",
                    dimensions=[
                        Dimension(name="date")
                    ],
                    metrics=[
                        Metric(name="activeUsers"),
                        Metric(name="sessions"),
                        Metric(name="engagedSessions"),
                        Metric(name="averageSessionDuration"),
                        Metric(name="screenPageViews"),
                        Metric(name="conversions")
                    ],
                    date_ranges=[
                        DateRange(start_date=yesterday_str, end_date=yesterday_str)
                    ]
                )
                
                # Run the report
                response = client.run_report(request)
                
                # Process the response
                metrics_data = {}
                if response.rows:
                    row = response.rows[0]
                    for i, metric in enumerate(response.metric_headers):
                        metric_name = metric.name
                        metric_value = float(row.metric_values[i].value)
                        metrics_data[metric_name] = metric_value
                
                # Prepare Google Analytics metrics data
                ga_data = {
                    'domain_id': domain_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'google_analytics': metrics_data
                }
                
                results.append(ga_data)
                print(f"Successfully fetched Google Analytics data for {domain_name}")
                
                # Add a small delay to avoid API rate limits
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching GA data for domain {domain.get('domain_id')}: {str(e)}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Successfully processed {len(results)} domains",
                'data': results
            })
        }
        
    except Exception as e:
        print(f"Error in Google Analytics fetcher: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error in Google Analytics fetcher: {str(e)}"
            })
        } 