<!-- src/pages/applicant/ApplicantDashboardView.vue -->
<template>
  <div class="applicant-dashboard">
    <TopNavigationBar />

    <div class="dashboard-content">
      <div class="page-header">
        <h1 class="dashboard-title">Личный кабинет</h1>
        <p class="dashboard-subtitle">Управление вашим профилем</p>
      </div>
      <div class="profile-card">
        <div class="card-header">
          <div class="card-header-icon">👤</div>
          <h2 class="card-title">Профиль</h2>
        </div>
        
        <div class="profile-info">
          <div class="info-item">
            <div class="info-icon">📧</div>
            <div class="info-content">
              <span class="label">Email</span>
              <span class="value">{{ auth.user?.email || '—' }}</span>
            </div>
          </div>
          
          <div class="info-item" v-if="auth.user?.phone">
            <div class="info-icon">📱</div>
            <div class="info-content">
              <span class="label">Телефон</span>
              <span class="value">{{ auth.user.phone }}</span>
            </div>
          </div>
          
          <div class="info-item" v-if="auth.user?.student_full_name">
            <div class="info-icon">🎓</div>
            <div class="info-content">
              <span class="label">ФИО ученика</span>
              <span class="value">{{ auth.user.student_full_name }}</span>
            </div>
          </div>
          
          <div class="info-item" v-if="auth.user?.parent_full_name">
            <div class="info-icon">👨‍👩‍👧</div>
            <div class="info-content">
              <span class="label">ФИО родителя</span>
              <span class="value">{{ auth.user.parent_full_name }}</span>
            </div>
          </div>
        </div>
        
        <div class="profile-actions">
          <router-link :to="{ name: 'edit-profile' }" class="btn-edit">
            <span class="btn-icon">✏️</span>
            <span>Редактировать профиль</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'

const auth = useAuthStore()
const router = useRouter()


onMounted(async () => {
  if (!auth.user && auth.isAuthenticated) {
    await auth.fetchMe()
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.applicant-dashboard {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.applicant-dashboard::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
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

.dashboard-header {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 24px 0;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  flex-shrink: 0;
}

.header-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
}

.header-title-section {
  flex: 1;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  letter-spacing: -1px;
  line-height: 1.2;
}

.dashboard-subtitle {
  font-size: 1rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.btn-back,
.btn-logout {
  padding: 12px 24px;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  cursor: pointer;
  font-family: inherit;
  position: relative;
  overflow: hidden;
}

.btn-back {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
}

.btn-back::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-back:hover::before {
  left: 100%;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-logout {
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border-color: rgba(255, 107, 107, 0.4);
}

.btn-logout:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
  border-color: rgba(255, 107, 107, 0.6);
}

.btn-icon {
  font-size: 1.1rem;
}

.dashboard-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px 32px;
  position: relative;
  z-index: 1;
  flex: 1;
  overflow-y: auto;
}

.profile-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.card-header-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.card-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.5px;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.info-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateX(8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}

.info-icon {
  font-size: 1.8rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  color: #ffffff;
  font-weight: 700;
  font-size: 1.1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.profile-actions {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-edit::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-edit:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(255, 255, 255, 0.4);
}

.btn-edit:hover::before {
  width: 400px;
  height: 400px;
}

.btn-edit:active {
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    padding: 0 24px;
    gap: 24px;
  }

  .dashboard-title {
    font-size: 2rem;
  }

  .dashboard-subtitle {
    font-size: 0.9rem;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .btn-back,
  .btn-logout {
    width: 100%;
    justify-content: center;
  }

  .dashboard-content {
    padding: 0 24px 40px;
  }

  .profile-card {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .card-title {
    font-size: 1.75rem;
  }

  .info-item {
    padding: 16px 20px;
    gap: 16px;
  }

  .info-icon {
    width: 40px;
    height: 40px;
    font-size: 1.5rem;
  }

  .btn-edit {
    width: 100%;
    justify-content: center;
    padding: 14px 24px;
  }
}
</style>
