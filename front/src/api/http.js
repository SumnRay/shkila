// src/api/http.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000', // твой бэк
  withCredentials: false,
})

// подставляем access-токен из localStorage
apiClient.interceptors.request.use((config) => {
  const access = localStorage.getItem('access')
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

export default apiClient
