// src/api/lessons.js
import apiClient from './http'

// Получить список уроков для админ-панели
// params может содержать: date_from, date_to, status, student, teacher и т.д.
export function adminGetLessons(params = {}) {
  return apiClient.get('/api/admin/lessons/', { params })
}

// Создать новый урок
// payload:
// {
//   student: number,          // ID ученика
//   teacher: number,          // ID преподавателя
//   scheduled_at: string,     // 'YYYY-MM-DDTHH:MM:SS'
//   link?: string | null,
//   comment?: string
// }
export function adminCreateLesson(payload) {
  return apiClient.post('/api/admin/lessons/', payload)
}
