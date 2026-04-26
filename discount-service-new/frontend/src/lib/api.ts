import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    config.headers['X-Request-ID'] = generateRequestId();
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export const discountAPI = {
  getAll: (params?: Record<string, any>) => 
    apiClient.get('/discounts', { params }),
  
  getById: (id: number) => 
    apiClient.get(`/discounts/${id}`),
  
  getPersonal: () => 
    apiClient.get('/discounts/personal'),
  
  getBankOffers: () => 
    apiClient.get('/discounts/bank-offers'),
  
  search: (query: string, params?: Record<string, any>) => 
    apiClient.get('/discounts/search', { params: { q: query, ...params } }),
  
  toggleFavorite: (id: number) => 
    apiClient.post(`/discounts/${id}/favorite`),
};

export const authAPI = {
  login: (email: string, password: string) => 
    apiClient.post('/auth/login', { email, password }),
  
  register: (data: Record<string, any>) => 
    apiClient.post('/auth/register', data),
  
  logout: () => 
    apiClient.post('/auth/logout'),
  
  me: () => 
    apiClient.get('/auth/me'),
  
  refreshToken: (refreshToken: string) => 
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
};

export const storesAPI = {
  getAll: () => 
    apiClient.get('/stores'),
  
  getById: (id: number) => 
    apiClient.get(`/stores/${id}`),
  
  getDiscounts: (storeId: number) => 
    apiClient.get(`/stores/${storeId}/discounts`),
};

export const categoriesAPI = {
  getAll: () => 
    apiClient.get('/categories'),
  
  getTree: () => 
    apiClient.get('/categories/tree'),
};

export const collectionsAPI = {
  getAll: () => 
    apiClient.get('/collections'),
  
  getById: (id: number) => 
    apiClient.get(`/collections/${id}`),
  
  create: (data: Record<string, any>) => 
    apiClient.post('/collections', data),
  
  update: (id: number, data: Record<string, any>) => 
    apiClient.put(`/collections/${id}`, data),
  
  delete: (id: number) => 
    apiClient.delete(`/collections/${id}`),
  
  share: (id: number) => 
    apiClient.post(`/collections/${id}/share`),
};

export const familyCardAPI = {
  get: () => 
    apiClient.get('/family-card'),
  
  create: (name: string) => 
    apiClient.post('/family-card', { name }),
  
  addMember: (email: string) => 
    apiClient.post('/family-card/members', { email }),
  
  removeMember: (memberId: number) => 
    apiClient.delete(`/family-card/members/${memberId}`),
};

export const subscriptionAPI = {
  getPlans: () => 
    apiClient.get('/subscriptions/plans'),
  
  getCurrent: () => 
    apiClient.get('/subscriptions/current'),
  
  subscribe: (planId: string) => 
    apiClient.post('/subscriptions/subscribe', { plan_id: planId }),
  
  cancel: () => 
    apiClient.post('/subscriptions/cancel'),
};
