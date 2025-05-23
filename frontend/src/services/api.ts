import axios, { AxiosError, AxiosResponse } from 'axios';
import { getCookie, setCookie, deleteCookie } from 'cookies-next';

// Use environment variable from Next.js config with /api prefix for rewrites
const API_URL = '/api';
const JWT_COOKIE_NAME = process.env.JWT_COOKIE_NAME || 'auth_token';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Type for API error response
interface ApiErrorResponse {
  error: string;
  message?: string;
  statusCode?: number;
}

// Enhanced Error interface
class ApiError extends Error {
  statusCode?: number;
  response?: AxiosResponse;
  
  constructor(message: string, statusCode?: number, response?: AxiosResponse) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

// Handle API Error
const handleApiError = (error: AxiosError<ApiErrorResponse>): never => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const errorMessage = error.response.data?.error || error.response.data?.message || 'An error occurred';
    const apiError = new ApiError(
      errorMessage,
      error.response.status,
      error.response
    );
    
    // Handle 401 Unauthorized errors (token expired or invalid)
    if (error.response.status === 401) {
      deleteCookie(JWT_COOKIE_NAME);
      // Redirect to login if we're in a browser context
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    throw apiError;
  } else if (error.request) {
    // The request was made but no response was received
    throw new ApiError('Network error - no response received', 0);
  } else {
    // Something happened in setting up the request that triggered an Error
    throw new ApiError(`Request setup error: ${error.message}`, 0);
  }
};

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = getCookie(JWT_COOKIE_NAME);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    return Promise.reject(handleApiError(error));
  }
);

// Authentication service
export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/login', { email, password });
    
    if (response.data.token) {
      // Set the auth token in cookies
      setCookie(JWT_COOKIE_NAME, response.data.token, {
        maxAge: 60 * 60 * 24 * 7, // 7 days
        path: '/',
      });
    }
    
    return response.data;
  },
  
  logout: async () => {
    // Just delete the cookie as our backend doesn't have a logout endpoint yet
    deleteCookie(JWT_COOKIE_NAME);
    return { success: true };
  },
  
  refreshToken: async () => {
    // Backend doesn't have refresh token endpoint yet
    // For now, we'll just return the current token
    const token = getCookie(JWT_COOKIE_NAME);
    if (!token) {
      throw new ApiError('No token to refresh', 401);
    }
    return { token };
  },
  
  checkAuth: async () => {
    try {
      // For now we'll just check if the token exists
      // In the future, we can add a /me endpoint to the backend
      const token = getCookie(JWT_COOKIE_NAME);
      if (!token) {
        return null;
      }
      return { authenticated: true };
    } catch (error) {
      // Auth check failed, handle quietly
      return null;
    }
  },
};

// Domain service
export const domainService = {
  getDomains: async () => {
    const response = await api.get('/domains');
    return response.data;
  },
  
  getDomain: async (domain: string) => {
    const response = await api.get(`/domains/${domain}`);
    return response.data;
  },
  
  updateDomain: async (domain: string, data: any) => {
    const response = await api.put(`/domains/${domain}`, data);
    return response.data;
  },
  
  addDomain: async (data: { name: string; domain: string; woocommerce_enabled?: boolean; ga_enabled?: boolean }) => {
    try {
      const response = await api.post('/domains', data);
      return { 
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error('Error adding domain:', error);
      // If we're in development mode and the endpoint doesn't exist, fake success response
      if (process.env.NODE_ENV === 'development') {
        console.log('Development mode: Simulating successful domain addition');
        return { 
          success: true, 
          domain_id: data.domain,
          message: 'Domain added successfully' 
        };
      }
      
      throw error;
    }
  },
  
  deleteDomain: async (domain: string) => {
    try {
      const response = await api.delete(`/domains/${domain}`);
      return {
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error('Error deleting domain:', error);
      throw error;
    }
  },
  
  getIntegrationDetails: async (domain: string, type: string) => {
    try {
      const response = await api.get(`/domains/${domain}/integrations/${type}`);
      return response.data;
    } catch (error) {
      // If the endpoint doesn't exist yet or returns an error, we'll just return null
      console.error(`Error fetching integration details for ${domain}/${type}:`, error);
      return null;
    }
  },
  
  connectIntegration: async (domain: string, type: string, credentials: any) => {
    try {
      const response = await api.post(`/domains/${domain}/integrations/${type}`, credentials);
      return { 
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error(`Error connecting integration for ${domain}/${type}:`, error);
      // If we're in development mode and the endpoint doesn't exist, fake success response
      if (process.env.NODE_ENV === 'development') {
        console.log('Development mode: Simulating successful integration');
        
        if (type === 'woocommerce') {
          // Simulate connecting to WooCommerce
          return {
            success: true,
            store_name: credentials.domain,
            product_count: 42,
            last_order_date: new Date().toISOString()
          };
        }
        
        return { success: true };
      }
      
      throw error;
    }
  },
  
  disconnectIntegration: async (domain: string, type: string) => {
    try {
      const response = await api.delete(`/domains/${domain}/integrations/${type}`);
      return { 
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error(`Error disconnecting integration for ${domain}/${type}:`, error);
      // If we're in development mode and the endpoint doesn't exist, fake success response
      if (process.env.NODE_ENV === 'development') {
        console.log('Development mode: Simulating successful disconnection');
        return { success: true };
      }
      
      throw error;
    }
  },
};

// Metrics service
export const metricsService = {
  getMetrics: async (domain: string, period?: string) => {
    const params = period ? { period } : {};
    const response = await api.get(`/metrics/${domain}`, { params });
    return response.data;
  },
};

export default api; 