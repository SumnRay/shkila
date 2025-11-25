// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../pages/auth/LoginView.vue'
import HomeView from '../pages/common/HomeView.vue'
import AdminDashboardView from '../pages/admin/AdminDashboardView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },

  // админка
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },

  // заглушки для других ролей (пока можно использовать HomeView)
  {
    path: '/student',
    name: 'student-dashboard',
    component: HomeView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/teacher',
    name: 'teacher-dashboard',
    component: HomeView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/manager',
    name: 'manager-dashboard',
    component: HomeView,
    meta: { requiresAuth: true, roles: ['manager'] },
  },
  {
    path: '/applicant',
    name: 'applicant-dashboard',
    component: HomeView,
    meta: { requiresAuth: true, roles: ['applicant'] },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // если есть токен, но нет user — пробуем подтянуть
  if (auth.access && !auth.user) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login' })
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    const target = auth.getRedirectRouteByRole()
    return next(target)
  }

  if (to.meta.roles && to.meta.roles.length > 0) {
    const role = auth.normalizedRole
    const allowed = to.meta.roles.map((r) => r.toLowerCase())
    if (!allowed.includes(role)) {
      const target = auth.getRedirectRouteByRole()
      return next(target)
    }
  }

  return next()
})

export default router
