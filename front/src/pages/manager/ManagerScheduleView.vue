<!-- src/pages/manager/ManagerScheduleView.vue -->
<template>
  <div class="manager-page">
    <header class="manager-header">
      <h1>Календарь уроков</h1>

      <div class="manager-info" v-if="auth.user">
        <span>{{ auth.user.email }}</span>
        <span class="role-badge">MANAGER</span>

        <router-link class="btn" :to="{ name: 'manager-dashboard' }">
          Панель
        </router-link>

        <button class="btn" @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="manager-main">
      <ScheduleView
        :lessons="lessons"
        :lessons-loading="lessonsLoading"
        :lessons-error="lessonsError"
        :on-create-lesson="handleCreateLesson"
        :on-update-lesson="handleUpdateLesson"
        :on-search-user="handleSearchUser"
        :on-get-autocomplete="handleGetAutocomplete"
        user-role="manager"
        :current-user-email="auth.user?.email || ''"
        @lesson-selected="selectLesson"
        @week-changed="handleWeekChanged"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ScheduleView from '../../components/ScheduleView.vue'
import { managerGetLessons, managerCreateLesson, managerUpdateLesson, managerSearchUserByEmail, managerGetUsersAutocomplete } from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

const loadLessons = async (params = {}) => {
  lessonsLoading.value = true
  lessonsError.value = null

  try {
    const { data } = await managerGetLessons(params)
    lessons.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load lessons error:', err)
    lessonsError.value = 'Ошибка загрузки уроков'
  } finally {
    lessonsLoading.value = false
  }
}

const handleCreateLesson = async (payload) => {
  try {
    console.log('Creating lesson with payload:', payload)
    const response = await managerCreateLesson(payload)
    console.log('Lesson created successfully:', response)
    await loadLessons()
  } catch (err) {
    console.error('create lesson error:', err)
    console.error('Error response:', err?.response?.data)
    throw err
  }
}

const handleUpdateLesson = async (lessonId, payload) => {
  try {
    await managerUpdateLesson(lessonId, payload)
    await loadLessons()
  } catch (err) {
    console.error('update lesson error:', err)
    throw err
  }
}

const handleSearchUser = async (email, type) => {
  try {
    console.log('Searching user by email:', email)
    const { data } = await managerSearchUserByEmail(email)
    console.log('User found:', data)
    return data
  } catch (err) {
    console.error('search user error:', err)
    console.error('Error response:', err?.response?.data)
    console.error('Error status:', err?.response?.status)
    // Если 401, возможно нужно перелогиниться
    if (err?.response?.status === 401) {
      console.warn('Unauthorized - token may have expired')
    }
    throw err
  }
}

const handleGetAutocomplete = async (role, search = '') => {
  try {
    const { data } = await managerGetUsersAutocomplete(role, search)
    return data
  } catch (err) {
    console.error('get autocomplete error:', err)
    return []
  }
}

const selectLesson = (lesson) => {
  console.log('Selected lesson:', lesson)
}

const handleWeekChanged = (params) => {
  loadLessons(params)
}

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  
  // Загружаем уроки на текущую неделю
  const today = new Date()
  const weekStart = new Date(today)
  const day = weekStart.getDay() || 7
  weekStart.setHours(0, 0, 0, 0)
  weekStart.setDate(weekStart.getDate() - (day - 1))
  
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekEnd.getDate() + 6)
  
  const toISO = (date) => {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  
  loadLessons({
    date_from: toISO(weekStart),
    date_to: toISO(weekEnd),
  })
})
</script>

<style scoped>
.manager-page {
  min-height: 100vh;
  background: #0a0a0a;
  color: #f5f5f5;
  padding: 24px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.manager-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 8px;
  background: #2e7d32;
  font-size: 11px;
  text-transform: uppercase;
}

.btn {
  padding: 6px 12px;
  color: white;
  background: #1e88e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  font-size: 13px;
}

.btn:hover {
  background: #1565c0;
}

.manager-main {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
</style>

