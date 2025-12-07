// src/api/admin.js
import apiClient from './http'

// ===== USERS =====

// список пользователей (фильтры: role, search)
export function adminGetUsers(params = {}) {
  return apiClient.get('/api/admin/users/', { params })
}

// Поиск пользователя по email
export function adminSearchUserByEmail(email) {
  return apiClient.get('/api/admin/users/by-email/', { params: { email } })
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

// ===== AUDIT LOGS =====

// получить список логов (поддерживает search, ordering, page — если включена пагинация)
export function adminGetAuditLogs(params = {}) {
  return apiClient.get('/api/admin/audit/', { params })
}
