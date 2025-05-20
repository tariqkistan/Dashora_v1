import boto3
import time
from datetime import datetime, timedelta

# Initialize CloudWatch Logs client
logs = boto3.client('logs', region_name='us-east-1')

def get_lambda_logs(function_name, start_time=None):
    if not start_time:
        start_time = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)
    
    try:
        # Get the log group name for the Lambda function
        log_group_name = f'/aws/lambda/dashora-analytics-{function_name}-UzoUPJ1SHWx4'
        print(f"Checking log group: {log_group_name}")
        
        # List all log groups to debug
        log_groups = logs.describe_log_groups()
        print("\nAvailable log groups:")
        for group in log_groups['logGroups']:
            print(group['logGroupName'])
        
        # Get log streams
        streams = logs.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not streams.get('logStreams'):
            print(f"No log streams found for {function_name}")
            return
        
        # Get logs from the most recent stream
        stream_name = streams['logStreams'][0]['logStreamName']
        logs_response = logs.get_log_events(
            logGroupName=log_group_name,
            logStreamName=stream_name,
            startTime=start_time,
            limit=100
        )
        
        print(f"\nRecent logs for {function_name}:")
        print("-" * 80)
        
        for event in logs_response['events']:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            print(f"{timestamp}: {event['message']}")
            
    except Exception as e:
        print(f"Error getting logs: {str(e)}")

if __name__ == '__main__':
    # Get logs for the API function
    get_lambda_logs('ApiFunction') 