import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://sales-route-tracker-production.up.railway.app';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const authService = {
  getAuthUrl: () => api.get('/auth/login'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Customers
export const customerService = {
  getAll: (params) => api.get('/customers/', { params }),
  getById: (id) => api.get(`/customers/${id}`),
  getByAccount: (accountNumber) => api.get(`/customers/account/${accountNumber}`),
  getByWeekAndDay: (week, day) => api.get(`/customers/week/${week}/day/${day}`),
};

// Visits
export const visitService = {
  getAll: () => api.get('/visits/'),
  getByCustomer: (customerId) => api.get(`/visits/customer/${customerId}`),
  create: (data) => api.post('/visits/', data),
  update: (id, data) => api.patch(`/visits/${id}`, data),
  delete: (id) => api.delete(`/visits/${id}`),
  getStats: () => api.get('/visits/stats/dashboard'),
};

// Sync
export const syncService = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/sync/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  downloadFile: async () => {
    const response = await api.get('/sync/download', {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'Route_Tracking_Data.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  syncFromOneDrive: () => api.post('/sync/import'),
  syncToOneDrive: () => api.post('/sync/export'),
  getStatus: () => api.get('/sync/status')
};

export default api;
