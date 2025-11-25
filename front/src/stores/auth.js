// src/stores/auth.js
import { defineStore } from 'pinia'
import { loginApi, getMeApi } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    user: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
    role: (state) => state.user?.role || null,
    normalizedRole() {
      return this.role ? String(this.role).toLowerCase() : null
    },
  },

  actions: {
    async login({ email, password }) {
      this.loading = true
      this.error = null
      try {
        const { data } = await loginApi({ email, password })

        // ВАЖНО: бэк возвращает { user, tokens }, а не { access, refresh }
        this.access = data.tokens.access
        this.refresh = data.tokens.refresh || null

        localStorage.setItem('access', this.access)
        if (this.refresh) {
          localStorage.setItem('refresh', this.refresh)
        }

        await this.fetchMe()
        return true
      } catch (err) {
        console.error('Login error:', err)
        this.error =
          err?.response?.data?.detail ||
          err?.response?.data?.error ||
          'Ошибка авторизации'
        this.access = null
        this.refresh = null
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      if (!this.access) return
      try {
        const { data } = await getMeApi()
        this.user = data
      } catch (err) {
        console.error('fetchMe error:', err)
        this.logout()
      }
    },

    logout() {
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },

    // маршрут, куда редиректить в зависимости от роли
    getRedirectRouteByRole() {
      switch (this.normalizedRole) {
        case 'admin':
          return { name: 'admin-dashboard' }
        case 'manager':
          return { name: 'manager-dashboard' }
        case 'teacher':
          return { name: 'teacher-dashboard' }
        case 'student':
          return { name: 'student-dashboard' }
        case 'applicant':
          return { name: 'applicant-dashboard' }
        default:
          return { name: 'home' }
      }
    },
  },
})
