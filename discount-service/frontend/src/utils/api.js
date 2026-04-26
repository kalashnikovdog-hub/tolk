import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage')
    if (token) {
      const parsed = JSON.parse(token)
      if (parsed.token) {
        config.headers.Authorization = `Bearer ${parsed.token}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
}

export const discountAPI = {
  getAll: (params) => api.get('/discounts', { params }),
  getById: (id) => api.get(`/discounts/${id}`),
  search: (query) => api.get('/discounts/search', { params: { q: query } }),
  getCategories: () => api.get('/categories'),
  getStores: () => api.get('/stores'),
  getPersonal: () => api.get('/discounts/personal'),
  getBankOffers: () => api.get('/discounts/bank-offers'),
}

export const collectionAPI = {
  getAll: () => api.get('/collections'),
  create: (data) => api.post('/collections', data),
  getById: (id) => api.get(`/collections/${id}`),
  update: (id, data) => api.put(`/collections/${id}`, data),
  delete: (id) => api.delete(`/collections/${id}`),
  share: (id) => api.post(`/collections/${id}/share`),
}

export const familyCardAPI = {
  get: () => api.get('/family-card'),
  create: (data) => api.post('/family-card', data),
  addMember: (data) => api.post('/family-card/members', data),
  removeMember: (memberId) => api.delete(`/family-card/members/${memberId}`),
  getMembers: () => api.get('/family-card/members'),
}

export const catalogAPI = {
  getAll: () => api.get('/catalogs'),
  getByStore: (storeId) => api.get(`/catalogs/store/${storeId}`),
  getById: (id) => api.get(`/catalogs/${id}`),
}

export const subscriptionAPI = {
  getPlans: () => api.get('/subscriptions/plans'),
  getCurrent: () => api.get('/subscriptions/current'),
  subscribe: (planId) => api.post('/subscriptions/subscribe', { plan_id: planId }),
  cancel: () => api.post('/subscriptions/cancel'),
}

export default api
