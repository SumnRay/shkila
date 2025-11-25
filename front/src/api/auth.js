// src/api/auth.js
import apiClient from './http'

// обычный логин (НЕ админский)
export function loginApi({ email, password }) {
  return apiClient.post('/api/auth/login/', { email, password })
}

// инфа о текущем пользователе по токену
export function getMeApi() {
  return apiClient.get('/api/auth/me/')
}

// при желании можно добавить админ-логин
export function adminLoginApi({ email, password }) {
  return apiClient.post('/api/auth/admin-login/', { email, password })
}
