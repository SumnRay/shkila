<!-- src/pages/teacher/TeacherStudentsView.vue -->
<template>
  <div class="teacher-students-page">
    <TopNavigationBar />

    <main class="students-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">Список учеников</h1>
          <p class="subtitle">
            Просмотр всех ваших учеников и их информации.
          </p>
        </div>
      </div>

      <!-- ПОИСК -->
      <section class="students-card search-card">
        <div class="card-header">
          <div class="card-icon">🔍</div>
          <h2 class="card-title">Поиск учеников</h2>
        </div>
        <div class="search-form">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по email, ФИО ученика или родителя"
            class="search-input"
            @input="handleSearch"
          />
          <button class="btn secondary" @click="loadStudents" :disabled="loadingStudents">
            {{ loadingStudents ? '⏳ Загружаем...' : '🔄 Обновить' }}
          </button>
        </div>
      </section>

      <!-- СПИСОК УЧЕНИКОВ -->
      <section class="students-card students-list-card">
        <div class="card-header">
          <div class="card-icon">👥</div>
          <h2 class="card-title">Мои ученики</h2>
        </div>

        <div v-if="studentsError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ studentsError }}</span>
        </div>

        <div v-if="loadingStudents" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем учеников...</p>
        </div>

        <div v-if="!loadingStudents && students.length" class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>ФИО ученика</th>
                <th>ФИО родителя</th>
                <th>Телефон</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.id">
                <td>{{ student.id }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.student_full_name || '—' }}</td>
                <td>{{ student.parent_full_name || '—' }}</td>
                <td>{{ student.phone || '—' }}</td>
                <td class="actions">
                  <button class="btn small secondary" @click="viewStudentLessons(student)">
                    Уроки
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-else-if="!loadingStudents && !students.length" class="empty-state">
          Учеников пока нет.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import { teacherGetStudents } from '../../api/teacher'

const auth = useAuthStore()
const router = useRouter()

const students = ref([])
const loadingStudents = ref(false)
const studentsError = ref(null)
const searchQuery = ref('')

// ===== ЗАГРУЗКА УЧЕНИКОВ =====
const loadStudents = async () => {
  loadingStudents.value = true
  studentsError.value = null

  try {
    const params = {}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const { data } = await teacherGetStudents(params)
    students.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load students error:', err)
    studentsError.value = err?.response?.data?.detail || 'Не удалось загрузить список учеников'
  } finally {
    loadingStudents.value = false
  }
}

// ===== ПОИСК =====
let searchTimeout = null
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadStudents()
  }, 500)
}

// ===== ПРОСМОТР УРОКОВ УЧЕНИКА =====
const viewStudentLessons = (student) => {
  router.push({ 
    name: 'teacher-schedule',
    query: { studentId: student.id }
  })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadStudents()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.teacher-students-page {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  padding: 0;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.teacher-students-page::before {
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

.page-header {
  padding: 20px 24px 0;
  margin-bottom: 24px;
}

.title-block {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #e8eaf6;
  letter-spacing: -1px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: #c5cae9;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.students-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 32px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  overflow-y: auto;
}

.students-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.4s ease-out;
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

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.card-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.card-title {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  flex: 1;
}

.search-card {
  grid-column: 1 / -1;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.btn.secondary {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn.small {
  padding: 8px 16px;
  font-size: 0.85rem;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  margin-top: 16px;
  font-size: 0.95rem;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.2);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border: 1px solid rgba(239, 68, 68, 0.4);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.error-icon {
  font-size: 1.2rem;
}

.students-list-card {
  grid-column: 1 / -1;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.table-container {
  overflow-x: auto;
  margin-top: 16px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.students-table th,
.students-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.students-table th {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  font-size: 1rem;
}

.students-table td {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 1200px) {
  .students-main {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .card-title {
    font-size: 1.5rem;
  }

  .search-form {
    flex-direction: column;
    align-items: stretch;
  }

  .students-table {
    font-size: 0.85rem;
  }

  .students-table th,
  .students-table td {
    padding: 8px 12px;
  }
}
</style>
