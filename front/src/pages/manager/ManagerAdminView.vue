<!-- src/pages/manager/ManagerAdminView.vue -->
<template>
  <div class="manager-admin-page">
    <TopNavigationBar />

    <!-- Основной контент -->
    <main class="main-container">
      <section class="content-section">
        <header class="content-header">
          <h1 class="page-title">Администрирование</h1>
        </header>

        <div class="admin-sections-grid">
          <article 
            class="admin-section-card"
            @click="goToSchedule"
          >
            <div class="section-card-content">
              <div class="section-icon">📅</div>
              <h2 class="section-title">Календарь</h2>
              <p class="section-description">
                Просмотр и управление расписанием занятий
              </p>
            </div>
            <button class="section-btn" @click.stop="goToSchedule">
              ОТКРЫТЬ
            </button>
          </article>

          <article 
            class="admin-section-card"
            @click="goToBalance"
          >
            <div class="section-card-content">
              <div class="section-icon">💰</div>
              <h2 class="section-title">Управление балансами</h2>
              <p class="section-description">
                Просмотр и изменение баланса уроков у учеников
              </p>
            </div>
            <button class="section-btn" @click.stop="goToBalance">
              ОТКРЫТЬ
            </button>
          </article>

          <article 
            class="admin-section-card"
            @click="goToRequests"
          >
            <div class="section-card-content">
              <div class="section-icon">💬</div>
              <h2 class="section-title">Связь с клиентами</h2>
              <p class="section-description">
                Просмотр и управление обращениями клиентов
              </p>
            </div>
            <button class="section-btn" @click.stop="goToRequests">
              ОТКРЫТЬ
            </button>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'

const auth = useAuthStore()
const router = useRouter()

const goToSchedule = () => {
  router.push({ name: 'manager-schedule' })
}

const goToBalance = () => {
  router.push({ name: 'manager-balance' })
}

const goToRequests = () => {
  router.push({ name: 'manager-requests' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.manager-admin-page {
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

.manager-admin-page::before {
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

/* Сетка разделов */
.admin-sections-grid {
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

.admin-section-card {
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

.admin-section-card::before {
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

.admin-section-card::after {
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

.admin-section-card:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.admin-section-card:hover::before {
  transform: scaleX(1);
}

.admin-section-card:hover::after {
  opacity: 1;
}

.section-card-content {
  padding: 40px;
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.section-icon {
  font-size: 4rem;
  margin-bottom: 24px;
  filter: drop-shadow(0 2px 10px rgba(0, 0, 0, 0.2));
}

.section-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 16px 0;
  padding: 0;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.section-description {
  margin: 0;
  padding: 0;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.5;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.section-btn {
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

.section-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.6s;
}

.section-btn::after {
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

.section-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #5568d3;
  box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.section-btn:hover::before {
  left: 100%;
}

.section-btn:hover::after {
  width: 400px;
  height: 400px;
}

.section-btn:active {
  transform: translateY(0) scale(0.98);
}

/* Адаптивность */
@media (max-width: 1600px) {
  .admin-sections-grid {
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

  .admin-sections-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 1200px) {
  .content-header {
    padding: 18px 18px 12px 18px;
  }
  
  .admin-sections-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }

  .admin-section-card {
    min-height: 300px;
  }

  .section-card-content {
    padding: 28px;
  }
}

@media (max-width: 768px) {
  .content-header {
    padding: 16px 16px 12px 16px;
  }

  .page-title {
    font-size: 2.5rem;
  }

  .admin-sections-grid {
    grid-template-columns: 1fr;
  }

  .admin-section-card {
    min-height: 280px;
  }

  .section-card-content {
    padding: 24px;
  }

  .section-title {
    font-size: 1.5rem;
  }
}
</style>



