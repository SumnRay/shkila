<!-- src/pages/common/LandingPage.vue -->
<template>
  <div class="home-page">
    <!-- Верхняя навигация -->
    <nav class="top-nav">
      <div class="nav-left">
        <div class="logo">PROGKIDS</div>
        <div class="lang-switcher">EN | RU</div>
      </div>
      <div class="nav-right">
        <div v-if="auth.isAuthenticated" class="user-menu">
          <span class="user-name">{{ auth.user?.email || 'Пользователь' }}</span>
          <div class="user-dropdown">
            <router-link 
              v-if="auth.normalizedRole === 'admin'"
              :to="{ name: 'admin-dashboard' }" 
              class="dropdown-item"
            >
              Админ панель
            </router-link>
            <router-link 
              v-if="auth.normalizedRole === 'manager'"
              :to="{ name: 'manager-dashboard' }" 
              class="dropdown-item"
            >
              Панель менеджера
            </router-link>
            <router-link 
              v-if="auth.normalizedRole === 'applicant'"
              :to="{ name: 'applicant-dashboard' }" 
              class="dropdown-item"
            >
              Личный кабинет
            </router-link>
            <router-link 
              v-if="auth.normalizedRole === 'student'"
              :to="{ name: 'student-dashboard' }" 
              class="dropdown-item"
            >
              Личный кабинет
            </router-link>
            <button @click="handleLogout" class="dropdown-item">Выйти</button>
          </div>
        </div>
        <div v-else class="auth-buttons">
          <router-link :to="{ name: 'login' }" class="nav-btn">Войти</router-link>
          <router-link :to="{ name: 'register' }" class="nav-btn primary">Регистрация</router-link>
        </div>
      </div>
    </nav>

    <div class="main-layout">
      <!-- Боковое меню -->
      <aside class="sidebar">
        <div class="sidebar-section">
          <h3 class="sidebar-title">ДОСТУПНЫЕ КУРСЫ:</h3>
          <div class="course-filters">
            <div class="filter-item active">ВСЕ КУРСЫ</div>
            <div class="filter-item">Snap!</div>
            <div class="filter-item">python™</div>
            <div class="filter-item">SCRATCH</div>
          </div>
        </div>
        <div class="sidebar-section">
          <h3 class="sidebar-title">Другие Курсы</h3>
          <div class="other-courses">
            <button class="other-course-btn">ChatGPT</button>
            <button class="other-course-btn">Пригласить друга</button>
            <button class="other-course-btn">Галерея Проектов</button>
          </div>
        </div>
      </aside>

      <!-- Основной контент -->
      <main class="main-content">
        <div class="content-header">
          <h1 class="page-title">
            ВСЕ КУРСЫ
            <span class="course-count">{{ courses.length }}</span>
          </h1>
          <p class="page-description">
            На этой странице представлены все курсы доступные на нашей платформе в данный момент.
          </p>
          <!-- Кнопка для админов и менеджеров -->
          <div v-if="auth.isAuthenticated && (auth.normalizedRole === 'admin' || auth.normalizedRole === 'manager')" class="admin-button-container">
            <router-link 
              v-if="auth.normalizedRole === 'admin'"
              :to="{ name: 'admin-dashboard' }" 
              class="admin-panel-btn"
            >
              ⚙️ Перейти в админ панель
            </router-link>
            <router-link 
              v-if="auth.normalizedRole === 'manager'"
              :to="{ name: 'manager-dashboard' }" 
              class="admin-panel-btn"
            >
              ⚙️ Перейти в панель менеджера
            </router-link>
          </div>
        </div>

        <div v-if="loading" class="loading">Загрузка курсов...</div>
        <div v-else-if="courses.length === 0" class="empty">Курсы пока не добавлены</div>
        <div v-else class="courses-grid">
          <div v-for="course in courses" :key="course.id" class="course-card">
            <div class="course-badge" v-if="course.default_lessons">
              <span class="badge-number">{{ course.default_lessons }}</span>
              <span class="badge-label">НОВИЧОК</span>
            </div>
            <div class="course-tag">SNAP</div>
            <h3 class="course-title">{{ course.title }}</h3>
            <p v-if="course.description" class="course-description">{{ course.description }}</p>
            <div class="course-meta">
              <span class="difficulty">Сложность: 2/10</span>
              <div class="course-status">
                <span class="status-icon unlocked">🔓</span>
                <span class="lessons-count">{{ course.default_lessons || 0 }}</span>
              </div>
            </div>
            <button class="course-btn">НАЧАТЬ</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import apiClient from '../../api/http'

