// src/api/auth.js
import apiClient from './http'

// регистрация пользователя
export function registerApi(payload) {
  // payload должен содержать:
  // email, phone, student_full_name, parent_full_name, password, parent_password
  return apiClient.post('/auth/register/', payload)
}

// обычный логин (НЕ админский)
export function loginApi({ email, password }) {
  return apiClient.post('/auth/login/', { email, password })
}

// инфа о текущем пользователе по токену
export function getMeApi() {
  return apiClient.get('/auth/me/')
}

// админ-логин (если нужно отдельное окно)
export function adminLoginApi({ email, password }) {
  return apiClient.post('/auth/admin-login/', { email, password })
}
