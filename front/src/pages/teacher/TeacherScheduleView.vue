<!-- src/pages/teacher/TeacherScheduleView.vue -->
<template>
  <div class="teacher-schedule-page">
    <TopNavigationBar />

    <main class="teacher-main">
      <div class="page-header">
        <div class="title-block">
          <h1>Расписание занятий</h1>
          <p class="subtitle">
            Проставляйте расписание занятий для ваших учеников.
          </p>
        </div>
      </div>
      <ScheduleView
        :lessons="lessons"
        :lessons-loading="lessonsLoading"
        :lessons-error="lessonsError"
        :on-create-lesson="handleCreateLesson"
        :on-update-lesson="handleUpdateLesson"
        :on-search-user="handleSearchUser"
        :on-get-autocomplete="handleGetAutocomplete"
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
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import { teacherGetLessons, teacherCreateLesson, teacherUpdateLesson, teacherSearchStudentByEmail, teacherGetStudentsAutocomplete } from '../../api/teacher'

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
    const response = await teacherUpdateLesson(lessonId, payload)
    await loadLessons()
    // Возвращаем обновленный урок из ответа API
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
    const { data } = await teacherSearchStudentByEmail(email)
    return data
  } catch (err) {
    console.error('search student error:', err)
    throw err
  }
}

const handleGetAutocomplete = async (role, search = '') => {
  try {
    // Для учителя role игнорируется, всегда возвращаем учеников
    const { data } = await teacherGetStudentsAutocomplete(search)
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
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

.teacher-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 10px;
}

.title-block h1 {
  font-size: 22px;
  font-weight: 900;
  color: #FFFFFF;
  margin: 0;
  letter-spacing: -1px;
}

.subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
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
  padding: 4px 12px;
  border-radius: 16px;
  border: 1px solid #FFD700;
  font-size: 11px;
  text-transform: uppercase;
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  font-weight: 700;
}

.teacher-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  cursor: pointer;
  background: transparent;
  color: #FFD700;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  font-family: inherit;
}

.btn.secondary {
  background: transparent;
  border-color: #FFD700;
  color: #FFD700;
}

.btn:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.teacher-main {
  width: 100%;
  max-width: 100%;
}

.page-header {
  padding: 20px 24px 0;
  margin-bottom: 24px;
}

.page-header .title-block h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  color: #e8eaf6;
  letter-spacing: -1px;
}

.page-header .subtitle {
  margin-top: 8px;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
  }

  .page-header .title-block h1 {
    font-size: 2rem;
  }

  .page-header .subtitle {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 12px 0;
  }

  .page-header .title-block h1 {
    font-size: 1.5rem;
  }

  .page-header .subtitle {
    font-size: 0.85rem;
  }
}
</style>
