<!-- src/pages/applicant/ApplicantDashboardView.vue -->
<template>
  <div class="applicant-dashboard">
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
      <div class="profile-card card">
        <h2>Профиль</h2>
        <div class="profile-info">
          <div class="info-item">
            <span class="label">Email:</span>
            <span class="value">{{ auth.user?.email || '—' }}</span>
          </div>
          <div class="info-item" v-if="auth.user?.phone">
            <span class="label">Телефон:</span>
            <span class="value">{{ auth.user.phone }}</span>
          </div>
          <div class="info-item" v-if="auth.user?.student_full_name">
            <span class="label">ФИО ученика:</span>
            <span class="value">{{ auth.user.student_full_name }}</span>
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
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'home' })
}

onMounted(async () => {
  if (!auth.user && auth.isAuthenticated) {
    await auth.fetchMe()
  }
})
</script>

<style scoped>
.applicant-dashboard {
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
  max-width: 800px;
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
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 32px;
}

.card h2 {
  margin: 0 0 24px 0;
  font-size: 1.5rem;
  color: #333;
  border-bottom: 2px solid #42b983;
  padding-bottom: 12px;
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

@media (max-width: 768px) {
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
}
</style>
