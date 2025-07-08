/**
 * API Service - Handles all API calls with authentication
 */
import axios from 'axios';

// API Configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// API Key - This should be set as an environment variable in production
const API_KEY = process.env.REACT_APP_API_KEY || 'dev_W31Og_PFEm7fg0v53MQ2Y2ogbJ4HHvt5';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`
  }
});

// Request interceptor to add auth header if not present
apiClient.interceptors.request.use(
  (config) => {
    // Ensure Authorization header is always present
    if (!config.headers.Authorization && API_KEY) {
      config.headers.Authorization = `Bearer ${API_KEY}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.error('API Key authentication failed. Please check your API key configuration.');
      // You could redirect to login page or show auth error
    }
    return Promise.reject(error);
  }
);

// API Service functions
export const apiService = {
  // Chat management
  getChats: (sessionId) => apiClient.get(`/chats?session_id=${sessionId}`),
  getChat: (chatId) => apiClient.get(`/chats/${chatId}`),
  createChat: (title, sessionId) => apiClient.post('/chats', { title, session_id: sessionId }),
  deleteChat: (chatId) => apiClient.delete(`/chats/${chatId}`),
  
  // Messages
  sendMessage: (chatId, question, useTools = true) => 
    apiClient.post(`/chats/${chatId}/messages`, { question }, { params: { use_tools: useTools } }),
  
  // Health check (no auth required)
  healthCheck: () => axios.get(`${API_URL.replace('/api', '')}/api/`),
  
  // Admin endpoints
  getStats: () => apiClient.get('/admin/stats'),
  searchMessages: (query, limit = 10) => apiClient.get(`/admin/search?query=${query}&limit=${limit}`),
  exportData: () => apiClient.get('/admin/export'),
  createBackup: () => apiClient.post('/admin/backup'),
};

// Export configured axios instance for custom calls
export default apiClient;
