<!-- src/pages/auth/LoginView.vue -->
<template>
  <div class="login-page">
    <h1>Вход</h1>

    <form class="login-form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>Email</span>
        <input
          v-model="email"
          type="email"
          required
          placeholder="admin@test.com"
        />
      </label>

      <label class="field">
        <span>Пароль</span>
        <input
          v-model="password"
          type="password"
          required
          placeholder="••••••••"
        />
      </label>

      <button class="btn" type="submit" :disabled="auth.loading">
        {{ auth.loading ? 'Входим...' : 'Войти' }}
      </button>

      <p v-if="auth.error" class="error">
        {{ auth.error }}
      </p>
    </form>

    <p class="hint">
      Нет аккаунта?
      <router-link :to="{ name: 'register' }">Зарегистрироваться</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const email = ref('')
const password = ref('')
const auth = useAuthStore()
const router = useRouter()

const handleSubmit = async () => {
  const ok = await auth.login({ email: email.value, password: password.value })
  if (ok) {
    const target = auth.getRedirectRouteByRole()
    router.push(target)
  }
}
</script>

<style scoped>
.login-page {
  max-width: 400px;
  margin: 80px auto;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #333;
  background: #111;
  color: #fff;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

input {
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #fff;
}

.btn {
  margin-top: 8px;
  padding: 10px 14px;
  background: #42b983;
  color: #000;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.7;
  cursor: default;
}

.error {
  color: #ff6b6b;
  font-size: 14px;
}

.hint {
  margin-top: 12px;
  font-size: 14px;
}

.hint a {
  color: #42b983;
}
</style>
