import requests
import json

# API configuration
API_BASE_URL = 'http://localhost:5000'
JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzQ3NzUxMTA5LCJpYXQiOjE3NDc2NjQ3MDksInN1YiI6InRlc3QtdXNlciJ9.5hL4f07L0R65CYaAW2rQtvsCfQ6MWgqrBQzXhav3mQw'

def test_endpoints():
    # Headers with JWT token
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints
    endpoints = ['/', '/domains', '/metrics/example.com']
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        print("-" * 50)
        
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
            print(f"Status code: {response.status_code}")
            print("Response headers:", json.dumps(dict(response.headers), indent=2))
            print("Response body:", json.dumps(response.json(), indent=2))
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_endpoints() 