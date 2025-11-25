<!-- src/pages/admin/AdminDashboardView.vue -->
<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>Админ-панель</h1>
      <div class="admin-info" v-if="auth.user">
        <span>{{ auth.user.email }}</span>
        <span class="role-badge">ADMIN</span>
        <button @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="admin-main">
      <section class="admin-card">
        <h2>Пользователи</h2>
        <p>Здесь потом будет список пользователей / фильтры / поиск.</p>
      </section>

      <section class="admin-card">
        <h2>Уроки и расписание</h2>
        <p>Тут сделаем управление уроками и расписанием.</p>
      </section>

      <section class="admin-card">
        <h2>Финансы</h2>
        <p>Баланс, платежи, пополнения и списания.</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid #555;
  font-size: 12px;
}

.admin-main {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.admin-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}
</style>
