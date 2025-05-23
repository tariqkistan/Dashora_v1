# Vercel Environment Variables Setup Guide

When deploying your Dashora frontend to Vercel, you'll need to set up the following environment variables to connect to your AWS Lambda backend.

## Required Environment Variables

| Variable Name | Description | Example Value |
|---------------|-------------|--------------|
| `NEXT_PUBLIC_API_URL` | The URL of your AWS API Gateway endpoint | `https://abc123def.execute-api.us-east-1.amazonaws.com/prod` |
| `NEXT_PUBLIC_ENV` | The environment name | `production` |
| `NEXT_PUBLIC_AUTH_ENABLED` | Whether authentication is enabled | `true` |
| `NEXT_PUBLIC_JWT_COOKIE_NAME` | The name of the JWT cookie | `auth_token` |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | Whether to enable analytics | `true` |
| `NEXT_PUBLIC_ENABLE_NOTIFICATIONS` | Whether to enable notifications | `false` |

## Setting Up Environment Variables in Vercel

1. Go to your Vercel dashboard at [vercel.com](https://vercel.com)
2. Select your Dashora project
3. Navigate to "Settings" → "Environment Variables"
4. Add each of the variables listed above with their respective values
5. Make sure you select the environments where each variable should be applied (Production, Preview, Development)
6. Click "Save" to apply your changes

## Important Notes

- **API URL**: You'll get the API Gateway URL after deploying your AWS Lambda functions. It will be shown in the AWS SAM deployment output or in the API Gateway console.
- **Environment**: Set to `production` for production deployments.
- **Authentication**: The `NEXT_PUBLIC_AUTH_ENABLED` should be set to `true` for production.
- **JWT Cookie Name**: This should match what you've set in your backend Lambda functions.

## Testing Your Configuration

After deploying, you can check if your environment variables are correctly set by visiting your deployed site and opening the browser's developer console. Run:

```javascript
console.log(process.env.NEXT_PUBLIC_API_URL);
```

This should show your API Gateway URL, confirming that your environment variables are correctly loaded. 