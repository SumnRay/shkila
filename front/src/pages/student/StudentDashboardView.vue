<!-- src/pages/student/StudentDashboardView.vue -->
<template>
  <div class="student-dashboard">
    <header class="dashboard-header">
      <div class="header-content">
        <h1>Личный кабинет</h1>
        <div class="header-actions">
          <router-link :to="{ name: 'home' }" class="btn-back">← На главную</router-link>
          <button @click="handleLogout" class="btn-logout">Выйти</button>
        </div>
      </div>
    </header>

    <div class="dashboard-content">
      <!-- Профиль и баланс -->
      <div class="profile-card card">
        <h2>Профиль</h2>
        <div class="profile-info">
          <div class="info-item">
            <span class="label">Email:</span>
            <span class="value">{{ dashboardData?.email || auth.user?.email || '—' }}</span>
          </div>
          <div class="info-item" v-if="auth.user?.phone">
            <span class="label">Телефон:</span>
            <span class="value">{{ auth.user.phone }}</span>
          </div>
          <div class="info-item" v-if="dashboardData?.student_full_name || auth.user?.student_full_name">
            <span class="label">ФИО ученика:</span>
            <span class="value">{{ dashboardData?.student_full_name || auth.user?.student_full_name }}</span>
          </div>
          <div class="info-item" v-if="auth.user?.parent_full_name">
            <span class="label">ФИО родителя:</span>
            <span class="value">{{ auth.user.parent_full_name }}</span>
          </div>
        </div>
        <div class="profile-actions">
          <router-link :to="{ name: 'edit-profile' }" class="btn-edit">
            Редактировать профиль
          </router-link>
        </div>
      </div>

      <!-- Баланс и статистика -->
      <div class="stats-card card">
        <h2>Баланс и статистика</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Доступно уроков</span>
            <span class="stat-value balance">{{ dashboardData?.balance || 0 }}</span>
          </div>
          <div class="stat-item" v-if="dashboardData">
            <span class="stat-label">Уровень</span>
            <span class="stat-value level">{{ dashboardData.level || 1 }}</span>
          </div>
          <div class="stat-item" v-if="dashboardData">
            <span class="stat-label">Опыт (XP)</span>
            <span class="stat-value xp">{{ dashboardData.xp || 0 }}</span>
          </div>
          <div class="stat-item" v-if="dashboardData">
            <span class="stat-label">Валюта сезона</span>
            <span class="stat-value currency">{{ dashboardData.season_currency || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- Ближайшие уроки -->
      <div class="lessons-card card">
        <div class="card-header">
          <h2>Ближайшие уроки</h2>
          <button @click="loadLessons" class="btn-refresh" :disabled="lessonsLoading">
            {{ lessonsLoading ? 'Загрузка...' : 'Обновить' }}
          </button>
        </div>
        <div v-if="lessonsLoading" class="loading">Загрузка уроков...</div>
        <div v-else-if="lessonsError" class="error">{{ lessonsError }}</div>
        <div v-else-if="upcomingLessons.length === 0" class="empty">
          У вас пока нет запланированных уроков
        </div>
        <div v-else class="lessons-list">
          <div v-for="lesson in upcomingLessons" :key="lesson.id" class="lesson-item">
            <div class="lesson-date">
              {{ formatDateTime(lesson.scheduled_at) }}
            </div>
            <div class="lesson-info">
              <div class="lesson-teacher">
                Преподаватель: {{ lesson.teacher_email || 'Не назначен' }}
              </div>
              <div class="lesson-status" :class="'status-' + lesson.status.toLowerCase()">
                {{ getStatusText(lesson.status) }}
              </div>
            </div>
            <div v-if="lesson.link" class="lesson-link">
              <a :href="lesson.link" target="_blank" class="link-btn">Перейти к уроку</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
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

const getStatusText = (status) => {
  const statusMap = {
    'PLANNED': 'Запланировано',
    'DONE': 'Проведено',
    'CANCELLED': 'Отменено',
  }
  return statusMap[status] || status
}

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'home' })
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
  background: #f5f5f5;
}

.dashboard-header {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 20px 0;
  margin-bottom: 32px;
}

.header-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 1.75rem;
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-back {
  padding: 10px 20px;
  background: transparent;
  color: #42b983;
  border: 1px solid #42b983;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: #42b983;
  color: #fff;
}

.btn-logout {
  padding: 10px 20px;
  background: transparent;
  color: #ff6b6b;
  border: 1px solid #ff6b6b;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background: #ff6b6b;
  color: #fff;
}

.dashboard-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px 48px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 32px;
}

.profile-card {
  grid-column: 1 / -1;
}

.stats-card {
  grid-column: 1 / -1;
}

.lessons-card {
  grid-column: 1 / -1;
}

.card h2 {
  margin: 0 0 24px 0;
  font-size: 1.5rem;
  color: #333;
  border-bottom: 2px solid #42b983;
  padding-bottom: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 2px solid #42b983;
  padding-bottom: 12px;
}

.card-header h2 {
  margin: 0;
  border: none;
  padding: 0;
}

.btn-refresh {
  padding: 8px 16px;
  background: #42b983;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #35a372;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #666;
  font-weight: 500;
}

.value {
  color: #333;
  font-weight: 600;
}

.profile-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.btn-edit {
  display: inline-block;
  padding: 12px 24px;
  background: #42b983;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-edit:hover {
  background: #35a372;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
}

.stat-value.balance {
  color: #42b983;
}

.stat-value.level {
  color: #1e88e5;
}

.stat-value.xp {
  color: #ff9800;
}

.stat-value.currency {
  color: #9c27b0;
}

.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #42b983;
}

.lesson-date {
  font-weight: 600;
  color: #333;
  min-width: 180px;
}

.lesson-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lesson-teacher {
  color: #666;
  font-size: 0.9rem;
}

.lesson-status {
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.status-planned {
  background: #e3f2fd;
  color: #1976d2;
}

.status-done {
  background: #e8f5e9;
  color: #388e3c;
}

.status-cancelled {
  background: #ffebee;
  color: #c62828;
}

.lesson-link {
  min-width: 150px;
}

.link-btn {
  padding: 8px 16px;
  background: #1e88e5;
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.link-btn:hover {
  background: #1565c0;
}

.loading,
.empty,
.error {
  text-align: center;
  padding: 32px;
  color: #666;
}

.error {
  color: #ff6b6b;
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .btn-back,
  .btn-logout {
    width: 100%;
    text-align: center;
  }

  .lesson-item {
    flex-direction: column;
    align-items: flex-start;
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

