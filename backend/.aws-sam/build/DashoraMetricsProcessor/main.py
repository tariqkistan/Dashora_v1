import json
import os
import boto3
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

def process_metrics(metrics):
    """Process and validate metrics before storing"""
    # Convert float values to Decimal for DynamoDB
    processed = {}
    for key, value in metrics.items():
        if isinstance(value, float):
            processed[key] = Decimal(str(value))
        else:
            processed[key] = value
    
    # Ensure required fields
    required_fields = ['domain', 'timestamp', 'data_source']
    for field in required_fields:
        if field not in processed:
            raise ValueError(f"Missing required field: {field}")
    
    return processed

def store_metrics(metrics):
    """Store metrics in DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    try:
        response = table.put_item(Item=metrics)
        return response
    except ClientError as e:
        print(f"Error storing metrics in DynamoDB: {str(e)}")
        raise

def lambda_handler(event, context):
    """Lambda handler for processing metrics from SQS and storing in DynamoDB"""
    try:
        processed_records = 0
        failed_records = 0
        
        # Process each record from SQS
        for record in event['Records']:
            try:
                # Parse message body
                message_body = json.loads(record['body'])
                
                # Process metrics
                processed_metrics = process_metrics(message_body)
                
                # Store in DynamoDB
                store_metrics(processed_metrics)
                
                processed_records += 1
                
            except Exception as e:
                print(f"Error processing record: {str(e)}")
                failed_records += 1
                
                # Send alert for failed record
                sns = boto3.client('sns')
                sns.publish(
                    TopicArn=os.environ['ALERT_TOPIC_ARN'],
                    Subject=f'Metrics Processing Error',
                    Message=f'Error processing metrics record: {str(e)}\nRecord: {record["body"]}'
                )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Metrics processing complete',
                'processed_records': processed_records,
                'failed_records': failed_records
            })
        }
        
    except Exception as e:
        print(f"Error in metrics processor: {str(e)}")
        
        # Send alert for general failure
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['ALERT_TOPIC_ARN'],
            Subject=f'Metrics Processor General Error',
            Message=f'Error in metrics processor: {str(e)}'
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 