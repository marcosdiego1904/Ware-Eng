import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1',
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
      console.warn('401 Unauthorized response received:', error.config?.url);
      
      // Only redirect to auth if this is NOT a rules API call (for debugging)
      const isRulesApiCall = error.config?.url?.includes('/rules') || error.config?.url?.includes('/categories');
      
      if (!isRulesApiCall && typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/auth';
      } else if (isRulesApiCall) {
        console.warn('Rules API call failed with 401 - check if backend is running and rules endpoints are configured');
      }
    }
    return Promise.reject(error);
  }
);

// User Preferences API for Clear Anomalies Feature
export const userPreferencesApi = {
  async getPreferences() {
    const response = await api.get('/user/preferences');
    return response.data;
  },

  async updatePreferences(preferences: {
    clear_previous_anomalies?: boolean;
    show_clear_warning?: boolean;
  }) {
    const response = await api.post('/user/preferences', preferences);
    return response.data;
  }
};

export default api;
export { api };