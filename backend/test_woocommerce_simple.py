import requests
import sys
import json

def test_woocommerce(domain, consumer_key, consumer_secret):
    """Test WooCommerce API connection with basic checks"""
    
    # Print basic info
    print("Testing WooCommerce API connection:")
    print(f"  Domain: {domain}")
    print(f"  Consumer Key: {consumer_key[:4]}...{consumer_key[-4:]} (hidden middle part)")
    print(f"  Consumer Secret: {consumer_secret[:4]}...{consumer_secret[-4:]} (hidden middle part)")

    # First, test WordPress API availability
    wp_url = f"https://{domain}/wp-json/"
    print(f"\nTesting basic WordPress API: {wp_url}")
    
    try:
        wp_response = requests.get(wp_url, timeout=10)
        print(f"WordPress API status code: {wp_response.status_code}")
        
        if wp_response.status_code == 200:
            print("WordPress API is available!")
            
            # Try to find available routes
            data = wp_response.json()
            # Print first 5 available routes to help diagnose
            if 'routes' in data:
                print("\nSome available WordPress API routes:")
                routes = list(data['routes'].keys())[:5]
                for route in routes:
                    print(f"  {route}")
                
                # Look for WooCommerce routes
                wc_routes = [r for r in data['routes'].keys() if '/wc/' in r or '/woocommerce/' in r]
                if wc_routes:
                    print("\nFound WooCommerce API routes:")
                    for route in wc_routes[:5]:  # Show max 5 routes
                        print(f"  {route}")
        else:
            print(f"WordPress API error: {wp_response.text[:100]}...")
    except Exception as e:
        print(f"WordPress API error: {str(e)}")
    
    # Test different WooCommerce API versions
    versions = ["v3", "v2", "v1"]
    endpoints = ["products", "orders", "customers"]
    
    for version in versions:
        for endpoint in endpoints:
            url = f"https://{domain}/wp-json/wc/{version}/{endpoint}"
            
            print(f"\nTrying WooCommerce API: {url}")
            
            # Authentication
            auth = (consumer_key, consumer_secret)
            
            # Parameters
            params = {
                'per_page': 2  # Just get 2 items to minimize data transfer
            }
            
            try:
                # Make the request with a 10-second timeout
                response = requests.get(url, auth=auth, params=params, timeout=10)
                
                # Show response status
                print(f"Response status code: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse the JSON response
                    print("Connection successful!")
                    items = response.json()
                    
                    # Show basic info about retrieved data
                    print(f"Received {len(items)} items")
                    return True
                else:
                    # Show error message
                    print(f"Error: {response.text[:100]}...")
            except requests.exceptions.RequestException as e:
                print(f"Connection error: {str(e)}")
            except Exception as e:
                print(f"General error: {str(e)}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python test_woocommerce_simple.py <domain> <consumer_key> <consumer_secret>")
        print("Example: python test_woocommerce_simple.py mystore.com ck_12345 cs_67890")
        sys.exit(1)
    
    domain = sys.argv[1]
    consumer_key = sys.argv[2]
    consumer_secret = sys.argv[3]
    
    test_woocommerce(domain, consumer_key, consumer_secret) 