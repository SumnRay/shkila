<!-- src/pages/student/StudentDashboardView.vue -->
<template>
  <div class="student-dashboard">
    <!-- Верхняя навигация -->
    <nav class="top-nav-bar">
      <div class="nav-left">
        <router-link :to="{ name: 'home' }" class="nav-link">На главную</router-link>
        <router-link :to="{ name: 'payment-calculator' }" class="nav-link">Оплатить занятие</router-link>
        <router-link :to="{ name: 'home' }" class="nav-link">Мои курсы</router-link>
      </div>
      <div class="nav-right">
        <button class="logout-btn" @click="handleLogout">Выход</button>
      </div>
    </nav>

    <div class="dashboard-content">
      <div class="main-grid">
        <!-- Левая колонка -->
        <div class="left-column">
          <!-- Профиль пользователя -->
          <div class="card profile-card">
            <div class="profile-avatar">
              <svg viewBox="0 0 100 100" class="avatar-icon">
                <circle cx="50" cy="50" r="50" fill="rgba(255, 255, 255, 0.1)"/>
                <circle cx="50" cy="35" r="15" fill="rgba(255, 255, 255, 0.8)"/>
                <path d="M 20 85 Q 20 65 50 65 Q 80 65 80 85" fill="rgba(255, 255, 255, 0.8)"/>
              </svg>
            </div>
            <div class="profile-info">
              <div class="profile-name">{{ dashboardData?.student_full_name || auth.user?.student_full_name || 'Ученик' }}</div>
              <div class="profile-email">{{ dashboardData?.email || auth.user?.email || '—' }}</div>
            </div>
            <router-link :to="{ name: 'edit-profile' }" class="edit-btn">
              Редактировать
            </router-link>
          </div>

          <!-- Осталось занятий -->
          <div class="card balance-section">
            <div class="section-title">Осталось занятий</div>
            <div class="balance-cards">
              <div class="balance-card">
                <div class="balance-label">Осталось занятий: {{ dashboardData?.balance || 0 }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Правая колонка -->
        <div class="right-column">
          <!-- Следующие запланированные занятия -->
          <div class="card schedule-card">
            <h2 class="schedule-title">Следующие запланированные занятия</h2>
            <div v-if="lessonsLoading" class="loading">Загрузка...</div>
            <div v-else-if="lessonsError" class="error">{{ lessonsError }}</div>
            <div v-else-if="upcomingLessons.length === 0" class="empty">
              Нет запланированных занятий
            </div>
            <div v-else class="schedule-list">
              <div 
                v-for="(lesson, index) in upcomingLessons" 
                :key="lesson.id" 
                class="schedule-item"
              >
                <div class="schedule-date">
                  {{ formatDate(lesson.scheduled_at) }} в {{ formatTime(lesson.scheduled_at) }}
                </div>
                <div class="schedule-course">Курс: {{ lesson.course || '—' }}</div>
                <div class="schedule-teacher">Преподаватель: {{ lesson.teacher_email || 'Не назначен' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Кнопка "Задать вопрос" -->
    <button class="floating-btn" @click="showRequestForm = true">
      Задать вопрос
    </button>

    <!-- Форма обращения к менеджеру -->
    <ManagerRequestForm
      :show="showRequestForm"
      :on-submit="handleCreateRequest"
      @close="showRequestForm = false"
      @success="handleRequestSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ManagerRequestForm from '../../components/ManagerRequestForm.vue'
import { studentGetDashboard, studentGetLessons, studentCreateRequest } from '../../api/student'

const auth = useAuthStore()
const router = useRouter()

const dashboardData = ref(null)
const dashboardLoading = ref(false)
const dashboardError = ref(null)

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

const showRequestForm = ref(false)

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
      return lessonDate >= now && lesson.status === 'PLANNED'
    })
    .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at))
    .slice(0, 3) // Максимум 3 занятия
})

const formatDate = (dateString) => {
  if (!dateString) return 'дд.мм.гг'
  const d = new Date(dateString)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
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

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'home' })
}

const handleCreateRequest = async (payload) => {
  await studentCreateRequest(payload)
}

const handleRequestSuccess = () => {
  showRequestForm.value = false
  console.log('Обращение успешно отправлено')
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
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding-bottom: 100px;
}

/* Верхняя навигация */
.top-nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 215, 0, 0.2);
  padding: 12px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-left {
  display: flex;
  gap: 24px;
  align-items: center;
}

.nav-link {
  color: #FFFFFF;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 4px 0;
}

.nav-link:hover {
  color: #FFD700;
}

.logout-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFFFFF;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.logout-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: start;
}

/* Карточки */
.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

/* Профиль */
.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  background: rgba(60, 60, 60, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #FFD700;
}

.avatar-icon {
  width: 60px;
  height: 60px;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #FFFFFF;
}

.profile-email {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
}

.edit-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFFFFF;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.edit-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

/* Секции */
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 16px;
}

.balance-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.balance-card {
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.balance-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-weight: 600;
}

/* Расписание */
.schedule-card {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.schedule-title {
  font-size: 2rem;
  font-weight: 900;
  color: #FFFFFF;
  text-align: center;
  margin: 0 0 24px 0;
  padding: 0;
}

.schedule-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.schedule-date {
  font-weight: 600;
  color: #FFFFFF;
  font-size: 0.95rem;
}

.schedule-course,
.schedule-teacher {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.schedule-more {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.more-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFD700;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.more-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

/* Floating button */
.floating-btn {
  position: fixed;
  bottom: 32px;
  right: 32px;
  padding: 14px 28px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  z-index: 50;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.floating-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

/* Состояния */
.loading,
.empty,
.error {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
}

.error {
  color: #ffaaaa;
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

  .top-nav-bar {
    padding: 10px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .nav-left {
    gap: 16px;
  }

  .nav-link {
    font-size: 0.85rem;
  }

  .profile-card {
    flex-direction: column;
    text-align: center;
  }

  .floating-btn {
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    font-size: 0.9rem;
  }
}
</style>
