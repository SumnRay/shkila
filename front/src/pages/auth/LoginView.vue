<!-- src/pages/auth/LoginView.vue -->
<template>
  <div class="auth-page">
    <TopNavigationBar />
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-icon">🔐</div>
          <h1 class="auth-title">Вход</h1>
          <p class="auth-subtitle">Добро пожаловать обратно!</p>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">
              <span class="label-icon">📧</span>
              <span>Email</span>
            </label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="admin@test.com"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span class="label-icon">🔑</span>
              <span>Пароль</span>
            </label>
            <input
              v-model="password"
              type="password"
              required
              placeholder="••••••••"
              class="form-input"
            />
          </div>

          <button 
            class="btn-submit" 
            type="submit" 
            :disabled="auth.loading"
          >
            <span v-if="!auth.loading">Войти</span>
            <span v-else class="loading-text">
              <span class="spinner"></span>
              Входим...
            </span>
          </button>

          <div v-if="auth.error" class="error-message">
            <span class="error-icon">⚠️</span>
            <span>{{ auth.error }}</span>
          </div>
        </form>

        <div class="auth-footer">
          <p class="hint">
            Нет аккаунта?
            <router-link :to="{ name: 'register' }" class="auth-link">
              Зарегистрироваться
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'

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
* {
  box-sizing: border-box;
}

.auth-page {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.auth-page::before {
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

.auth-container {
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
}

.auth-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  padding: 48px 40px;
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

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.auth-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  letter-spacing: -1px;
}

.auth-subtitle {
  font-size: 1rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 0.95rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.label-icon {
  font-size: 1.2rem;
}

.form-input {
  padding: 16px 20px;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.btn-submit {
  margin-top: 8px;
  padding: 18px 24px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  font-weight: 700;
  font-size: 1.05rem;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-submit::before {
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

.btn-submit:hover:not(:disabled) {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(255, 255, 255, 0.4);
}

.btn-submit:hover:not(:disabled)::before {
  width: 400px;
  height: 400px;
}

.btn-submit:active:not(:disabled) {
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 10px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(102, 126, 234, 0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.4);
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

.error-icon {
  font-size: 1.2rem;
}

.auth-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.hint {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.auth-link {
  color: #ffffff;
  font-weight: 700;
  text-decoration: none;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.auth-link:hover {
  border-bottom-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .auth-card {
    padding: 36px 28px;
    border-radius: 20px;
  }

  .auth-icon {
    font-size: 3rem;
  }

  .auth-title {
    font-size: 2rem;
  }

  .auth-subtitle {
    font-size: 0.9rem;
  }

  .form-input {
    padding: 14px 18px;
    font-size: 0.95rem;
  }

  .btn-submit {
    padding: 16px 24px;
    font-size: 1rem;
  }
}
</style>
