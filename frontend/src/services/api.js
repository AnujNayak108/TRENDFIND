import axios from 'axios'

// Normalize VITE_API_URL so deployments that set only the domain still work
const rawApiUrl = (import.meta.env.VITE_API_URL || '').trim()
const API_BASE_URL = rawApiUrl
  ? rawApiUrl.replace(/\/+$/,'') + '/api/v1' // ensure it ends with /api/v1
  : '/api/v1'

console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s timeout - scraping across multiple sources takes time
})

export const trendsAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/trends', { params })
    return response.data
  },
  getById: async (id) => {
    const response = await api.get(`/trends/${id}`)
    return response.data
  },
}

export const productsAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/products', { params })
    return response.data
  },
  getById: async (id) => {
    // Validate ID before making request
    if (!id || id === 'undefined' || id === 'null') {
      throw new Error('Invalid product ID')
    }
    const response = await api.get(`/products/${id}`)
    return response.data
  },
}

export const scrapeAPI = {
  run: async () => {
    const response = await api.post('/scrape/run')
    return response.data
  },
  getStatus: async () => {
    const response = await api.get('/scrape/status')
    return response.data
  },
}

export default api

