import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized error (e.g., redirect to login or clear token)
      localStorage.removeItem('token');
      if (typeof window !== 'undefined') {
        // window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async register(userData: any) {
    const response = await api.post('/register', userData);
    return response.data;
  },

  async sendOtp(phone: string) {
    const response = await api.post('/send-otp', { phone });
    return response.data;
  },

  async verifyOtp(phone: string, otp: string) {
    const response = await api.post('/verify-otp', { phone, otp });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/me');
    return response.data;
  },
};

export default api;
