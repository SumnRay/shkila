// src/api/http.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // бэк крутится на 8000
  withCredentials: false,
})

apiClient.interceptors.request.use((config) => {
  const access = localStorage.getItem('access')
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

export default apiClient
