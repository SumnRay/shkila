<!-- src/pages/teacher/TeacherScheduleView.vue -->
<template>
  <div class="teacher-schedule-page">
    <header class="teacher-header">
      <div class="title-block">
        <h1>Расписание занятий</h1>
        <p class="subtitle">
          Проставляйте расписание занятий для ваших учеников.
        </p>
      </div>

      <div class="teacher-info" v-if="auth.user">
        <div class="teacher-user">
          <span class="teacher-email">{{ auth.user.email }}</span>
          <span class="role-badge">TEACHER</span>
        </div>

        <div class="teacher-actions">
          <button class="btn secondary" @click="goToDashboard">
            Панель учителя
          </button>
          <button class="btn" @click="handleLogout">
            Выйти
          </button>
        </div>
      </div>
    </header>

    <main class="teacher-main">
      <ScheduleView
        :lessons="lessons"
        :lessons-loading="lessonsLoading"
        :lessons-error="lessonsError"
        :on-create-lesson="handleCreateLesson"
        :on-update-lesson="handleUpdateLesson"
        :on-search-user="handleSearchUser"
        user-role="teacher"
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
import { teacherGetLessons, teacherCreateLesson, teacherUpdateLesson, teacherSearchStudentByEmail } from '../../api/teacher'

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
    const { data } = await teacherGetLessons(params)
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
    await teacherCreateLesson(payload)
    await loadLessons()
  } catch (err) {
    console.error('create lesson error:', err)
    throw err
  }
}

const handleUpdateLesson = async (lessonId, payload) => {
  try {
    await teacherUpdateLesson(lessonId, payload)
    await loadLessons()
  } catch (err) {
    console.error('update lesson error:', err)
    throw err
  }
}

const handleSearchUser = async (email, type) => {
  try {
    const { data } = await teacherSearchStudentByEmail(email)
    return data
  } catch (err) {
    console.error('search student error:', err)
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

const goToDashboard = () => {
  router.push({ name: 'teacher-dashboard' })
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
.teacher-schedule-page {
  min-height: 100vh;
  background: #0a0a0a;
  color: #f5f5f5;
  padding: 24px;
}

.teacher-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.title-block h1 {
  font-size: 26px;
  font-weight: 600;
}

.subtitle {
  margin-top: 4px;
  font-size: 14px;
  color: #aaa;
}

.teacher-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.teacher-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.teacher-email {
  font-size: 14px;
}

.role-badge {
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #444;
  font-size: 11px;
  text-transform: uppercase;
  background: #ff9800;
}

.teacher-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  background: #1e88e5;
  color: #fff;
  font-size: 13px;
}

.btn.secondary {
  background: #333;
  color: #f5f5f5;
}

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.teacher-main {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
</style>
