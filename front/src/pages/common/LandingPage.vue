<!-- src/pages/common/LandingPage.vue -->
<template>
  <div class="home-page">
    <TopNavigationBar />

    <!-- Верхняя навигация (старая, удаляется) -->
    <header class="top-nav" style="display: none;">
      <nav class="nav-right">
        <!-- Кнопка Администрирование для работников школы -->
        <div 
          v-if="auth.isAuthenticated && isStaffRole" 
          class="admin-menu"
        >
          <button class="admin-btn" @click="toggleAdminMenu">
            <span class="admin-btn-icon">⚙️</span>
            <span>Администрирование</span>
          </button>
          <div 
            class="admin-dropdown"
            :class="{ 'admin-dropdown-open': showAdminMenu }"
            @click.stop
          >
            <!-- Разделы для Админа -->
            <template v-if="auth.normalizedRole === 'admin'">
              <router-link :to="{ name: 'admin-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📊</span>
                <span>Админ панель</span>
              </router-link>
              <router-link :to="{ name: 'admin-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📅</span>
                <span>Расписание</span>
              </router-link>
              <router-link :to="{ name: 'admin-courses' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📚</span>
                <span>Курсы</span>
              </router-link>
              <router-link :to="{ name: 'admin-logs' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📋</span>
                <span>Логи</span>
              </router-link>
            </template>
            
            <!-- Разделы для Менеджера -->
            <template v-if="auth.normalizedRole === 'manager'">
              <router-link :to="{ name: 'manager-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📊</span>
                <span>Панель менеджера</span>
              </router-link>
              <router-link :to="{ name: 'manager-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📅</span>
                <span>Расписание</span>
              </router-link>
              <router-link :to="{ name: 'manager-balance' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">💰</span>
                <span>Баланс</span>
              </router-link>
            </template>
            
            <!-- Разделы для Учителя -->
            <template v-if="auth.normalizedRole === 'teacher'">
              <router-link :to="{ name: 'teacher-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📊</span>
                <span>Панель учителя</span>
              </router-link>
              <router-link :to="{ name: 'teacher-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="dropdown-icon">📅</span>
                <span>Расписание</span>
              </router-link>
            </template>
          </div>
        </div>

        <!-- Меню пользователя -->
        <div v-if="auth.isAuthenticated" class="user-menu">
          <button class="user-name" @click="toggleUserMenu">
            {{ auth.user?.email || 'Пользователь' }}
          </button>
          <div 
            class="user-dropdown"
            :class="{ 'user-dropdown-open': showUserMenu }"
            @click.stop
          >
            <router-link 
              v-if="auth.normalizedRole === 'applicant'"
              :to="{ name: 'applicant-dashboard' }" 
              class="dropdown-item"
              @click="closeUserMenu"
            >
              Личный кабинет
            </router-link>
            <router-link 
              v-if="auth.normalizedRole === 'student'"
              :to="{ name: 'student-dashboard' }" 
              class="dropdown-item"
              @click="closeUserMenu"
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
      </nav>
    </header>

    <!-- Основной контент -->
    <main class="main-container">
      <section class="content-section">
        <header class="content-header">
          <h1 class="page-title">Курсы</h1>
        </header>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка курсов...</p>
        </div>
        
        <div v-else-if="courses.length === 0" class="empty-state">
          <p>Курсы пока не добавлены</p>
        </div>
        
        <div v-else class="courses-grid">
          <article 
            v-for="course in courses" 
            :key="course.id" 
            class="course-card"
            @click="openCourseDetails(course)"
          >
            <div class="course-card-content">
              <h2 class="course-title">{{ course.title }}</h2>
              <div class="course-meta">
                <span class="meta-icon">📚</span>
                <span class="meta-text">Модулей: {{ course.modules_count || 0 }}</span>
              </div>
            </div>
            <button class="course-btn" @click.stop="openCourseDetails(course)">
              ПОДРОБНЕЕ
            </button>
          </article>
        </div>
      </section>
    </main>

    <!-- Модальное окно с деталями курса -->
    <div v-if="selectedCourse" class="modal-backdrop" @click="closeCourseDetails">
      <div class="course-modal" @click.stop>
        <header class="course-modal-header">
          <h2>{{ selectedCourse.title }}</h2>
          <button class="close-btn" @click="closeCourseDetails" aria-label="Закрыть">×</button>
        </header>
        <div class="course-modal-content">
          <div v-if="selectedCourse.modules && selectedCourse.modules.length" class="modules-section">
            <h3>Модули курса</h3>
            <div class="modules-list">
              <article
                v-for="module in selectedCourse.modules"
                :key="module.id"
                class="module-card"
              >
                <header class="module-header">
                  <h4>{{ module.title }}</h4>
                  <span class="module-order">Модуль {{ module.order }}</span>
                </header>
                <p v-if="module.description" class="module-description">
                  {{ module.description }}
                </p>
                <div v-if="module.topics && module.topics.length" class="topics-list">
                  <h5>Темы занятий ({{ module.topics_count || module.topics.length }}):</h5>
                  <ul class="topics-ul">
                    <li v-for="topic in module.topics" :key="topic.id" class="topic-item">
                      <span class="topic-order">{{ topic.order }}.</span>
                      <div class="topic-content">
                        <strong>{{ topic.title }}</strong>
                        <p v-if="topic.description" class="topic-description">{{ topic.description }}</p>
                      </div>
                    </li>
                  </ul>
                </div>
                <p v-else class="no-topics">Тем пока нет</p>
              </article>
            </div>
          </div>
          <p v-else class="no-modules">Модулей пока нет</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import apiClient from '../../api/http'