const auth = useAuthStore()
const router = useRouter()
const courses = ref([])
const loading = ref(false)

const fetchCourses = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/api/applicant/courses/public/')
    courses.value = data
  } catch (err) {
    console.error('Ошибка загрузки курсов:', err)
    courses.value = []
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'home' })
}

onMounted(() => {
  fetchCourses()
  if (auth.isAuthenticated && !auth.user) {
    auth.fetchMe()
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.top-nav {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: #42b983;
}

.lang-switcher {
  color: #666;
  font-size: 0.9rem;
  cursor: pointer;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

.nav-btn {
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
  color: #333;
  background: #fff;
}

.nav-btn.primary {
  background: #42b983;
  color: #fff;
  border-color: #42b983;
}

.nav-btn:hover {
  background: #f5f5f5;
}

.nav-btn.primary:hover {
  background: #35a372;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.user-name {
  padding: 8px 16px;
  color: #333;
  font-weight: 500;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  margin-top: 8px;
  display: none;
}

.user-menu:hover .user-dropdown {
  display: block;
}

.dropdown-item {
  display: block;
  padding: 12px 16px;
  text-decoration: none;
  color: #333;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.main-layout {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  gap: 24px;
  padding: 24px;
}

.sidebar {
  width: 280px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  height: fit-content;
  position: sticky;
  top: 80px;
}

.sidebar-section {
  margin-bottom: 32px;
}

.sidebar-title {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.course-filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  color: #333;
}

.filter-item.active {
  background: #42b983;
  color: #fff;
  font-weight: 600;
}

.filter-item:hover:not(.active) {
  background: #f5f5f5;
}

.other-courses {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.other-course-btn {
  padding: 10px 12px;
  border-radius: 6px;
  border: none;
  background: #42b983;
  color: #fff;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
  text-align: left;
}

.other-course-btn:hover {
  background: #35a372;
}

.main-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 32px;
}

.content-header {
  background: #42b983;
  color: #fff;
  padding: 24px 32px;
  border-radius: 8px;
  margin-bottom: 32px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 16px;
}

.course-count {
  background: #ffc107;
  color: #000;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 1.5rem;
  font-weight: 700;
}

.page-description {
  margin: 0;
  font-size: 1rem;
  opacity: 0.95;
}

.admin-button-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.admin-panel-btn {
  display: inline-block;
  padding: 14px 28px;
  background: #ffc107;
  color: #000;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

.admin-panel-btn:hover {
  background: #ffb300;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 193, 7, 0.4);
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.course-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;
}

.course-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.course-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #ffc107;
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.badge-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: #000;
}

.badge-label {
  font-size: 0.7rem;
  color: #000;
  font-weight: 600;
}

.course-tag {
  display: inline-block;
  background: #ffc107;
  color: #000;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.course-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #333;
}

.course-description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 16px;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.difficulty {
  font-size: 0.85rem;
  color: #666;
}

.course-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-icon {
  font-size: 1.2rem;
}

.lessons-count {
  background: #42b983;
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.course-btn {
  width: 100%;
  padding: 12px;
  background: #42b983;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.course-btn:hover {
  background: #35a372;
}

.loading,
.empty {
  text-align: center;
  padding: 48px;
  color: #666;
  font-size: 1.1rem;
}

@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    position: static;
  }
}

@media (max-width: 768px) {
  .top-nav {
    flex-direction: column;
    gap: 12px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 1.75rem;
  }
}
</style>
