<!-- src/pages/common/HomeView.vue -->
<template>
  <div class="home">
    <h1>Личный кабинет</h1>
    <p v-if="auth.user">
      Вы вошли как: {{ auth.user.email }} (роль: {{ auth.role || '—' }})
    </p>
    <button @click="handleLogout">Выйти</button>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.home {
  padding: 24px;
}
</style>
