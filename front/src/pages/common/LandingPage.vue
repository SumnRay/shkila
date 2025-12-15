<!-- src/pages/common/LandingPage.vue -->
<template>
  <div class="home-page">
    <!-- Навигация -->
    <div class="top-nav">
      <div class="nav-right">
        <router-link 
          v-if="!auth.isAuthenticated" 
          :to="{ name: 'login' }" 
          class="nav-btn auth-btn"
        >
          Вход/Регистрация
        </router-link>
        <div v-else class="nav-auth-wrapper">
          <TopNavigationBar />
        </div>
      </div>
    </div>

    <!-- Hero секция -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">F.L.A.R.E.</h1>
          <p class="hero-subtitle">— современное обучение программированию</p>
          <p class="hero-slogan">От первого шага до первых проектов.</p>
          <div class="hero-cta">
            <button class="cta-button" @click="handleEnroll">
              Записаться
            </button>
            <span class="cta-text">Начни прямо сейчас!</span>
          </div>
        </div>
        <div class="hero-graphic">
          <div class="circuit-board">
            <svg viewBox="0 0 200 200" class="power-icon">
              <defs>
                <linearGradient id="powerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
                  <stop offset="50%" style="stop-color:#FFA500;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#FF8C00;stop-opacity:1" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <filter id="strongGlow">
                  <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <!-- Main circuit traces (thicker, more prominent) -->
              <path d="M 10 100 L 70 100" stroke="url(#powerGradient)" stroke-width="3" fill="none" filter="url(#glow)"/>
              <path d="M 130 100 L 190 100" stroke="url(#powerGradient)" stroke-width="3" fill="none" filter="url(#glow)"/>
              <path d="M 100 10 L 100 70" stroke="url(#powerGradient)" stroke-width="3" fill="none" filter="url(#glow)"/>
              <path d="M 100 130 L 100 190" stroke="url(#powerGradient)" stroke-width="3" fill="none" filter="url(#glow)"/>
              
              <!-- Diagonal traces -->
              <path d="M 30 30 L 50 50" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M 170 30 L 150 50" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M 30 170 L 50 150" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M 170 170 L 150 150" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              
              <!-- Additional circuit connections -->
              <path d="M 70 100 L 70 80 L 50 80" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M 130 100 L 130 80 L 150 80" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M 70 100 L 70 120 L 50 120" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M 130 100 L 130 120 L 150 120" stroke="url(#powerGradient)" stroke-width="2" fill="none" filter="url(#glow)"/>
              
              <!-- Circuit nodes (small circles at intersections) -->
              <circle cx="70" cy="100" r="3" fill="url(#powerGradient)" filter="url(#glow)"/>
              <circle cx="130" cy="100" r="3" fill="url(#powerGradient)" filter="url(#glow)"/>
              <circle cx="100" cy="70" r="3" fill="url(#powerGradient)" filter="url(#glow)"/>
              <circle cx="100" cy="130" r="3" fill="url(#powerGradient)" filter="url(#glow)"/>
              
              <!-- Power button circle (main element) -->
              <circle cx="100" cy="100" r="40" stroke="url(#powerGradient)" stroke-width="5" fill="none" filter="url(#strongGlow)"/>
              <circle cx="100" cy="100" r="35" stroke="url(#powerGradient)" stroke-width="3" fill="none" filter="url(#glow)"/>
              
              <!-- Power symbol (more prominent) -->
              <path d="M 100 70 L 100 130" stroke="url(#powerGradient)" stroke-width="5" stroke-linecap="round" filter="url(#strongGlow)"/>
              <path d="M 100 100 L 82 82" stroke="url(#powerGradient)" stroke-width="5" stroke-linecap="round" filter="url(#strongGlow)"/>
              
              <!-- Inner glow effect -->
              <circle cx="100" cy="100" r="30" fill="none" stroke="url(#powerGradient)" stroke-width="1" opacity="0.3" filter="url(#glow)"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- Секция курсов -->
    <section class="courses-section">
      <h2 class="courses-title">Курсы</h2>
      
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка курсов...</p>
      </div>
      
      <div v-else-if="courses.length === 0" class="empty-state">
        <p>Курсы пока не добавлены</p>
      </div>
      
      <div v-else class="courses-grid">
        <article 
          v-for="course in displayedCourses" 
          :key="course.id" 
          class="course-card"
        >
          <h3 class="course-card-title">{{ course.title }}</h3>
          <div class="course-card-description">
            <p v-for="(line, index) in getCourseDescription(course)" :key="index">
              {{ line }}
            </p>
          </div>
          <button class="course-enroll-btn" @click="handleCourseEnroll(course)">
            Записаться
          </button>
        </article>
      </div>

      <div v-if="courses.length > 3" class="more-courses">
        <button class="more-courses-btn" @click="showAllCourses = !showAllCourses">
          {{ showAllCourses ? 'Скрыть' : 'Больше курсов →' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import { applicantGetPublicCourses } from '../../api/applicant'

const auth = useAuthStore()
const router = useRouter()
const courses = ref([])
const loading = ref(false)
const showAllCourses = ref(false)

const displayedCourses = computed(() => {
  if (showAllCourses.value || courses.value.length <= 3) {
    return courses.value
  }
  return courses.value.slice(0, 3)
})

const fetchCourses = async () => {
  loading.value = true
  try {
    const { data } = await applicantGetPublicCourses()
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

const getCourseDescription = (course) => {
  // Описания курсов на основе названия
  const descriptions = {
    'python': [
      'Просто начать. Легко продолжать.',
      'Понятный синтаксис — идеально для первых шагов.',
      'Используется в анализе данных, AI, вебе и автоматизации.'
    ],
    'c++': [
      'Максимум мощности и контроля.',
      'Высокая производительность для игр и системных приложений.',
      'Позволяет управлять памятью и ресурсами напрямую.'
    ],
    'javascript': [
      'Язык, который работает в браузере.',
      'Делает сайты интерактивными и живыми.',
      'React, Vue, Node.js — огромная экосистема для роста.'
    ]
  }

  // Ищем точное совпадение или частичное
  const courseTitle = course.title.toLowerCase().trim()
  
  // Проверяем точное совпадение
  if (descriptions[courseTitle]) {
    return descriptions[courseTitle]
  }
  
  // Проверяем частичное совпадение
  for (const [key, desc] of Object.entries(descriptions)) {
    if (courseTitle.includes(key) || key.includes(courseTitle)) {
      return desc
    }
  }

  // Дефолтное описание
  return [
    'Современный подход к обучению.',
    'Практические задания и проекты.',
    `Модулей: ${course.modules_count || 0}`
  ]
}

const handleEnroll = () => {
  if (auth.isAuthenticated) {
    router.push({ name: 'applicant-dashboard' })
  } else {
    router.push({ name: 'register' })
  }
}

const handleCourseEnroll = (course) => {
  if (auth.isAuthenticated) {
    router.push({ name: 'applicant-dashboard' })
  } else {
    router.push({ name: 'register' })
  }
}

onMounted(() => {
  fetchCourses()
  if (auth.isAuthenticated && !auth.user) {
    auth.fetchMe()
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.home-page {
  width: 100%;
  min-height: 100vh;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

/* Навигация */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 32px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  flex-shrink: 0;
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-auth-wrapper {
  display: flex;
  align-items: center;
}

.nav-auth-wrapper :deep(.top-navigation-bar) {
  background: transparent;
  border: none;
  padding: 0;
  box-shadow: none;
  position: static;
}

.auth-btn {
  padding: 10px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid #FFD700;
  color: #FFD700;
  background: transparent;
  display: inline-block;
  cursor: pointer;
}

.auth-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

/* Hero секция */
.hero-section {
  padding: 80px 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  min-height: auto;
  position: relative;
  flex-shrink: 0;
  box-sizing: border-box;
}

.hero-content {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 60px;
  align-items: center;
  min-height: auto;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 100%;
  width: 100%;
  box-sizing: border-box;
}

.hero-title {
  font-size: 4.5rem;
  font-weight: 900;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
  letter-spacing: -2px;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.4rem;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
  font-weight: 400;
  line-height: 1.4;
}

.hero-slogan {
  font-size: 1rem;
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
  line-height: 1.5;
}

.hero-cta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.cta-button {
  padding: 14px 36px;
  border-radius: 8px;
  border: none;
  background: #FFD700;
  color: #1A1A1A;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  white-space: nowrap;
}

.cta-button:hover {
  background: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.cta-text {
  font-size: 0.95rem;
  color: #FFFFFF;
  font-weight: 500;
  white-space: nowrap;
}

.hero-graphic {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 300px;
  box-sizing: border-box;
}

.circuit-board {
  width: 100%;
  max-width: 280px;
  height: auto;
  aspect-ratio: 1;
  position: relative;
}

.power-icon {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.5));
}

/* Секция курсов */
.courses-section {
  padding: 100px 32px;
  max-width: 1400px;
  width: 100%;
  margin: 60px auto 0 auto;
  position: relative;
  border-top: 2px solid rgba(255, 215, 0, 0.2);
  flex-shrink: 0;
  box-sizing: border-box;
}

.courses-title {
  font-size: 3rem;
  font-weight: 900;
  text-align: center;
  margin: 0 0 60px 0;
  padding: 0;
  color: #FFFFFF;
  letter-spacing: -1px;
  width: 100%;
  box-sizing: border-box;
}

/* Состояния загрузки */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  font-weight: 600;
}

.loading-spinner {
  width: 56px;
  height: 56px;
  border: 5px solid rgba(255, 215, 0, 0.2);
  border-top-color: #FFD700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Сетка курсов */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 40px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.course-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: all 0.3s ease;
  min-height: 350px;
  height: auto;
  width: 100%;
  max-width: 100%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  box-sizing: border-box;
  overflow: hidden;
}

.course-card:hover {
  border-color: #FF8C00;
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(255, 215, 0, 0.3);
}

.course-card-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
}

.course-card-description {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-card-description p {
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  line-height: 1.6;
}

.course-enroll-btn {
  padding: 14px 28px;
  border-radius: 8px;
  border: none;
  background: #FFD700;
  color: #1A1A1A;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  margin-top: auto;
}

.course-enroll-btn:hover {
  background: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 215, 0, 0.4);
}

.more-courses {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  width: 100%;
  box-sizing: border-box;
}

.more-courses-btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFD700;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.more-courses-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .hero-section {
    padding: 60px 32px;
    width: 100%;
  }

  .courses-section {
    padding: 80px 32px;
    margin-top: 40px;
    width: 100%;
  }

  .hero-content {
    grid-template-columns: 1fr;
    gap: 50px;
    min-height: auto;
    width: 100%;
  }

  .hero-graphic {
    order: -1;
    min-height: 250px;
    width: 100%;
  }

  .circuit-board {
    max-width: 240px;
  }

  .hero-title {
    font-size: 4rem;
  }

  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 28px;
    width: 100%;
  }

  .course-card {
    min-height: 320px;
    width: 100%;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 50px 20px;
    width: 100%;
  }

  .courses-section {
    padding: 60px 20px;
    margin-top: 30px;
    width: 100%;
  }

  .hero-content {
    gap: 40px;
    width: 100%;
  }

  .hero-title {
    font-size: 3rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .hero-slogan {
    font-size: 0.95rem;
  }

  .hero-graphic {
    min-height: 200px;
    width: 100%;
  }

  .circuit-board {
    max-width: 200px;
  }

  .courses-title {
    font-size: 2.5rem;
    margin-bottom: 40px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
    gap: 24px;
    width: 100%;
  }

  .course-card {
    min-height: auto;
    padding: 28px;
    width: 100%;
  }

  .top-nav {
    padding: 12px 20px;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 40px 16px;
    width: 100%;
  }

  .courses-section {
    padding: 50px 16px;
    margin-top: 20px;
    width: 100%;
  }

  .hero-content {
    width: 100%;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .hero-cta {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    width: 100%;
  }

  .cta-button {
    width: 100%;
    padding: 12px 24px;
  }

  .cta-text {
    text-align: center;
  }

  .hero-graphic {
    min-height: 180px;
    width: 100%;
  }

  .circuit-board {
    max-width: 180px;
  }

  .courses-title {
    font-size: 2rem;
    margin-bottom: 30px;
  }

  .courses-grid {
    width: 100%;
  }

  .course-card {
    padding: 24px;
    width: 100%;
  }
}
</style>
