import json
import os
import boto3
from datetime import datetime, timedelta

# Environment variables
METRICS_TABLE_NAME = os.environ.get('METRICS_TABLE_NAME', 'dashora-metrics')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
metrics_table = dynamodb.Table(METRICS_TABLE_NAME)

def lambda_handler(event, context):
    """
    Processes and combines metrics data from WooCommerce and Google Analytics.
    This function is triggered when new data is available from the fetcher functions.
    """
    try:
        # Check if event is from CloudWatch Events
        if 'detail' in event and 'responsePayload' in event['detail']:
            # Extract the payload from the event
            fetcher_response = event['detail']['responsePayload']
            if 'body' in fetcher_response:
                # Parse the body from the fetcher response
                body = json.loads(fetcher_response['body'])
                metrics_data = body.get('data', [])
            else:
                metrics_data = []
        # Direct invocation with test data
        elif 'data' in event:
            metrics_data = event['data']
        else:
            metrics_data = []

        if not metrics_data:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': "No metrics data to process"
                })
            }

        processed_count = 0
        for metric in metrics_data:
            try:
                domain_id = metric.get('domain_id')
                timestamp = metric.get('timestamp')
                
                if not domain_id or not timestamp:
                    continue
                
                # Get existing metrics for this domain/timestamp if they exist
                try:
                    response = metrics_table.get_item(
                        Key={
                            'domain_id': domain_id,
                            'timestamp': timestamp
                        }
                    )
                    existing_item = response.get('Item', {})
                except Exception:
                    existing_item = {}
                
                # Merge the new metrics with existing data
                updated_item = {**existing_item, **metric}
                
                # Calculate combined metrics if we have both data sources
                if 'woocommerce' in updated_item and 'google_analytics' in updated_item:
                    wc_data = updated_item['woocommerce']
                    ga_data = updated_item['google_analytics']
                    
                    # Create combined metrics
                    combined_metrics = {
                        'conversion_rate': (ga_data.get('conversions', 0) / ga_data.get('sessions', 1)) if ga_data.get('sessions', 0) > 0 else 0,
                        'revenue_per_session': (wc_data.get('total_sales', 0) / ga_data.get('sessions', 1)) if ga_data.get('sessions', 0) > 0 else 0,
                        'revenue_per_user': (wc_data.get('total_sales', 0) / ga_data.get('activeUsers', 1)) if ga_data.get('activeUsers', 0) > 0 else 0
                    }
                    
                    updated_item['combined_metrics'] = combined_metrics
                
                # Store the updated metrics in DynamoDB
                metrics_table.put_item(Item=updated_item)
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing metrics for domain {metric.get('domain_id')}: {str(e)}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Successfully processed metrics for {processed_count} domains"
            })
        }
        
    except Exception as e:
        print(f"Error in metrics processor: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error in metrics processor: {str(e)}"
            })
        } 