import requests

# Your WooCommerce store details
DOMAIN = "www.perfectlaser.co.za"
CONSUMER_KEY = "ck_05adf8de03dddbf5e812a17c63a3688175eea1dd"
CONSUMER_SECRET = "cs_cc8d68e6a58e99fde24bce06ee5e157c95710198"

# Print basic info
print("Testing WooCommerce API connection:")
print(f"  Domain: {DOMAIN}")
print(f"  Consumer Key: {CONSUMER_KEY[:4]}...{CONSUMER_KEY[-4:]}")
print(f"  Consumer Secret: {CONSUMER_SECRET[:4]}...{CONSUMER_SECRET[-4:]}")

# Full URL for the test
url = f"https://{DOMAIN}/wp-json/wc/v3/products"

# Authentication
auth = (CONSUMER_KEY, CONSUMER_SECRET)

# Parameters
params = {
    'per_page': 2  # Just get 2 products to minimize data transfer
}

print(f"\nConnecting to: {url}")

try:
    # Make the request with a 10-second timeout
    print("Sending request...")
    response = requests.get(url, auth=auth, params=params, timeout=15)
    
    # Show response status
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        # Parse the JSON response
        print("Connection successful!")
        products = response.json()
        
        # Show basic product info
        print(f"\nReceived {len(products)} products:")
        for i, product in enumerate(products):
            print(f"  Product {i+1}: {product.get('name')} - ${product.get('price')}")
    else:
        # Show error message
        print(f"Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Connection error: {str(e)}")
except Exception as e:
    print(f"General error: {str(e)}")

print("\nTest completed.") 