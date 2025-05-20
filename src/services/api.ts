import axios from 'axios';

// Define an API client with the base URL
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  // Get token from cookies or localStorage
  const token = typeof window !== 'undefined' ? 
    document.cookie.replace(/(?:(?:^|.*;\s*)auth_token\s*=\s*([^;]*).*$)|^.*$/, "$1") : 
    "";
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

// Domain service
export const domainService = {
  getDomains: async () => {
    try {
      const response = await apiClient.get('/domains');
      return response.data;
    } catch (error) {
      console.error('Error fetching domains:', error);
      throw error;
    }
  },
};

// Metrics service
export const metricsService = {
  getMetrics: async (domain: string) => {
    try {
      const response = await apiClient.get(`/metrics/${domain}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching metrics for ${domain}:`, error);
      throw error;
    }
  },
}; 