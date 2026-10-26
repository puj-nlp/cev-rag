/**
 * API Service - Handles all API calls using secure backend proxy
 * No API keys needed - the browser session lives in an HttpOnly cookie set by the backend,
 * and state-changing requests carry a custom header the backend requires (CSRF protection).
 */
import axios from 'axios';

// API Configuration
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Legacy key from when the session ID was generated and stored by the browser
const LEGACY_SESSION_KEY = 'ventana_session_id';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'cev-rag'
  },
  withCredentials: true,
  timeout: 120000,
});

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
    } else if (error.response?.status === 429) {
      console.error('Too many requests. Please wait a moment and try again.');
    }
    return Promise.reject(error);
  }
);

let sessionPromise = null;

/**
 * Ensures the HttpOnly session cookie exists before chat calls.
 * A browser that still has the old localStorage session hands it over once so
 * its chat history stays available; the value is then removed from localStorage.
 */
const ensureSession = () => {
  if (!sessionPromise) {
    let legacySessionId = null;
    try {
      legacySessionId = window.localStorage.getItem(LEGACY_SESSION_KEY);
    } catch (e) {
      // Storage unavailable
    }
    sessionPromise = apiClient
      .post('/frontend/session', { legacy_session_id: legacySessionId })
      .then((response) => {
        try {
          window.localStorage.removeItem(LEGACY_SESSION_KEY);
        } catch (e) {
          // Storage unavailable
        }
        return response;
      })
      .catch((error) => {
        sessionPromise = null;
        throw error;
      });
  }
  return sessionPromise;
};

const withSession = (request) => (...args) => ensureSession().then(() => request(...args));

// API Service functions using frontend-specific endpoints
export const apiService = {
  // Chat management (using /frontend endpoints - no API key required)
  getChats: withSession(() => apiClient.get('/frontend/chats')),
  getChat: withSession((chatId) => apiClient.get(`/frontend/chats/${encodeURIComponent(chatId)}`)),
  createChat: withSession((title) => apiClient.post('/frontend/chats', { title })),
  deleteChat: withSession((chatId) => apiClient.delete(`/frontend/chats/${encodeURIComponent(chatId)}`)),
  
  // Messages (using /frontend endpoints - no API key required)
  sendMessage: withSession((chatId, question, language = 'es', useTools = true) =>
    apiClient.post(
      `/frontend/chats/${encodeURIComponent(chatId)}/messages`,
      { question, language },
      { params: { use_tools: useTools } }
    )),
  
  // Health check (no auth required)
  healthCheck: () => apiClient.get('/'),
};

// Export configured axios instance for custom calls
export default apiClient;
