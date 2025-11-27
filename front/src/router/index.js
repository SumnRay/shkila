// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../pages/auth/LoginView.vue'
import RegisterView from '../pages/auth/RegisterView.vue'
import HomeView from '../pages/common/HomeView.vue'

import AdminDashboardView from '../pages/admin/AdminDashboardView.vue'
import AdminScheduleView from '../pages/admin/AdminScheduleView.vue'
import AdminLogsView from '../pages/admin/AdminLogsView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guestOnly: true },
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },

  // ===== АДМИНКА =====
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/schedule',
    name: 'admin-schedule',
    component: AdminScheduleView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/logs',
    name: 'admin-logs',
    component: AdminLogsView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },

  // заглушки для других ролей
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

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // страница только для гостей (login/register)
  if (to.meta.guestOnly && auth.isAuthenticated) {
    const target = auth.getRedirectRouteByRole
      ? auth.getRedirectRouteByRole()
      : { name: 'home' }
    return next(target)
  }

  // требуется авторизация
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // ограничение по ролям
  if (to.meta.roles && to.meta.roles.length > 0) {
    const role = auth.normalizedRole
    const allowed = to.meta.roles.map((r) => r.toLowerCase())
    if (!allowed.includes((role || '').toLowerCase())) {
      const target = auth.getRedirectRouteByRole
        ? auth.getRedirectRouteByRole()
        : { name: 'home' }
      return next(target)
    }
  }

  return next()
})

export default router
