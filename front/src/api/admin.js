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

// ===== COURSES =====

// получить список курсов
export function adminGetCourses() {
  return apiClient.get('/api/admin/courses/')
}

// получить детали курса
export function adminGetCourse(id) {
  return apiClient.get(`/api/admin/courses/${id}/`)
}

// создать курс
export function adminCreateCourse(payload) {
  return apiClient.post('/api/admin/courses/', payload)
}

// обновить курс
export function adminUpdateCourse(id, payload) {
  return apiClient.patch(`/api/admin/courses/${id}/`, payload)
}

// удалить курс
export function adminDeleteCourse(id) {
  return apiClient.delete(`/api/admin/courses/${id}/`)
}

// ===== MODULES =====

// получить список модулей (можно фильтровать по course_id)
export function adminGetModules(params = {}) {
  return apiClient.get('/api/admin/modules/', { params })
}

// получить детали модуля
export function adminGetModule(id) {
  return apiClient.get(`/api/admin/modules/${id}/`)
}

// создать модуль
export function adminCreateModule(payload) {
  return apiClient.post('/api/admin/modules/', payload)
}

// обновить модуль
export function adminUpdateModule(id, payload) {
  return apiClient.patch(`/api/admin/modules/${id}/`, payload)
}

// удалить модуль
export function adminDeleteModule(id) {
  return apiClient.delete(`/api/admin/modules/${id}/`)
}

// ===== LESSON TOPICS =====

// получить список тем (можно фильтровать по module_id)
export function adminGetLessonTopics(params = {}) {
  return apiClient.get('/api/admin/lesson-topics/', { params })
}

// получить детали темы
export function adminGetLessonTopic(id) {
  return apiClient.get(`/api/admin/lesson-topics/${id}/`)
}

// создать тему
export function adminCreateLessonTopic(payload) {
  return apiClient.post('/api/admin/lesson-topics/', payload)
}

// обновить тему
export function adminUpdateLessonTopic(id, payload) {
  return apiClient.patch(`/api/admin/lesson-topics/${id}/`, payload)
}

// удалить тему
export function adminDeleteLessonTopic(id) {
  return apiClient.delete(`/api/admin/lesson-topics/${id}/`)
}
