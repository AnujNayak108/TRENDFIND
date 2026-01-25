import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

