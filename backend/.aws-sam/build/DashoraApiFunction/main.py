import json
import os
import boto3
from decimal import Decimal
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

def get_metrics(domain=None, start_time=None, end_time=None, data_source=None):
    """Retrieve metrics from DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    # If no time range specified, default to last 30 days
    if not end_time:
        end_time = int(datetime.utcnow().timestamp())
    if not start_time:
        start_time = int((datetime.utcnow() - timedelta(days=30)).timestamp())
    
    try:
        if domain:
            # Query by domain and time range
            response = table.query(
                KeyConditionExpression=Key('domain').eq(domain) & 
                                     Key('timestamp').between(start_time, end_time)
            )
        else:
            # Use GSI to query by time range across all domains
            response = table.query(
                IndexName='timestamp-index',
                KeyConditionExpression=Key('timestamp').between(start_time, end_time)
            )
        
        items = response['Items']
        
        # Filter by data source if specified
        if data_source:
            items = [item for item in items if item['data_source'] == data_source]
        
        return items
        
    except ClientError as e:
        print(f"Error querying DynamoDB: {str(e)}")
        raise

def lambda_handler(event, context):
    """Lambda handler for serving metrics via API Gateway"""
    try:
        # Get query parameters
        params = event.get('queryStringParameters', {}) or {}
        domain = params.get('domain')
        data_source = params.get('data_source')
        
        # Parse time range if provided
        try:
            start_time = int(params.get('start_time', ''))
        except (ValueError, TypeError):
            start_time = None
            
        try:
            end_time = int(params.get('end_time', ''))
        except (ValueError, TypeError):
            end_time = None
        
        # Get metrics
        metrics = get_metrics(
            domain=domain,
            start_time=start_time,
            end_time=end_time,
            data_source=data_source
        )
        
        # Convert Decimal to float for JSON serialization
        def decimal_to_float(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            return obj
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'metrics': metrics
            }, default=decimal_to_float)
        }
        
    except Exception as e:
        print(f"Error in API handler: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'error': str(e)
            })
        } 