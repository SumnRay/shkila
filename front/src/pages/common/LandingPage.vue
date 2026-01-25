<!-- src/pages/common/LandingPage.vue -->
<template>
  <div class="home-page">
    <!-- Hero секция -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">F.L.A.R.E.</h1>
          <p class="hero-subtitle">Персональный сервис учёта и индивидуального обучения</p>
          <p class="hero-description">Прозрачный учет занятий, индивидуальный подход и личный преподаватель.</p>
          <div class="hero-cta">
            <button class="cta-button-primary" @click="handleEnroll">
              Записаться
            </button>
            <button class="cta-button-secondary" @click="scrollToFeatures">
              Подробнее о сервисе
              <span class="caret-icon">▼</span>
            </button>
          </div>
        </div>
        <div class="hero-graphic">
          <div class="logo-wrapper">
            <img src="/logo.png" alt="F.L.A.R.E. Logo" class="main-logo" />
          </div>
        </div>
      </div>
    </section>

    <!-- Секция возможностей -->
    <section class="features-section" ref="featuresSection">
      <h2 class="features-title">Что даёт платформа F.L.A.R.E.</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">💼</div>
          <h3 class="feature-title">Баланс оплаченных занятий</h3>
          <p class="feature-description">Количество уроков и остаточный баланс.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📅</div>
          <h3 class="feature-title">Удобное расписание</h3>
          <p class="feature-description">Ближайшие занятия и удобное расписание.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⏰</div>
          <h3 class="feature-title">История занятий</h3>
          <p class="feature-description">История всех занятий.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">👤</div>
          <h3 class="feature-title">Личный кабинет</h3>
          <p class="feature-description">Личный кабинет ученика.</p>
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
      <div v-else class="courses-layout">
        <div class="course-detail-card">
          <h3 class="course-detail-title">{{ selectedCourse?.title || 'Курс' }}</h3>
          <div class="course-tags">
            <span class="course-tag">
              <span class="tag-icon">📖</span>
              С нуля
            </span>
            <span class="course-tag">
              <span class="tag-icon">👤</span>
              Индивидуально
            </span>
            <span class="course-tag">
              <span class="tag-icon">💻</span>
              Онлайн
            </span>
          </div>
          <div v-if="selectedCourse" class="course-info">
            <div v-if="selectedCourse.modules && selectedCourse.modules.length > 0" class="course-modules">
              <p class="course-modules-count">Модулей: {{ selectedCourse.modules_count || 0 }}</p>
              <div class="course-description">
                <p v-for="(module, index) in selectedCourse.modules.slice(0, 3)" :key="module.id" class="module-preview">
                  {{ module.title }}
                </p>
                <p v-if="selectedCourse.modules.length > 3" class="module-preview-more">
                  и ещё {{ selectedCourse.modules.length - 3 }} модулей...
                </p>
              </div>
            </div>
            <p v-else class="course-detail-description">
              Просто начать. Легко продолжать. Понятно сложно — очевидно для первых шагов. Используем в анализе данных, AI, вебе и автоматизации.
            </p>
          </div>
          <p v-else class="course-detail-description">
            Просто начать. Легко продолжать. Понятно сложно — очевидно для первых шагов. Используем в анализе данных, AI, вебе и автоматизации.
          </p>
          <button class="course-enroll-btn" @click="handleEnroll">
            Записаться
          </button>
        </div>
        <div class="course-benefits">
          <div class="benefit-item">
            <span class="benefit-checkmark">✓</span>
            <span class="benefit-text">С нуля — Индивидуально — Онлайн</span>
          </div>
          <div class="benefit-item">
            <span class="benefit-checkmark">✓</span>
            <span class="benefit-text">Ближайшие занятия и удобное расписание</span>
          </div>
          <div class="benefit-item">
            <span class="benefit-checkmark">✓</span>
            <span class="benefit-text">История всех занятий</span>
          </div>
          <div class="benefit-item">
            <span class="benefit-checkmark">✓</span>
            <span class="benefit-text">Личный кабинет ученика</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Секция призыва к действию -->
    <section class="cta-section">
      <h2 class="cta-title">Хотите индивидуальное обучение и прозрачный учёт занятий?</h2>
      <button class="cta-button-primary" @click="handleEnroll">
        Записаться
      </button>
    </section>

    <!-- Футер -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import { applicantGetPublicCourses } from '../../api/applicant'
