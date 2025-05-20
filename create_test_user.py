import boto3
import jwt
import time
from datetime import datetime, timedelta, timezone

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('dashora-users-v2')

# JWT secret from the deployment
JWT_SECRET = 'da5h0raAn4lyt1csS3cretK3y2024Pr0duct10n'

def create_test_user():
    try:
        # Create a test user with access to example.com
        user_id = 'test-user'
        users_table.put_item(
            Item={
                'user_id': user_id,
                'domains': ['example.com'],
                'created_at': int(time.time())
            }
        )
        print("Test user created successfully")
        
        # Generate JWT token with proper claims
        payload = {
            'user_id': user_id,
            'exp': int((datetime.now(timezone.utc) + timedelta(days=1)).timestamp()),
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'sub': user_id
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        print("\nJWT Token details:")
        print("-" * 50)
        print("Token:", token)
        print("\nFor testing, use this curl command:")
        print("-" * 50)
        print(f"curl -H 'Authorization: Bearer {token}' https://2or9i88vmc.execute-api.us-east-1.amazonaws.com/prod/domains")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    create_test_user() 