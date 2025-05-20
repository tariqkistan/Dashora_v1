# Dashora Data Source Integration Guide

This guide will help you set up real data sources for your Dashora Analytics Dashboard.

## 1. WooCommerce Integration

### Prerequisites
- A WordPress site with WooCommerce plugin installed and activated
- Administrator access to the WordPress site

### Steps

1. **Create API Keys in WooCommerce**
   
   - Log in to your WordPress admin dashboard
   - Navigate to WooCommerce > Settings > Advanced > REST API
   - Click "Add Key"
   - Enter a description (e.g., "Dashora Analytics")
   - Set User to an admin account
   - Set Permissions to "Read"
   - Click "Generate API Key"
   - **IMPORTANT**: Save the Consumer Key and Consumer Secret that are generated

2. **Configure Domain in Dashora**

   Create a domain record in the DynamoDB `dashora-domains` table with the following structure:
   
   ```json
   {
     "user_id": "your-user-id",
     "domain_id": "your-store-domain.com",
     "name": "Your Store Name",
     "woocommerce_config": {
       "api_url": "https://your-store-domain.com",
       "consumer_key": "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
       "consumer_secret": "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
     }
   }
   ```

3. **Test the Integration**

   - Deploy the Lambda functions
   - Manually trigger the WooCommerce fetcher function
   - Check the CloudWatch logs for any errors

## 2. Google Analytics 4 Integration

### Prerequisites
- A Google Analytics 4 property set up for your website
- Admin access to the Google Analytics property
- Google Cloud Platform (GCP) account

### Steps

1. **Create a Service Account in GCP**

   - Go to Google Cloud Console (https://console.cloud.google.com/)
   - Create a new project (or use an existing one)
   - Navigate to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Enter a name (e.g., "Dashora Analytics")
   - Grant "Viewer" role
   - Click "Create"
   - Create a key for this service account (JSON format)
   - **IMPORTANT**: Download and securely store the JSON key file

2. **Enable Google Analytics API**

   - In Google Cloud Console, navigate to APIs & Services > Library
   - Search for "Google Analytics Data API"
   - Enable the API

3. **Grant Access in Google Analytics**

   - Go to your Google Analytics 4 property
   - Navigate to Admin > Property > Property Access Management
   - Add the service account email with "Viewer" permissions

4. **Configure Domain in Dashora**

   Update the domain record in the DynamoDB `dashora-domains` table to include GA configuration:
   
   ```json
   {
     "user_id": "your-user-id",
     "domain_id": "your-domain.com",
     "name": "Your Domain Name",
     "woocommerce_config": {
       // Your existing WooCommerce config (if applicable)
     },
     "ga_config": {
       "property_id": "123456789",  // Your GA4 property ID (numbers only)
       "service_account_info": {
         // Copy the entire contents of your service account JSON key file here
       }
     }
   }
   ```

5. **Test the Integration**

   - Deploy the Lambda functions
   - Manually trigger the Google Analytics fetcher function
   - Check the CloudWatch logs for any errors

## 3. Troubleshooting

### WooCommerce Issues

- **Authentication Errors**: Double-check your consumer key and secret
- **Permission Issues**: Ensure the API key has at least "Read" permissions
- **HTTPS Issues**: Ensure your store uses HTTPS and has a valid SSL certificate

### Google Analytics Issues

- **Authentication Errors**: Verify the service account JSON file is correctly formatted
- **Access Issues**: Make sure the service account has viewer access to the GA4 property
- **API Quota**: Check if you've exceeded Google Analytics API quotas

## 4. Next Steps

Once your data sources are properly integrated:

1. The fetcher functions will automatically run on their scheduled times
2. The metrics processor will combine data from both sources
3. The API will expose the processed data for your dashboard frontend

For more detailed troubleshooting, check the CloudWatch logs for each Lambda function. 