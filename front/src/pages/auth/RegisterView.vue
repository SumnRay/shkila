<!-- src/pages/auth/RegisterView.vue -->
<template>
  <div class="login-page">
    <h1>Регистрация</h1>

    <form class="login-form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>Email</span>
        <input
          v-model="email"
          type="email"
          required
          placeholder="parent@example.com"
        />
      </label>

      <label class="field">
        <span>Телефон</span>
        <input
          v-model="phone"
          type="text"
          required
          placeholder="+7..."
        />
      </label>

      <label class="field">
        <span>ФИО ученика</span>
        <input
          v-model="studentFullName"
          type="text"
          required
          placeholder="Иванов Иван Иванович"
        />
      </label>

      <label class="field">
        <span>ФИО родителя</span>
        <input
          v-model="parentFullName"
          type="text"
          required
          placeholder="Иванова Мария Петровна"
        />
      </label>

      <label class="field">
        <span>Пароль ученика</span>
        <input
          v-model="password"
          type="password"
          required
          placeholder="Пароль для входа ученика"
        />
      </label>

      <label class="field">
        <span>Пароль родителя</span>
        <input
          v-model="parentPassword"
          type="password"
          required
          placeholder="Пароль для входа родителя"
        />
      </label>

      <button class="btn" type="submit" :disabled="auth.loading">
        {{ auth.loading ? 'Регистрируем...' : 'Зарегистрироваться' }}
      </button>

      <p v-if="auth.error" class="error">
        {{ auth.error }}
      </p>
    </form>

    <p class="hint">
      Уже есть аккаунт?
      <router-link :to="{ name: 'login' }">Войти</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const email = ref('')
const phone = ref('')
const studentFullName = ref('')
const parentFullName = ref('')
const password = ref('')
const parentPassword = ref('')

const auth = useAuthStore()
const router = useRouter()

const handleSubmit = async () => {
  const ok = await auth.register({
    email: email.value,
    phone: phone.value,
    student_full_name: studentFullName.value,
    parent_full_name: parentFullName.value,
    password: password.value,
    parent_password: parentPassword.value,
  })

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
