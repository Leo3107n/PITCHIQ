import axios from 'axios'
import { API_BASE } from '../utils/constants'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,  // 30s — allows for Render cold starts
})

client.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const data = err.response?.data

    // If the response is HTML (e.g. Flask 404 "Cannot POST ..."), extract a clean message
    if (typeof data === 'string' && data.trim().startsWith('<')) {
      const match = data.match(/<pre>(.*?)<\/pre>/s)
      const msg = match ? match[1].trim() : 'Server error — check that the backend is running.'
      return Promise.reject({ error: msg })
    }

    // If it's a proper JSON error object
    if (data && typeof data === 'object') {
      return Promise.reject(data)
    }

    // Network error or timeout
    if (err.code === 'ECONNABORTED') {
      return Promise.reject({ error: 'Request timed out. The server may be busy.' })
    }
    if (!err.response) {
      return Promise.reject({ error: 'Cannot reach the backend. Make sure the server is running.' })
    }

    return Promise.reject({ error: err.message || 'Unknown error.' })
  }
)

export default client
