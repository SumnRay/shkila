<!-- src/pages/admin/AdminScheduleView.vue -->
<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>Календарь уроков</h1>

      <div class="admin-info" v-if="auth.user">
        <span>{{ auth.user.email }}</span>
        <span class="role-badge">ADMIN</span>

        <router-link class="btn" :to="{ name: 'admin-dashboard' }">
          Панель
        </router-link>

        <button class="btn" @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="admin-main">
      <ScheduleView
        :lessons="lessons"
        :lessons-loading="lessonsLoading"
        :lessons-error="lessonsError"
        :on-create-lesson="handleCreateLesson"
        :on-update-lesson="handleUpdateLesson"
        :on-search-user="handleSearchUser"
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
import { adminGetLessons, adminCreateLesson, adminUpdateLesson } from '../../api/lessons'
import { adminSearchUserByEmail } from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

function toISO(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function addDays(date, n) {
  const d = new Date(date)
  d.setDate(d.getDate() + n)
  return d
}

function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay() || 7
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - (day - 1))
  return d
}

const loadLessons = async (params = {}) => {
  lessonsLoading.value = true
  lessonsError.value = null

  try {
    const { data } = await adminGetLessons(params)
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
    await adminCreateLesson(payload)
    await loadLessons()
  } catch (err) {
    console.error('create lesson error:', err)
    throw err
  }
}

const handleUpdateLesson = async (lessonId, payload) => {
  try {
    const response = await adminUpdateLesson(lessonId, payload)
    await loadLessons()
    // Возвращаем обновленный урок из ответа или находим его в списке
    if (response?.data) {
      return response.data
    }
    // Если ответ не содержит данных, находим обновленный урок в списке
    const updatedLesson = lessons.value.find(l => l.id === lessonId)
    return updatedLesson || null
  } catch (err) {
    console.error('update lesson error:', err)
    throw err
  }
}

const handleSearchUser = async (email, type) => {
  try {
    const { data } = await adminSearchUserByEmail(email)
    return data
  } catch (err) {
    console.error('search user error:', err)
    throw err
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
  const weekStart = startOfWeek(today)
  const weekEnd = addDays(weekStart, 6)
  
  loadLessons({
    date_from: toISO(weekStart),
    date_to: toISO(weekEnd),
  })
})
</script>


<style scoped>
.admin-page {
  min-height: 100vh;
  background: #202124;
  color: #e8eaed;
  padding: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  padding: 16px 24px;
  background: #202124;
  border-bottom: 1px solid #3c4043;
}

.admin-header h1 {
  font-size: 22px;
  font-weight: 400;
  color: #e8eaed;
  margin: 0;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
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

.role-badge {
  padding: 4px 12px;
  border-radius: 16px;
  border: none;
  background: #fbbc04;
  color: #202124;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 500;
}

.admin-main {
  width: 100%;
  max-width: 100%;
}
</style>
