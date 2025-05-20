import os
import json
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Set environment variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['METRICS_TABLE_NAME'] = 'dashora-metrics-v2'
os.environ['DOMAINS_TABLE_NAME'] = 'dashora-domains-v2'
os.environ['USERS_TABLE_NAME'] = 'dashora-users-v2'
os.environ['JWT_SECRET'] = 'da5h0raAn4lyt1csS3cretK3y2024Pr0duct10n'

# Import mock handlers from API test
from api_test import lambda_handler

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Dashora Analytics API",
        "endpoints": [
            "/domains",
            "/metrics/{domain_name}?days=7"
        ]
    })

@app.route('/domains', methods=['GET'])
def get_domains():
    # Convert Flask request to Lambda event format
    event = {
        'httpMethod': 'GET',
        'path': '/domains',
        'queryStringParameters': {},
        'headers': dict(request.headers)
    }
    
    # Add authorization header if present
    auth_header = request.headers.get('Authorization')
    if auth_header:
        event['headers']['Authorization'] = auth_header
    
    # Call the Lambda handler
    response = lambda_handler(event, {})
    
    # Convert Lambda response to Flask response
    return jsonify(json.loads(response['body'])), response['statusCode']

@app.route('/metrics/<domain>', methods=['GET'])
def get_metrics(domain):
    # Get query parameters
    days = request.args.get('days', '7')
    
    # Convert Flask request to Lambda event format
    event = {
        'httpMethod': 'GET',
        'path': f'/metrics/{domain}',
        'queryStringParameters': {'days': days},
        'headers': dict(request.headers)
    }
    
    # Add authorization header if present
    auth_header = request.headers.get('Authorization')
    if auth_header:
        event['headers']['Authorization'] = auth_header
    
    # Call the Lambda handler
    response = lambda_handler(event, {})
    
    # Convert Lambda response to Flask response
    return jsonify(json.loads(response['body'])), response['statusCode']

@app.route('/test-token', methods=['GET'])
def test_token():
    """Helper endpoint to generate a valid test token"""
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzQ3NzUxMTA5LCJpYXQiOjE3NDc2NjQ3MDksInN1YiI6InRlc3QtdXNlciJ9.5hL4f07L0R65CYaAW2rQtvsCfQ6MWgqrBQzXhav3mQw"
    return jsonify({
        "message": "Use this token for testing",
        "token": test_token,
        "usage": "Add Authorization header with value: Bearer " + test_token
    })

if __name__ == '__main__':
    print("Starting Dashora Local API Server...")
    print("-" * 50)
    print("Available endpoints:")
    print("  GET /              - API info")
    print("  GET /test-token    - Get a test token")
    print("  GET /domains       - List all domains")
    print("  GET /metrics/{domain}?days=7 - Get metrics for a domain")
    print("-" * 50)
    print("To test with curl:")
    print('  curl http://localhost:5000/test-token')
    print('  curl -H "Authorization: Bearer TOKEN_FROM_ABOVE" http://localhost:5000/domains')
    print("-" * 50)
    app.run(debug=True) 