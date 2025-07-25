import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    console.log('Request interceptor - URL:', config.url);
    
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('Added auth token to request');
      } else {
        console.log('No auth token found in localStorage');
      }
    }
    
    // If data is FormData, remove Content-Type to let browser set multipart boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
      console.log('Removed Content-Type for FormData request');
    }
    
    console.log('Final request config:', {
      url: config.url,
      method: config.method,
      headers: { ...config.headers },
      data: config.data instanceof FormData ? 'FormData' : config.data
    });
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/auth';
      }
    }
    return Promise.reject(error);
  }
);

export default api;