import json
from datetime import datetime

def lambda_handler(event, context):
    """
    API Gateway Lambda handler (in lambda directory)
    Note: The main API handler is in lambdas/api_handler/lambda_function.py
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'API handler executed successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
    } 