/**
 * API Service - Handles all API calls using secure backend proxy
 * No API keys needed - authentication handled by backend origin validation
 */
import axios from 'axios';

// API Configuration
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000,
});

// Request interceptor to add necessary headers
apiClient.interceptors.request.use(
  (config) => {
    // Add origin header for backend validation
    if (typeof window !== 'undefined') {
      config.headers['Origin'] = window.location.origin;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 403) {
      console.error('Access denied: Requests must come from authorized frontend.');
    } else if (error.response?.status === 401) {
      console.error('Authentication failed. Please check your configuration.');
    }
    return Promise.reject(error);
  }
);

// API Service functions using frontend-specific endpoints
export const apiService = {
  // Chat management (using /frontend endpoints - no API key required)
  getChats: (sessionId) => apiClient.get(`/frontend/chats?session_id=${sessionId}`),
  getChat: (chatId) => apiClient.get(`/frontend/chats/${chatId}`),
  createChat: (title, sessionId) => apiClient.post('/frontend/chats', { title, session_id: sessionId }),
  deleteChat: (chatId) => apiClient.delete(`/frontend/chats/${chatId}`),
  
  // Messages (using /frontend endpoints - no API key required)
  sendMessage: (chatId, question, useTools = true) => 
    apiClient.post(`/frontend/chats/${chatId}/messages`, { question }, { params: { use_tools: useTools } }),
  
  // Health check (no auth required)
  healthCheck: () => apiClient.get('/'),
};

// Export configured axios instance for custom calls
export default apiClient;
