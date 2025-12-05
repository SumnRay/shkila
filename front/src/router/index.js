// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../pages/auth/LoginView.vue'
import RegisterView from '../pages/auth/RegisterView.vue'
import LandingPage from '../pages/common/LandingPage.vue'
import EditProfileView from '../pages/common/EditProfileView.vue'
import ApplicantDashboardView from '../pages/applicant/ApplicantDashboardView.vue'
import AdminDashboardView from '../pages/admin/AdminDashboardView.vue'
import AdminScheduleView from '../pages/admin/AdminScheduleView.vue'
import AdminLogsView from '../pages/admin/AdminLogsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: LandingPage,
    meta: { guestOnly: false },
  },
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
    path: '/applicant',
    name: 'applicant-dashboard',
    component: ApplicantDashboardView,
    meta: { requiresAuth: true, roles: ['applicant'] },
  },
  {
    path: '/edit-profile',
    name: 'edit-profile',
    component: EditProfileView,
    meta: { requiresAuth: true, roles: ['applicant'] },
  },
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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // страница только для гостей (login/register)
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next({ name: 'home' })
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
      return next({ name: 'home' })
    }
  }

  return next()
})

export default router
