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
  },

  actions: {
    async login({ email, password }) {
      this.loading = true
      this.error = null
      try {
        const { data } = await loginApi({ email, password })
        // ожидаем, что бэк вернёт access / refresh
        this.access = data.access
        this.refresh = data.refresh || null

        localStorage.setItem('access', this.access)
        if (this.refresh) {
          localStorage.setItem('refresh', this.refresh)
        }

        await this.fetchMe()
        return true
      } catch (err) {
        this.error =
          err.response?.data?.detail ||
          err.response?.data?.error ||
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
        // если токен мёртв — разлогиниваем
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
  },
})
