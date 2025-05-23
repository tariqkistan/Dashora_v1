import boto3
import argparse
import uuid
from boto3.dynamodb.conditions import Key

# Function to add or update a store with WooCommerce credentials
def add_or_update_store(domain, wc_key, wc_secret, user_id='test-user', name=None, ga_enabled=False):
    """
    Add or update a store in the Dashora system with WooCommerce credentials
    """
    if not name:
        name = domain.replace('.com', '').capitalize()
    
    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    domains_table = dynamodb.Table('dashora-domains-api')
    
    # Check if domain already exists for the user
    response = domains_table.query(
        KeyConditionExpression=Key('user_id').eq(user_id) & Key('domain_id').eq(domain)
    )
    
    if response['Count'] > 0:
        # Update existing domain
        print(f"Updating existing domain {domain} for user {user_id}")
        domains_table.update_item(
            Key={
                'user_id': user_id,
                'domain_id': domain
            },
            UpdateExpression="set wc_consumer_key=:k, wc_consumer_secret=:s, woocommerce_enabled=:we, name=:n, ga_enabled=:ge",
            ExpressionAttributeValues={
                ':k': wc_key,
                ':s': wc_secret,
                ':we': True,
                ':n': name,
                ':ge': ga_enabled
            }
        )
    else:
        # Create new domain
        print(f"Adding new domain {domain} for user {user_id}")
        domains_table.put_item(
            Item={
                'user_id': user_id,
                'domain_id': domain,
                'wc_consumer_key': wc_key,
                'wc_consumer_secret': wc_secret,
                'woocommerce_enabled': True,
                'ga_enabled': ga_enabled,
                'name': name
            }
        )
    
    print(f"Successfully added/updated store: {domain}")
    return {
        'domain': domain,
        'name': name,
        'woocommerce_enabled': True,
        'ga_enabled': ga_enabled
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add or update a WooCommerce store')
    parser.add_argument('--domain', required=True, help='Store domain (e.g., mystore.com)')
    parser.add_argument('--key', required=True, help='WooCommerce API Consumer Key')
    parser.add_argument('--secret', required=True, help='WooCommerce API Consumer Secret')
    parser.add_argument('--user_id', default='test-user', help='User ID (default: test-user)')
    parser.add_argument('--name', help='Store name (default: derived from domain)')
    parser.add_argument('--ga_enabled', action='store_true', help='Enable Google Analytics integration')
    
    args = parser.parse_args()
    
    result = add_or_update_store(
        args.domain,
        args.key,
        args.secret,
        args.user_id,
        args.name,
        args.ga_enabled
    )
    
    print(f"Store details: {result}") 