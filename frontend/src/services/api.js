import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_V1 = '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post(`${API_V1}/auth/register`, data),
  login: (data) => api.post(`${API_V1}/auth/login`, data),
};

// Chat API
export const chatAPI = {
  query: (data) => api.post(`${API_V1}/chat/query`, data),
};

// Documents API
export const documentsAPI = {
  upload: (formData) => api.post(`${API_V1}/documents/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: () => api.get(`${API_V1}/documents/list`),
};

export default api;
