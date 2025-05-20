# 🚀 Dashora - Multi-Site Analytics Dashboard

Real-time analytics dashboard that aggregates data from multiple WooCommerce stores and Google Analytics accounts.

## 📊 Architecture Overview

The system uses a serverless architecture on AWS with the following components:

- **Data Collection**: AWS Lambda functions fetch data from WooCommerce and Google Analytics v4
- **Storage**: Amazon DynamoDB for metrics storage
- **API Layer**: Amazon API Gateway with Lambda integration
- **Frontend**: React-based dashboard with auto-refresh capabilities
- **Security**: AWS Secrets Manager and IAM roles
- **Monitoring**: CloudWatch Logs and SNS alerts

## 🛠️ Project Structure

```
dashora/
├── backend/
│   ├── lambdas/
│   │   ├── woocommerce_fetcher/
│   │   ├── ga_fetcher/
│   │   ├── metrics_processor/
│   │   └── api_handler/
│   └── terraform/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   └── public/
└── docs/
```

## 🔧 Setup & Configuration

### Prerequisites

1. AWS CLI configured with appropriate credentials
2. Node.js 18+ and npm/yarn
3. Python 3.9+
4. Terraform (optional, for IaC)

### Environment Variables

Create a `.env` file in both frontend and backend directories:

```env
# Backend
AWS_REGION=us-east-1
DYNAMODB_TABLE=dashora-metrics
SECRETS_MANAGER_PREFIX=/dashora/

# Frontend
REACT_APP_API_ENDPOINT=https://your-api.execute-api.region.amazonaws.com/
REACT_APP_REFRESH_INTERVAL=300000
```

### API Credentials Setup

1. WooCommerce:
   - Generate API keys from WooCommerce > Settings > Advanced > REST API
   - Store in AWS Secrets Manager under `/dashora/woocommerce/{domain}`

2. Google Analytics:
   - Create service account and download credentials
   - Store in AWS Secrets Manager under `/dashora/google-analytics/{domain}`

## 🚀 Deployment

### Backend Deployment

1. Create AWS resources:
   ```bash
   cd backend/terraform
   terraform init
   terraform apply
   ```

2. Deploy Lambda functions:
   ```bash
   cd backend/lambdas
   ./deploy.sh
   ```

### Frontend Deployment

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Build and deploy:
   ```bash
   npm run build
   # Deploy to your hosting service
   ```

## 📈 Monitoring & Maintenance

- CloudWatch Logs are available for all Lambda functions
- SNS notifications are set up for API failures
- Check CloudWatch Metrics dashboard for performance metrics

## 🔐 Security Considerations

- All API keys are stored in AWS Secrets Manager
- IAM roles follow principle of least privilege
- API Gateway uses API key authentication
- Frontend uses environment variables for sensitive data

## 🗓️ Development Timeline

### Week 1: MVP Launch Plan

1. **Day 1-2**: Infrastructure Setup
   - Set up AWS resources
   - Configure security and IAM roles

2. **Day 3-4**: Backend Development
   - Implement Lambda functions
   - Set up DynamoDB

3. **Day 5-6**: Frontend Development
   - Create React dashboard
   - Implement data fetching and charts

4. **Day 7**: Testing & Deployment
   - End-to-end testing
   - Production deployment

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Support

For support, email support@dashora.com or create an issue in the repository.

# Dashora Analytics

A multi-site analytics dashboard for aggregating and displaying metrics from WooCommerce stores and Google Analytics accounts.

## Features

- **Multi-site Management**: Track metrics across multiple domains
- **WooCommerce Integration**: Display order and revenue data
- **Google Analytics Integration**: Show traffic metrics
- **Unified Dashboard**: View all your site performance in one place

## Project Structure

- **Frontend**: Next.js application with Tailwind CSS
- **Backend**: Node.js Express API server (development mock) and AWS serverless backend (production)

## Prerequisites

- Node.js (v16+)
- npm or yarn
- For production deployment: AWS account

## Quick Start

### Frontend Setup

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Create a `.env.local` file with:
   ```
   API_URL=http://localhost:5000
   ```

3. Start the development server:
   ```
   npm run dev
   ```

### Backend Setup (Development Mock)

1. Install dependencies:
   ```
   cd backend
   npm install
   ```

2. Start the server:
   ```
   npm run dev
   ```

### Login Credentials (Mock Server)
- Email: admin@example.com
- Password: password

## Production Deployment

For production, the backend uses:
- AWS Lambda for serverless processing
- DynamoDB for data storage
- API Gateway for RESTful endpoints

See the [Terraform Configuration](./terraform) for infrastructure setup.

## Development Guidelines

- Follow existing code style and architecture
- Use environment variables for configuration
- Add tests for new features

## License

MIT 