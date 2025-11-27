// src/api/admin.js
import apiClient from './http'

// список пользователей (фильтры: role, search)
export function adminGetUsers(params = {}) {
  return apiClient.get('/api/admin/users/', { params })
}

// обновление данных пользователя (email, phone, ФИО и т.п.)
export function adminUpdateUser(id, payload) {
  return apiClient.patch(`/api/admin/users/${id}/`, payload)
}

// удаление пользователя
export function adminDeleteUser(id) {
  return apiClient.delete(`/api/admin/users/${id}/`)
}

// смена роли пользователя
export function adminSetUserRole(id, role) {
  return apiClient.patch(`/api/admin/users/${id}/set-role/`, { role })
}
