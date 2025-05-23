#!/usr/bin/env python3

import jwt
import time
import json

# Use the same JWT secret as in the Lambda
JWT_SECRET = "dashora_secret_jwt_1509517567"
JWT_EXPIRATION = 3600  # 1 hour in seconds

def test_jwt_generation_and_verification():
    """Test JWT token generation and verification"""
    print("Testing JWT token generation and verification...")
    
    # Generate JWT token
    now = int(time.time())
    token_payload = {
        'user_id': 'test-user',
        'email': 'test@example.com',
        'iat': now,
        'exp': now + JWT_EXPIRATION
    }
    
    print(f"Creating token with payload: {json.dumps(token_payload)}")
    print(f"Using JWT_SECRET: {JWT_SECRET[:3]}...{JWT_SECRET[-3:]} (length: {len(JWT_SECRET)})")
    
    try:
        # Generate token
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
        print(f"Token generated successfully: {token[:20]}...")
        
        # Verify token format
        token_parts = token.split('.')
        print(f"Token parts count: {len(token_parts)}")
        print(f"Token parts: header={token_parts[0][:10]}..., payload={token_parts[1][:10]}..., signature={token_parts[2][:10]}...")
        
        # Verify token
        decoded_payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(f"Token decoded successfully: {decoded_payload}")
        
        # Test with Bearer format
        bearer_token = f"Bearer {token}"
        print(f"Bearer token: {bearer_token[:30]}...")
        
        # Extract token from Bearer format
        if bearer_token.startswith('Bearer '):
            extracted_token = bearer_token.split(' ')[1]
            print(f"Extracted token: {extracted_token[:20]}...")
            
            # Verify extracted token
            decoded_extracted = jwt.decode(extracted_token, JWT_SECRET, algorithms=['HS256'])
            print(f"Extracted token decoded successfully: {decoded_extracted}")
        
        print("✅ JWT test passed!")
        return True
        
    except Exception as e:
        print(f"❌ JWT test failed: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_jwt_generation_and_verification() 