import Footer from '../../components/Footer.vue'

const auth = useAuthStore()
const router = useRouter()
const featuresSection = ref(null)
const courses = ref([])
const loading = ref(false)

const selectedCourse = computed(() => {
  return courses.value.length > 0 ? courses.value[0] : null
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

const handleEnroll = () => {
  if (auth.isAuthenticated) {
    router.push({ name: 'applicant-dashboard' })
  } else {
    router.push({ name: 'register' })
  }
}

const scrollToFeatures = () => {
  if (featuresSection.value) {
    featuresSection.value.scrollIntoView({ behavior: 'smooth' })
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
  background: #000000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

/* Hero секция */
.hero-section {
  padding: 120px 32px 100px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.hero-content {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 80px;
  align-items: center;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 100%;
  width: 100%;
  box-sizing: border-box;
}

.hero-title {
  font-size: 5.5rem;
  font-weight: 900;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
  letter-spacing: -3px;
  line-height: 1;
  text-transform: uppercase;
}

.hero-subtitle {
  font-size: 1.6rem;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
  font-weight: 400;
  line-height: 1.4;
}

.hero-description {
  font-size: 1.15rem;
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 400;
  line-height: 1.7;
}

.hero-cta {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
  flex-wrap: wrap;
}

.cta-button-primary {
  padding: 16px 40px;
  border-radius: 8px;
  border: none;
  background: #FFD700;
  color: #000000;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  white-space: nowrap;
}

.cta-button-primary:hover {
  background: #FFA500;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.5);
}

.cta-button-secondary {
  padding: 16px 40px;
  border-radius: 8px;
  border: none;
  background: rgba(30, 30, 30, 0.9);
  color: #FFFFFF;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 10px;
}

.cta-button-secondary:hover {
  background: rgba(50, 50, 50, 0.95);
  transform: translateY(-2px);
}

.caret-icon {
  font-size: 0.85rem;
  transition: transform 0.3s ease;
}

.cta-button-secondary:hover .caret-icon {
  transform: translateY(3px);
}

.hero-graphic {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 350px;
  box-sizing: border-box;
}

.logo-wrapper {
  width: 100%;
  max-width: 320px;
  height: auto;
  aspect-ratio: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.main-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 25px rgba(255, 215, 0, 0.7)) 
          drop-shadow(0 0 50px rgba(255, 215, 0, 0.5))
          drop-shadow(0 0 75px rgba(255, 165, 0, 0.4));
  animation: logo-glow 3s ease-in-out infinite alternate;
}

@keyframes logo-glow {
  0% {
    filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.6)) 
            drop-shadow(0 0 40px rgba(255, 215, 0, 0.4))
            drop-shadow(0 0 60px rgba(255, 165, 0, 0.3));
  }
  100% {
    filter: drop-shadow(0 0 30px rgba(255, 215, 0, 0.8)) 
            drop-shadow(0 0 60px rgba(255, 215, 0, 0.6))
            drop-shadow(0 0 90px rgba(255, 165, 0, 0.5));
  }
}

/* Секция возможностей */
.features-section {
  padding: 120px 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.features-title {
  font-size: 3.2rem;
  font-weight: 900;
  text-align: center;
  margin: 0 0 80px 0;
  padding: 0;
  color: #FFFFFF;
  letter-spacing: -1.5px;
  width: 100%;
  box-sizing: border-box;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 40px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.feature-card {
  background: rgba(30, 30, 30, 0.9);
  border-radius: 16px;
  padding: 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  transition: all 0.3s ease;
  box-sizing: border-box;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(255, 215, 0, 0.25);
  border-color: rgba(255, 215, 0, 0.3);
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 4px;
  filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
}

.feature-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
}

.feature-description {
  font-size: 1.05rem;
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.7;
}

/* Секция курсов */
.courses-section {
  padding: 120px 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.courses-title {
  font-size: 3.2rem;
  font-weight: 900;
  margin: 0 0 80px 0;
  padding: 0;
  color: #FFFFFF;
  letter-spacing: -1.5px;
  width: 100%;
  box-sizing: border-box;
}

.courses-layout {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 80px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.course-detail-card {
  background: rgba(30, 30, 30, 0.9);
  border-radius: 16px;
  padding: 48px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  box-sizing: border-box;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.course-detail-title {
  font-size: 2.8rem;
  font-weight: 800;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
  letter-spacing: -1px;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.course-tag {
  background: rgba(0, 0, 0, 0.6);
  color: #FFFFFF;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tag-icon {
  font-size: 1.1rem;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-modules {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-modules-count {
  font-size: 1rem;
  color: rgba(255, 215, 0, 0.9);
  font-weight: 600;
  margin: 0;
  padding: 0;
}

.course-description {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-preview {
  font-size: 1.05rem;
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  padding-left: 16px;
  position: relative;
}

.module-preview::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #FFD700;
  font-weight: bold;
}

.module-preview-more {
  font-size: 1rem;
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  padding-left: 16px;
}

.course-detail-description {
  font-size: 1.15rem;
  margin: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.9;
}

.course-enroll-btn {
  padding: 16px 40px;
  border-radius: 8px;
  border: none;
  background: #FFD700;
  color: #000000;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  align-self: flex-start;
  margin-top: auto;
}

.course-enroll-btn:hover {
  background: #FFA500;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.5);
}

.course-benefits {
  display: flex;
  flex-direction: column;
  gap: 28px;
  padding-top: 24px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.benefit-checkmark {
  color: #FFD700;
  font-size: 1.8rem;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
}

.benefit-text {
  font-size: 1.15rem;
  color: #FFFFFF;
  line-height: 1.7;
  font-weight: 400;
}

/* Секция призыва к действию */
.cta-section {
  padding: 120px 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  text-align: center;
  box-sizing: border-box;
}

.cta-title {
  font-size: 2.8rem;
  font-weight: 700;
  margin: 0 0 50px 0;
  padding: 0;
  color: #FFFFFF;
  line-height: 1.3;
  letter-spacing: -0.5px;
}

/* Состояния загрузки */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.3rem;
  font-weight: 600;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(255, 215, 0, 0.2);
  border-top-color: #FFD700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Адаптивность */
@media (max-width: 1200px) {
  .hero-section,
  .features-section,
  .courses-section,
  .cta-section {
    padding: 100px 32px;
  }

  .hero-content {
    grid-template-columns: 1fr;
    gap: 60px;
  }

  .hero-graphic {
    order: -1;
    min-height: 280px;
  }

  .logo-wrapper {
    max-width: 260px;
  }

  .courses-layout {
    grid-template-columns: 1fr;
    gap: 50px;
  }
}

@media (max-width: 768px) {
  .hero-section,
  .features-section,
  .courses-section,
  .cta-section {
    padding: 80px 20px;
  }

  .hero-title {
    font-size: 4rem;
  }

  .hero-subtitle {
    font-size: 1.4rem;
  }

  .hero-description {
    font-size: 1.05rem;
  }

  .hero-cta {
    flex-direction: column;
    align-items: stretch;
  }

  .cta-button-primary,
  .cta-button-secondary {
    width: 100%;
  }

  .features-title,
  .courses-title {
    font-size: 2.5rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .feature-card {
    padding: 36px;
  }

  .cta-title {
    font-size: 2.2rem;
  }

  .course-detail-card {
    padding: 36px;
  }
}

@media (max-width: 480px) {
  .hero-section,
  .features-section,
  .courses-section,
  .cta-section {
    padding: 60px 16px;
  }

  .hero-title {
    font-size: 3rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .features-title,
  .courses-title {
    font-size: 2rem;
  }

  .feature-card,
  .course-detail-card {
    padding: 28px;
  }

  .cta-title {
    font-size: 1.8rem;
  }
}
</style>