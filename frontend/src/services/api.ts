import axios from 'axios';
import { getCookie } from 'cookies-next';

const API_URL = process.env.API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = getCookie('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// This is a development mock for authentication
// In production, this would call a real authentication endpoint
export const authService = {
  login: async (email: string, password: string) => {
    // For development/demo purposes, accept any credentials
    // In production, this should validate against a real backend
    if (email && password) {
      // Mock successful login with a fixed token
      // This token is just for development and should be replaced in production
      return {
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwiZXhwIjoxNzE0NjE5MjAwLCJpYXQiOjE3MTQwMTkyMDAsInN1YiI6InRlc3QtdXNlciJ9.Ih3iQBBqGlVVNvlJKPCzQ3jX7yXX9XZwjCcRKAQOeVc',
        user: {
          id: 'test-user',
          email: email
        }
      };
    }
    
    // If no credentials provided, reject
    throw new Error('Invalid credentials');
  },
};

export const domainService = {
  getDomains: async () => {
    // For development/demo, return mock data
    // In production, this would call the real API
    return {
      domains: [
        {
          domain: 'example.com',
          name: 'Example Store',
          woocommerce_enabled: true,
          ga_enabled: true
        },
        {
          domain: 'test-store.com',
          name: 'Test Store',
          woocommerce_enabled: true,
          ga_enabled: false
        },
        {
          domain: 'demo-shop.com',
          name: 'Demo Shop',
          woocommerce_enabled: false,
          ga_enabled: true
        }
      ]
    };
  },
};

export const metricsService = {
  getMetrics: async (domain: string) => {
    // For development/demo, return mock data
    // In production, this would call the real API
    return {
      metrics: [
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000) - 86400 * 6,
          pageviews: 245,
          visitors: 120,
          orders: 8,
          revenue: 560.45
        },
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000) - 86400 * 5,
          pageviews: 289,
          visitors: 145,
          orders: 12,
          revenue: 720.30
        },
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000) - 86400 * 4,
          pageviews: 321,
          visitors: 156,
          orders: 10,
          revenue: 645.80
        },
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000) - 86400 * 3,
          pageviews: 287,
          visitors: 130,
          orders: 9,
          revenue: 590.25
        },
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000) - 86400 * 2,
          pageviews: 345,
          visitors: 175,
          orders: 15,
          revenue: 849.75
        },
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000) - 86400,
          pageviews: 325,
          visitors: 162,
          orders: 14,
          revenue: 795.99
        },
        {
          domain: domain,
          timestamp: Math.floor(Date.now() / 1000),
          pageviews: 348,
          visitors: 177,
          orders: 17,
          revenue: 912.50
        }
      ]
    };
  },
};

export default api; 