const auth = useAuthStore()
const router = useRouter()
const courses = ref([])
const selectedCourse = ref(null)
const loading = ref(false)
// Навигация теперь в TopNavigationBar компоненте

const fetchCourses = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/api/applicant/courses/public/')
    courses.value = data
  } catch (err) {
    if (err?.response?.status !== 401) {
      console.error('Ошибка загрузки курсов:', err)
    }
    courses.value = []
  } finally {
    loading.value = false
  }
}

const openCourseDetails = (course) => {
  selectedCourse.value = course
}

const closeCourseDetails = () => {
  selectedCourse.value = null
}

onMounted(() => {
  fetchCourses()
  if (auth.isAuthenticated && !auth.user) {
    auth.fetchMe()
  }
  
  // Закрытие меню при клике вне их
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.home-page {
  width: 100vw;
  height: 100vh;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
  padding: 0;
  position: relative;
}

.home-page::before {
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

/* Навигация */
.top-nav {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0;
  margin: 0;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  min-height: 80px;
  position: relative;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 32px;
  margin: 0;
  height: 100%;
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

.nav-btn {
  padding: 12px 28px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  display: inline-block;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.nav-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.nav-btn:hover::before {
  left: 100%;
}

.nav-btn.primary {
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 6px 20px rgba(255, 255, 255, 0.3);
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  text-decoration: none;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
}

.nav-btn.primary:hover {
  background: rgba(255, 255, 255, 1);
  text-decoration: none;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 255, 255, 0.4);
}

/* Меню администрирования */
.admin-menu {
  position: relative;
  cursor: pointer;
}

.admin-btn {
  padding: 12px 24px;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  border: none;
  font-family: inherit;
}

.admin-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.admin-btn-icon {
  font-size: 1.1rem;
}

.admin-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  min-width: 240px;
  display: none;
  z-index: 1000;
  overflow: hidden;
}

.admin-dropdown-open {
  display: block;
  animation: fadeInDown 0.2s ease;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.user-name {
  padding: 12px 24px;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  border: none;
  font-family: inherit;
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  display: none;
  z-index: 1000;
  overflow: hidden;
}

.user-dropdown-open {
  display: block;
  animation: fadeInDown 0.2s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  text-decoration: none;
  color: #495057;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  font-weight: 500;
}

.dropdown-item:hover {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  color: #667eea;
}

.dropdown-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

/* Основной контент - 100% ширины и высоты */
.main-container {
  width: 100%;
  height: 100%;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.content-section {
  width: 100%;
  height: 100%;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.content-header {
  margin: 0;
  padding: 32px 32px 20px 32px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 4.5rem;
  font-weight: 900;
  margin: 0;
  padding: 0;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  letter-spacing: -2px;
  line-height: 1.1;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Состояния загрузки */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.loading-spinner {
  width: 56px;
  height: 56px;
  border: 5px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Сетка курсов - использует максимум пространства */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 0;
  width: 100%;
  flex: 1;
  align-content: start;
  padding: 0;
  margin: 0;
  position: relative;
  z-index: 1;
}

.course-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0;
  padding: 0;
  margin: 0;
  position: relative;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  min-height: 360px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.course-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #ffffff 0%, rgba(255, 255, 255, 0.5) 100%);
  transform: scaleX(0);
  transition: transform 0.4s ease;
  z-index: 2;
}

.course-card::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.course-card:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.course-card:hover::before {
  transform: scaleX(1);
}

.course-card:hover::after {
  opacity: 1;
}

.course-card-content {
  padding: 40px;
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.course-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 24px 0;
  padding: 0;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.course-meta {
  margin: 0;
  padding: 0;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta-icon {
  font-size: 1.6rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.meta-text {
  font-weight: 600;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.course-btn {
  width: 100%;
  padding: 20px 24px;
  margin: 0;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: none;
  border-radius: 0;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 1px;
  z-index: 2;
}

.course-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.6s;
}

.course-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.2);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.course-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #5568d3;
  box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.course-btn:hover::before {
  left: 100%;
}

.course-btn:hover::after {
  width: 400px;
  height: 400px;
}

.course-btn:active {
  transform: translateY(0) scale(0.98);
}

/* Адаптивность */
@media (max-width: 1600px) {
  .courses-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 1400px) {
  .content-header {
    padding: 28px 28px 16px 28px;
  }
  
  .page-title {
    font-size: 4rem;
  }

  .courses-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 1200px) {
  .content-header {
    padding: 18px 18px 12px 18px;
  }
  
  .courses-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }

  .course-card {
    min-height: 300px;
  }

  .course-card-content {
    padding: 28px;
  }
}

@media (max-width: 768px) {
  .nav-right {
    padding: 0 16px;
  }

  .content-header {
    padding: 16px 16px 12px 16px;
  }

  .page-title {
    font-size: 2.5rem;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .course-card {
    min-height: 280px;
  }

  .course-card-content {
    padding: 24px;
  }

  .course-title {
    font-size: 1.5rem;
  }
}

/* Модальное окно с деталями курса */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px) saturate(180%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.course-modal {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(30px) saturate(180%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.course-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 36px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 24px 24px 0 0;
}

.course-modal-header h2 {
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
}

.close-btn {
  background: rgba(0, 0, 0, 0.04);
  border: none;
  font-size: 28px;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  line-height: 1;
}

.close-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transform: rotate(90deg);
}

.course-modal-content {
  padding: 32px;
}

.modules-section h3 {
  margin: 0 0 24px 0;
  font-size: 22px;
  font-weight: 700;
  color: #212529;
}

.modules-list {
  display: grid;
  gap: 20px;
}

.module-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.module-card:hover {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.module-header h4 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #212529;
}

.module-order {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.module-description {
  color: #6c757d;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 20px;
}

.topics-list {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.topics-list h5 {
  margin: 0 0 16px 0;
  font-size: 15px;
  color: #495057;
  font-weight: 600;
}

.topics-ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.topic-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.topic-item:hover {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.04) 0%, rgba(118, 75, 162, 0.04) 100%);
  border-color: rgba(102, 126, 234, 0.2);
  transform: translateX(4px);
}

.topic-order {
  color: #667eea;
  font-weight: 700;
  min-width: 28px;
  font-size: 16px;
}

.topic-content {
  flex: 1;
}

.topic-content strong {
  display: block;
  color: #212529;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
}

.topic-description {
  color: #6c757d;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}

.no-topics,
.no-modules {
  color: #adb5bd;
  font-style: italic;
  text-align: center;
  padding: 32px;
  font-size: 15px;
}
</style>
