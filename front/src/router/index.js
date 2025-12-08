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
import AdminCoursesView from '../pages/admin/AdminCoursesView.vue'
import ManagerScheduleView from '../pages/manager/ManagerScheduleView.vue'
import ManagerBalanceView from '../pages/manager/ManagerBalanceView.vue'
import TeacherDashboardView from '../pages/teacher/TeacherDashboardView.vue'
import TeacherScheduleView from '../pages/teacher/TeacherScheduleView.vue'
import StudentDashboardView from '../pages/student/StudentDashboardView.vue'
import PaymentCalculatorView from '../pages/common/PaymentCalculatorView.vue'

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
    meta: { requiresAuth: true, roles: ['applicant', 'student'] },
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
  {
    path: '/admin/courses',
    name: 'admin-courses',
    component: AdminCoursesView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/manager/schedule',
    name: 'manager-schedule',
    component: ManagerScheduleView,
    meta: { requiresAuth: true, roles: ['manager'] },
  },
  {
    path: '/manager/balance/:studentId?',
    name: 'manager-balance',
    component: ManagerBalanceView,
    meta: { requiresAuth: true, roles: ['manager'] },
  },
  {
    path: '/teacher',
    name: 'teacher-dashboard',
    component: TeacherDashboardView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/teacher/schedule',
    name: 'teacher-schedule',
    component: TeacherScheduleView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/student',
    name: 'student-dashboard',
    component: StudentDashboardView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/payment',
    name: 'payment-calculator',
    component: PaymentCalculatorView,
    meta: { requiresAuth: true, roles: ['student', 'applicant'] },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // страница только для гостей (login/register)
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next({ name: 'home' })
  }

  // требуется авторизация
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Если требуется авторизация и есть токен, но пользователь еще не загружен
  // дожидаемся загрузки пользователя перед проверкой роли
  if (to.meta.requiresAuth && auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch (err) {
      // Если не удалось загрузить пользователя, редиректим на логин
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
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
