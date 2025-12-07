// src/api/student.js
import apiClient from './http'

// Получить данные личного кабинета ученика
export function studentGetDashboard() {
  return apiClient.get('/api/student/dashboard/')
}

// Получить список курсов
export function studentGetCourses() {
  return apiClient.get('/api/student/courses/')
}

// Получить список уроков
export function studentGetLessons(params = {}) {
  return apiClient.get('/api/student/lessons/', { params })
}

// Получить баланс
export function studentGetBalance() {
  return apiClient.get('/api/student/balance/')
}

// Получить историю платежей
export function studentGetPayments() {
  return apiClient.get('/api/student/payments/')
}

// Создать платеж
export function studentCreatePayment(payload) {
  return apiClient.post('/api/student/payments/create/', payload)
}

// Получить краткую информацию о сезоне
export function studentGetSeasonSummary() {
  return apiClient.get('/api/student/season/summary/')
}

