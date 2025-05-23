import requests
import json
from datetime import datetime, timedelta

def test_woocommerce_connection(domain, consumer_key, consumer_secret):
    """Test a connection to the WooCommerce API"""
    
    # WooCommerce API URL
    url = f"https://{domain}/wp-json/wc/v3/orders"
    
    # Calculate date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Parameters for WooCommerce API
    params = {
        'after': start_date.isoformat(),
        'before': end_date.isoformat(),
        'per_page': 5  # Just fetch a few orders for testing
    }
    
    # Authentication
    auth = (consumer_key, consumer_secret)
    
    print(f"Testing connection to {url}")
    print(f"Using authentication: {consumer_key[:5]}...:{consumer_secret[:5]}...")
    
    try:
        # Make the API request
        response = requests.get(url, params=params, auth=auth)
        
        # Check the response
        if response.status_code == 200:
            orders = response.json()
            print(f"Connection successful! Received {len(orders)} orders.")
            
            # Display summary of orders
            if len(orders) > 0:
                total_sales = sum(float(order.get('total', 0)) for order in orders)
                print(f"Total sales from these orders: ${total_sales:.2f}")
                
                # Display first order details
                first_order = orders[0]
                print("\nSample order:")
                print(f"Order ID: {first_order.get('id')}")
                print(f"Date: {first_order.get('date_created')}")
                print(f"Status: {first_order.get('status')}")
                print(f"Total: ${float(first_order.get('total', 0)):.2f}")
            
            return True
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"Error connecting to WooCommerce API: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python test_woocommerce.py <domain> <consumer_key> <consumer_secret>")
        sys.exit(1)
    
    domain = sys.argv[1]
    consumer_key = sys.argv[2]
    consumer_secret = sys.argv[3]
    
    test_woocommerce_connection(domain, consumer_key, consumer_secret) 