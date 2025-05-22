import json
import boto3
import sys

def add_store_to_dynamodb(domain, consumer_key, consumer_secret, store_name=None):
    """Add a WooCommerce store to DynamoDB"""
    
    if not store_name:
        store_name = domain.split('.')[0].capitalize()  # Use first part of domain as store name
    
    # Print summary
    print(f"Adding WooCommerce store to DynamoDB:")
    print(f"  Domain: {domain}")
    print(f"  Store Name: {store_name}")
    print(f"  Consumer Key: {consumer_key[:4]}...{consumer_key[-4:]} (hidden middle part)")
    print(f"  Consumer Secret: {consumer_secret[:4]}...{consumer_secret[-4:]} (hidden middle part)")
    
    try:
        # Create DynamoDB resource and get table
        print("\nConnecting to DynamoDB...")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('dashora-domains-api')
        
        # Create the item
        item = {
            'user_id': 'test-user',
            'domain_id': domain,
            'name': store_name,
            'wc_consumer_key': consumer_key,
            'wc_consumer_secret': consumer_secret,
            'woocommerce_enabled': True,
            'ga_enabled': False
        }
        
        # Add item to table
        print("Adding item to table...")
        table.put_item(Item=item)
        
        print(f"Successfully added store '{store_name}' to DynamoDB table!")
        return True
        
    except Exception as e:
        print(f"Error adding store to DynamoDB: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_store_json.py <domain> <consumer_key> <consumer_secret> [store_name]")
        print("Example: python add_store_json.py mystore.com ck_12345 cs_67890 \"My Store\"")
        sys.exit(1)
    
    domain = sys.argv[1]
    consumer_key = sys.argv[2]
    consumer_secret = sys.argv[3]
    store_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    add_store_to_dynamodb(domain, consumer_key, consumer_secret, store_name) 