<!-- src/pages/student/StudentDashboardView.vue -->
<template>
  <div class="student-dashboard">
    <TopNavigationBar />

    <div class="dashboard-content">
      <!-- Статистика вверху -->
      <div class="stats-section">
        <div class="stat-card balance-card">
          <div class="stat-icon">📚</div>
          <div class="stat-content">
            <div class="stat-label">Доступно уроков</div>
            <div class="stat-value">{{ dashboardData?.balance || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Основной контент в две колонки -->
      <div class="main-grid">
        <!-- Левая колонка -->
        <div class="left-column">
          <!-- Профиль -->
          <div class="card profile-card">
            <div class="card-title">
              <span>👤</span>
              <h3>Профиль</h3>
            </div>
            <div class="profile-content">
              <div class="profile-main">
                <div class="profile-name">{{ dashboardData?.student_full_name || auth.user?.student_full_name || 'Ученик' }}</div>
                <div class="profile-email">{{ dashboardData?.email || auth.user?.email || '—' }}</div>
              </div>
              <router-link :to="{ name: 'edit-profile' }" class="btn-edit">
                Редактировать
              </router-link>
            </div>
          </div>

          <!-- Ближайшие уроки -->
          <div class="card lessons-card">
            <div class="card-title">
              <span>📅</span>
              <h3>Ближайшие уроки</h3>
              <button @click="loadLessons" class="btn-refresh" :disabled="lessonsLoading">
                {{ lessonsLoading ? '...' : '↻' }}
              </button>
            </div>
            <div v-if="lessonsLoading" class="loading">Загрузка...</div>
            <div v-else-if="lessonsError" class="error">{{ lessonsError }}</div>
            <div v-else-if="upcomingLessons.length === 0" class="empty">
              Нет запланированных уроков
            </div>
            <div v-else class="lessons-list">
              <div v-for="lesson in upcomingLessons" :key="lesson.id" class="lesson-item">
                <div class="lesson-time">{{ formatTime(lesson.scheduled_at) }}</div>
                <div class="lesson-date">{{ formatDate(lesson.scheduled_at) }}</div>
                <div class="lesson-teacher">{{ lesson.teacher_email || 'Не назначен' }}</div>
                <div v-if="lesson.link" class="lesson-link">
                  <a :href="lesson.link" target="_blank" class="link-btn">Ссылка</a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Правая колонка -->
        <div class="right-column">
          <!-- История занятий -->
          <LessonHistory />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import LessonHistory from '../../components/LessonHistory.vue'
import { studentGetDashboard, studentGetLessons } from '../../api/student'

const auth = useAuthStore()
const router = useRouter()

const dashboardData = ref(null)
const dashboardLoading = ref(false)
const dashboardError = ref(null)

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

const loadDashboard = async () => {
  dashboardLoading.value = true
  dashboardError.value = null
  try {
    const { data } = await studentGetDashboard()
    dashboardData.value = data
  } catch (err) {
    console.error('load dashboard error:', err)
    dashboardError.value = 'Не удалось загрузить данные'
  } finally {
    dashboardLoading.value = false
  }
}

const loadLessons = async () => {
  lessonsLoading.value = true
  lessonsError.value = null
  try {
    const { data } = await studentGetLessons({
      status: 'PLANNED',
      ordering: 'scheduled_at'
    })
    lessons.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load lessons error:', err)
    lessonsError.value = 'Не удалось загрузить уроки'
  } finally {
    lessonsLoading.value = false
  }
}

const upcomingLessons = computed(() => {
  const now = new Date()
  return lessons.value
    .filter(lesson => {
      if (!lesson.scheduled_at) return false
      const lessonDate = new Date(lesson.scheduled_at)
      return lessonDate >= now
    })
    .slice(0, 5) // Показываем только ближайшие 5 уроков
})

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
  })
}

const formatTime = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusText = (status) => {
  const statusMap = {
    'PLANNED': 'Запланировано',
    'DONE': 'Проведено',
    'CANCELLED': 'Отменено',
  }
  return statusMap[status] || status
}


onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }

  if (!auth.user && auth.isAuthenticated) {
    await auth.fetchMe()
  }

  await loadDashboard()
  await loadLessons()
})
</script>

<style scoped>
.student-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  position: relative;
}

.student-dashboard::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
  position: relative;
  z-index: 1;
}

/* Статистика вверху */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(76, 68, 118, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  background: rgba(76, 68, 118, 0.95);
  border-color: rgba(102, 126, 234, 0.6);
}

.stat-card.balance-card {
  background: rgba(102, 126, 234, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  color: #ffffff;
  border: 1px solid rgba(102, 126, 234, 0.6);
}

.stat-icon {
  font-size: 2.5rem;
  line-height: 1;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.85rem;
  margin-bottom: 4px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.balance-card .stat-label {
  color: rgba(255, 255, 255, 0.9);
  opacity: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.balance-card .stat-value {
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Основная сетка */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
}

/* Карточки */
.card {
  background: rgba(76, 68, 118, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  background: rgba(76, 68, 118, 0.95);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.6);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.card-title span {
  font-size: 1.5rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.card-title h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #ffffff;
  flex: 1;
  font-weight: 800;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 1.2rem;
  color: #ffffff;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: rotate(180deg);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Профиль */
.profile-card {
  margin-bottom: 24px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.profile-email {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.85);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.btn-edit {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  text-align: center;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.btn-edit:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* Уроки */
.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lesson-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  border-left: 4px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.lesson-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.lesson-time {
  font-weight: 700;
  font-size: 1.1rem;
  color: #ffffff;
  min-width: 60px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.lesson-date {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.85);
  min-width: 80px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.lesson-teacher {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.lesson-link {
  min-width: 80px;
}

.link-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.2);
}

.link-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

.loading,
.empty,
.error {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.error {
  color: #ffb3b3;
  font-weight: 600;
  text-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
}

/* Адаптивность */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 20px 16px;
  }

  .stats-section {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .lesson-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .lesson-time {
    min-width: auto;
  }

  .lesson-date {
    min-width: auto;
  }

  .lesson-link {
    width: 100%;
  }

  .link-btn {
    display: block;
    text-align: center;
  }
}
</style>


