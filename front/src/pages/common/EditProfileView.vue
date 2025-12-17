<!-- src/pages/common/EditProfileView.vue -->
<template>
  <div class="edit-profile">
    <TopNavigationBar />

    <div class="profile-content">
      <div class="page-header">
        <h1>Редактирование профиля</h1>
      </div>
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
            <router-link :to="cancelRoute" class="btn-cancel">
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import { updateMeApi } from '../../api/auth'

const auth = useAuthStore()
const router = useRouter()

const cancelRoute = computed(() => {
  const role = auth.normalizedRole
  if (role === 'student') {
    return { name: 'student-dashboard' }
  } else if (role === 'applicant') {
    return { name: 'applicant-dashboard' }
  }
  return { name: 'home' }
})

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
    const { data } = await updateMeApi(formData.value)
    
    // Обновляем данные в store
    await auth.fetchMe()
    
    success.value = true
    
    // Через 2 секунды перенаправляем в личный кабинет
    setTimeout(() => {
      const role = auth.normalizedRole
      if (role === 'student') {
        router.push({ name: 'student-dashboard' })
      } else if (role === 'applicant') {
        router.push({ name: 'applicant-dashboard' })
      } else {
        router.push({ name: 'home' })
      }
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
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  position: relative;
}

.profile-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 48px;
  position: relative;
  z-index: 1;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2rem;
  margin: 0;
  color: #FFFFFF;
  font-weight: 900;
  letter-spacing: -1px;
}

.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 12px 30px rgba(255, 215, 0, 0.3);
  border-color: #FF8C00;
  transform: translateY(-2px);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 0.95rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.form-group input {
  width: 100%;
  padding: 14px 18px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-save {
  padding: 12px 24px;
  background: #FFD700;
  color: #1A1A1A;
  border: 1px solid #FFD700;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
  font-family: inherit;
}

.btn-save:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  padding: 12px 24px;
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
  font-family: inherit;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.btn-cancel:hover {
  border-color: rgba(255, 107, 107, 0.6);
  color: #ffb3b3;
  background: rgba(255, 107, 107, 0.1);
}

.error-message {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.5);
  border-radius: 8px;
  color: #ffb3b3;
  font-size: 0.9rem;
  text-shadow: 0 1px 4px rgba(255, 107, 107, 0.3);
}

.success-message {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.9rem;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .profile-content {
    padding: 24px 16px 32px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .card {
    padding: 24px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-group input {
    padding: 12px 16px;
    font-size: 0.95rem;
  }

  .form-actions {
    flex-direction: column;
    gap: 10px;
  }

  .btn-save,
  .btn-cancel {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .profile-content {
    padding: 20px 12px 24px;
  }

  .page-header h1 {
    font-size: 1.3rem;
  }

  .card {
    padding: 20px;
  }

  .form-group {
    margin-bottom: 18px;
  }

  .form-group label {
    font-size: 0.9rem;
  }

  .form-group input {
    padding: 10px 14px;
    font-size: 0.9rem;
  }

  .btn-save,
  .btn-cancel {
    padding: 10px 20px;
    font-size: 0.95rem;
  }
}
</style>
