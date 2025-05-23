// Script to test API connection
const axios = require('axios');

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

async function testApiConnection() {
  console.log('Testing API connection to:', API_URL);
  
  try {
    // Test login endpoint
    console.log('\nTesting login endpoint...');
    const loginResponse = await axios.post(`${API_URL}/login`, {
      email: 'admin@example.com',
      password: 'password'
    });
    
    console.log('Login response:', loginResponse.data);
    
    if (loginResponse.data && loginResponse.data.token) {
      const token = loginResponse.data.token;
      console.log('Successfully got token from login');
      
      // Test domains endpoint with the token
      console.log('\nTesting domains endpoint...');
      const domainsResponse = await axios.get(`${API_URL}/domains`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      console.log('Domains response:', domainsResponse.data);
      
      if (domainsResponse.data && domainsResponse.data.domains && domainsResponse.data.domains.length > 0) {
        const domain = domainsResponse.data.domains[0].domain;
        
        // Test metrics endpoint with the token
        console.log(`\nTesting metrics endpoint for domain: ${domain}...`);
        const metricsResponse = await axios.get(`${API_URL}/metrics/${domain}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        console.log('Metrics response:', metricsResponse.data);
      }
    }
    
    console.log('\nAPI connection test completed successfully!');
  } catch (error) {
    console.error('API connection test failed:');
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    } else if (error.request) {
      console.error('No response received from server');
    } else {
      console.error('Error:', error.message);
    }
  }
}

testApiConnection(); 