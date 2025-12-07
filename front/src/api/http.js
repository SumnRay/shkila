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

// Обработка 401 ошибок - автоматическое обновление токена
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Если ошибка 401 и это не запрос на обновление токена
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Если уже идет обновление токена, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refresh = localStorage.getItem('refresh')
      if (!refresh) {
        // Нет refresh токена - очищаем все и выходим
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        processQueue(error, null)
        isRefreshing = false
        return Promise.reject(error)
      }

      try {
        // Пытаемся обновить токен
        const response = await axios.post(
          `${apiClient.defaults.baseURL}/api/token/refresh/`,
          { refresh }
        )
        
        const { access } = response.data
        localStorage.setItem('access', access)
        
        // Обновляем заголовок в оригинальном запросе
        originalRequest.headers.Authorization = `Bearer ${access}`
        
        // Обрабатываем очередь
        processQueue(null, access)
        isRefreshing = false
        
        // Повторяем оригинальный запрос
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Не удалось обновить токен - очищаем все
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        processQueue(refreshError, null)
        isRefreshing = false
        
        // Если это не запрос на /api/auth/me, перенаправляем на логин
        if (!originalRequest.url.includes('/api/auth/me')) {
          // Можно добавить редирект на страницу логина, но не будем делать это здесь
          // чтобы не создавать циклических зависимостей
        }
        
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
