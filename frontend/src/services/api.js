import axios from 'axios'
import { API_BASE } from '../utils/constants'

const client = axios.create({ baseURL: API_BASE, timeout: 15000 })

client.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err.response?.data || err.message)
)

export default client
