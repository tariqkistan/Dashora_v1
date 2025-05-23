import boto3
import sys

def add_woocommerce_store(domain, consumer_key, consumer_secret, store_name=None):
    """Add WooCommerce store credentials to the domains table"""
    
    if not store_name:
        store_name = domain.replace('.com', '').capitalize()
    
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    domains_table = dynamodb.Table('dashora-domains-api')
    
    try:
        # Add domain to table
        domains_table.put_item(
            Item={
                'user_id': 'test-user',
                'domain_id': domain,
                'name': store_name,
                'wc_consumer_key': consumer_key,
                'wc_consumer_secret': consumer_secret,
                'woocommerce_enabled': True,
                'ga_enabled': False
            }
        )
        
        print(f"Successfully added {domain} to the domains table")
        return True
    except Exception as e:
        print(f"Error adding domain: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_woocommerce.py <domain> <consumer_key> <consumer_secret> [store_name]")
        sys.exit(1)
    
    domain = sys.argv[1]
    consumer_key = sys.argv[2]
    consumer_secret = sys.argv[3]
    store_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    add_woocommerce_store(domain, consumer_key, consumer_secret, store_name) 