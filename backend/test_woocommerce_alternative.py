import requests
import sys
import json

def test_woocommerce_alternative(domain, consumer_key, consumer_secret):
    """Test alternative WooCommerce API endpoints"""
    
    print("Testing alternative WooCommerce API endpoints:")
    print(f"  Domain: {domain}")
    print(f"  Consumer Key: {consumer_key[:4]}...{consumer_key[-4:]} (hidden middle part)")
    print(f"  Consumer Secret: {consumer_secret[:4]}...{consumer_secret[-4:]} (hidden middle part)")
    
    # Test WordPress REST API namespaces
    print("\nChecking available WordPress REST API namespaces...")
    namespaces_url = f"https://{domain}/wp-json/"
    
    try:
        response = requests.get(namespaces_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'namespaces' in data:
                print("Available REST API namespaces:")
                for namespace in data['namespaces']:
                    print(f"  {namespace}")
                    # If we find a WooCommerce namespace, note it
                    if 'wc' in namespace or 'woocommerce' in namespace:
                        print(f"  *** WooCommerce namespace found: {namespace} ***")
        else:
            print(f"Couldn't get namespaces: {response.status_code}")
    except Exception as e:
        print(f"Error checking namespaces: {str(e)}")
    
    # Try alternative WooCommerce URL patterns
    patterns = [
        "/wp-json/wc-api/v3/products",
        "/wp-json/wc-api/v2/products",
        "/wp-json/wc-api/v1/products",
        "/wp-json/wc/v3/products",
        "/wp-json/woocommerce/v3/products",
        "/wp-json/woocommerce/v2/products",
        "/wp-json/woocommerce/v1/products",
        "/wc-api/v3/products",
        "/wc-api/v2/products",
    ]
    
    print("\nTrying alternative WooCommerce API patterns:")
    for pattern in patterns:
        url = f"https://{domain}{pattern}"
        print(f"\nTesting: {url}")
        
        try:
            # Try both with and without authentication to see what happens
            print("  Without authentication:")
            response_no_auth = requests.get(url, timeout=10)
            print(f"  Status: {response_no_auth.status_code}")
            
            if response_no_auth.status_code == 200:
                print("  Success! API endpoint found without authentication")
                continue  # Skip authentication test if we already succeeded
            
            print("  With authentication:")
            response_auth = requests.get(
                url, 
                auth=(consumer_key, consumer_secret),
                params={'per_page': 2},
                timeout=10
            )
            print(f"  Status: {response_auth.status_code}")
            
            if response_auth.status_code == 200:
                print("  Success! API endpoint found with authentication")
                data = response_auth.json()
                print(f"  Received {len(data)} items")
            elif response_auth.status_code == 401:
                print("  Authentication required (401) - API endpoint may exist")
            else:
                print(f"  Error: {response_auth.text[:100]}...")
                
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python test_woocommerce_alternative.py <domain> <consumer_key> <consumer_secret>")
        print("Example: python test_woocommerce_alternative.py mystore.com ck_12345 cs_67890")
        sys.exit(1)
    
    domain = sys.argv[1]
    consumer_key = sys.argv[2]
    consumer_secret = sys.argv[3]
    
    test_woocommerce_alternative(domain, consumer_key, consumer_secret) 