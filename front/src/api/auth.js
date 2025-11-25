// src/api/auth.js
import apiClient from './http'

export function loginApi(payload) {
  // предполагаем, что бэк ждёт email + password
  return apiClient.post('/api/auth/login/', payload)
}

export function getMeApi() {
  return apiClient.get('/api/auth/me/')
}
