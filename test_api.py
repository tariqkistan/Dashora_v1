import requests
import json

# API configuration
API_BASE_URL = 'https://2or9i88vmc.execute-api.us-east-1.amazonaws.com/prod'
JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzQ3NzUwODQ0LCJpYXQiOjE3NDc2NjQ0NDQsInN1YiI6InRlc3QtdXNlciJ9.PBP5BKXyUlgwVE7jLlHC-dfrKRPNA4Ch47nKYzC-1xs'

def test_endpoints():
    # Headers with JWT token
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints
    endpoints = ['/', '/domains']
    
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
    
    # Test metrics endpoint with different time ranges
    test_metrics_endpoint(headers)

def test_metrics_endpoint(headers):
    # First get the domains
    try:
        response = requests.get(f"{API_BASE_URL}/domains", headers=headers)
        domains = response.json().get('domains', [])
        
        if not domains:
            print("\nNo domains found to test metrics endpoint")
            return
        
        # Test metrics for first domain with different time ranges
        domain = domains[0]['domain']
        time_ranges = [7, 30]  # Test 7 days and 30 days
        
        for days in time_ranges:
            print(f"\nTesting metrics endpoint for domain {domain} with {days} days")
            print("-" * 50)
            
            try:
                response = requests.get(
                    f"{API_BASE_URL}/metrics/{domain}",
                    params={'days': days},
                    headers=headers
                )
                print(f"Status code: {response.status_code}")
                print("Response headers:", json.dumps(dict(response.headers), indent=2))
                print("Response body:", json.dumps(response.json(), indent=2))
                
            except Exception as e:
                print(f"Error: {str(e)}")
    
    except Exception as e:
        print(f"Error getting domains: {str(e)}")

if __name__ == '__main__':
    test_endpoints() 