<!-- src/pages/common/EditProfileView.vue -->
<template>
  <div class="edit-profile">
    <header class="profile-header">
      <div class="header-content">
        <h1>Редактирование профиля</h1>
        <router-link :to="{ name: 'applicant-dashboard' }" class="btn-back">← Назад</router-link>
      </div>
    </header>

    <div class="profile-content">
      <div class="profile-form card">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="example@mail.com"
            />
          </div>

          <div class="form-group">
            <label for="phone">Телефон</label>
            <input
              id="phone"
              v-model="formData.phone"
              type="text"
              placeholder="+7..."
            />
          </div>

          <div class="form-group">
            <label for="student_full_name">ФИО ученика</label>
            <input
              id="student_full_name"
              v-model="formData.student_full_name"
              type="text"
              placeholder="Иванов Иван Иванович"
            />
          </div>

          <div class="form-group">
            <label for="parent_full_name">ФИО родителя</label>
            <input
              id="parent_full_name"
              v-model="formData.parent_full_name"
              type="text"
              placeholder="Иванова Мария Петровна"
            />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="loading">
              {{ loading ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <router-link :to="{ name: 'applicant-dashboard' }" class="btn-cancel">
              Отмена
            </router-link>
          </div>

          <p v-if="error" class="error-message">
            {{ error }}
          </p>

          <p v-if="success" class="success-message">
            Профиль успешно обновлен!
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import apiClient from '../../api/http'

const auth = useAuthStore()
const router = useRouter()

const formData = ref({
  email: '',
  phone: '',
  student_full_name: '',
  parent_full_name: ''
})

const loading = ref(false)
const error = ref(null)
const success = ref(false)

const loadProfile = async () => {
  if (!auth.user && auth.isAuthenticated) {
    await auth.fetchMe()
  }
  
  if (auth.user) {
    formData.value = {
      email: auth.user.email || '',
      phone: auth.user.phone || '',
      student_full_name: auth.user.student_full_name || '',
      parent_full_name: auth.user.parent_full_name || ''
    }
  }
}

const handleSubmit = async () => {
  loading.value = true
  error.value = null
  success.value = false

  try {
    const { data } = await apiClient.patch('/api/auth/me/', formData.value)
    
    // Обновляем данные в store
    await auth.fetchMe()
    
    success.value = true
    
    // Через 2 секунды перенаправляем на главную
    setTimeout(() => {
      router.push({ name: 'applicant-dashboard' })
    }, 2000)
  } catch (err) {
    console.error('Ошибка обновления профиля:', err)
    
    if (err?.response?.data) {
      const data = err.response.data
      if (typeof data === 'string') {
        error.value = data
      } else if (data.detail) {
        error.value = data.detail
      } else if (data.email) {
        error.value = Array.isArray(data.email) ? data.email[0] : data.email
      } else {
        const messages = []
        for (const key in data) {
          const val = data[key]
          if (Array.isArray(val)) {
            messages.push(val.join(' '))
          } else if (typeof val === 'string') {
            messages.push(val)
          }
        }
        error.value = messages.join(' ') || 'Ошибка обновления профиля'
      }
    } else {
      error.value = 'Ошибка обновления профиля'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.edit-profile {
  min-height: 100vh;
  background: #f5f5f5;
}

.profile-header {
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

.profile-content {
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

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-weight: 500;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #fff;
  color: #333;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.form-group input::placeholder {
  color: #999;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-save {
  padding: 12px 24px;
  background: #42b983;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-save:hover:not(:disabled) {
  background: #35a372;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-cancel {
  padding: 12px 24px;
  background: transparent;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-block;
}

.btn-cancel:hover {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid #ff6b6b;
  border-radius: 8px;
  color: #ff6b6b;
  font-size: 0.9rem;
}

.success-message {
  margin-top: 16px;
  padding: 12px;
  background: rgba(66, 185, 131, 0.1);
  border: 1px solid #42b983;
  border-radius: 8px;
  color: #42b983;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .btn-back {
    width: 100%;
    text-align: center;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-save,
  .btn-cancel {
    width: 100%;
    text-align: center;
  }
}
</style>
