<!-- src/pages/manager/ManagerBalanceView.vue -->
<template>
  <div class="manager-balance-page">
    <TopNavigationBar />

    <main class="balance-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">Управление балансами</h1>
          <p class="subtitle">
            Просмотр и изменение баланса уроков у учеников.
          </p>
        </div>
      </div>

      <!-- ПОИСК УЧЕНИКА -->
      <section class="balance-card search-card">
        <div class="card-header">
          <div class="card-icon">🔍</div>
          <h2 class="card-title">Поиск ученика</h2>
        </div>
        <div class="search-form">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Email или ФИО ученика"
            class="search-input"
            @input="searchStudents"
          />
          <select v-model="selectedStudentId" @change="loadStudentBalance" class="search-select">
            <option value="">Выберите ученика</option>
            <option v-for="student in searchResults" :key="student.id" :value="student.id">
              {{ student.email }} - {{ student.student_full_name || 'Без ФИО' }}
            </option>
          </select>
        </div>
      </section>

      <!-- БАЛАНС УЧЕНИКА -->
      <section v-if="currentBalance" class="balance-card balance-info-card">
        <div class="card-header">
          <div class="card-icon">💰</div>
          <h2 class="card-title">Баланс ученика</h2>
        </div>
        <div class="balance-info">
          <div class="balance-item">
            <span class="label">Email:</span>
            <span class="value">{{ currentBalance.student_email }}</span>
          </div>
          <div class="balance-item highlight">
            <span class="label">Доступно уроков:</span>
            <span class="value large">{{ currentBalance.lessons_available }}</span>
          </div>
          <div class="balance-item">
            <span class="label">Обновлено:</span>
            <span class="value">{{ formatDate(currentBalance.updated_at) }}</span>
          </div>
        </div>

        <div class="balance-actions">
          <h3 class="actions-title">Изменить баланс</h3>
          <div class="balance-form">
            <label class="form-label">
              <span class="label-text">Установить новое значение:</span>
              <input
                v-model.number="newBalance"
                type="number"
                min="0"
                placeholder="Количество уроков"
                class="form-input"
              />
            </label>
            <div class="or-divider">или</div>
            <label class="form-label">
              <span class="label-text">Изменить на:</span>
              <input
                v-model.number="balanceDelta"
                type="number"
                placeholder="+5 или -3"
                class="form-input"
              />
            </label>
            <button
              class="btn primary"
              @click="updateBalance"
              :disabled="updatingBalance || (!newBalance && !balanceDelta)"
            >
              {{ updatingBalance ? 'Сохраняем...' : 'Сохранить' }}
            </button>
          </div>
          <p v-if="updateError" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ updateError }}
          </p>
          <p v-if="updateSuccess" class="success-message">
            <span class="success-icon">✅</span>
            {{ updateSuccess }}
          </p>
        </div>
      </section>

      <!-- СПИСОК ВСЕХ УЧЕНИКОВ С БАЛАНСОМ -->
      <section class="balance-card students-list-card">
        <div class="card-header">
          <div class="card-icon">👥</div>
          <h2 class="card-title">Все ученики</h2>
          <button class="btn small secondary" @click="loadAllStudents" :disabled="loadingStudents">
            {{ loadingStudents ? '⏳ Обновляем...' : '🔄 Обновить' }}
          </button>
        </div>

        <div v-if="studentsError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ studentsError }}</span>
        </div>

        <div v-if="loadingStudents" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем учеников...</p>
        </div>

        <div v-if="!loadingStudents && allStudents.length" class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>ФИО</th>
                <th>Баланс</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in allStudents" :key="student.id">
                <td>{{ student.id }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.student_full_name || '—' }}</td>
                <td class="balance-cell">{{ student.balance || 0 }}</td>
                <td class="actions">
                  <button class="btn small secondary" @click="selectStudent(student.id)">
                    Выбрать
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-else-if="!loadingStudents && !allStudents.length" class="empty-state">
          Учеников пока нет.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import {
  managerGetClients,
  managerGetStudentBalance,
  managerUpdateStudentBalance
} from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref('')
const searchResults = ref([])
const selectedStudentId = ref('')
const currentBalance = ref(null)

const newBalance = ref(null)
const balanceDelta = ref(null)
const updatingBalance = ref(false)
const updateError = ref(null)
const updateSuccess = ref(null)

const allStudents = ref([])
const loadingStudents = ref(false)
const studentsError = ref(null)

// ===== ПОИСК УЧЕНИКОВ =====
const searchStudents = async () => {
  if (!searchQuery.value || searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }

  try {
    const { data } = await managerGetClients({
      search: searchQuery.value,
      role: 'STUDENT'
    })
    searchResults.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('search students error:', err)
  }
}

// ===== ЗАГРУЗКА БАЛАНСА УЧЕНИКА =====
const loadStudentBalance = async () => {
  if (!selectedStudentId.value) {
    currentBalance.value = null
    return
  }

  try {
    const { data } = await managerGetStudentBalance(selectedStudentId.value)
    currentBalance.value = data
    newBalance.value = null
    balanceDelta.value = null
    updateError.value = null
    updateSuccess.value = null
  } catch (err) {
    console.error('load balance error:', err)
    updateError.value = 'Не удалось загрузить баланс'
  }
}

// ===== ОБНОВЛЕНИЕ БАЛАНСА =====
const updateBalance = async () => {
  if (!selectedStudentId.value) return

  updatingBalance.value = true
  updateError.value = null
  updateSuccess.value = null

  try {
    const payload = {}
    if (newBalance.value !== null && newBalance.value !== '') {
      payload.lessons_available = Number(newBalance.value)
    } else if (balanceDelta.value !== null && balanceDelta.value !== '') {
      payload.delta = Number(balanceDelta.value)
    } else {
      updatingBalance.value = false
      return
    }

    const { data } = await managerUpdateStudentBalance(selectedStudentId.value, payload)
    currentBalance.value = data
    updateSuccess.value = 'Баланс успешно обновлён'
    
    // Обновляем список всех учеников
    await loadAllStudents()
  } catch (err) {
    console.error('update balance error:', err)
    updateError.value = err?.response?.data?.detail || 'Не удалось обновить баланс'
  } finally {
    updatingBalance.value = false
  }
}

// ===== ЗАГРУЗКА ВСЕХ УЧЕНИКОВ =====
const loadAllStudents = async () => {
  loadingStudents.value = true
  studentsError.value = null

  try {
    const { data } = await managerGetClients({ role: 'STUDENT' })
    const students = Array.isArray(data) ? data : data.results || []
    
    // Загружаем баланс для каждого ученика
    const studentsWithBalance = await Promise.all(
      students.map(async (student) => {
        try {
          const { data: balanceData } = await managerGetStudentBalance(student.id)
          return { ...student, balance: balanceData.lessons_available }
        } catch {
          return { ...student, balance: 0 }
        }
      })
    )

    allStudents.value = studentsWithBalance
  } catch (err) {
    console.error('load all students error:', err)
    studentsError.value = 'Не удалось загрузить список учеников'
  } finally {
    loadingStudents.value = false
  }
}

// ===== ВЫБОР УЧЕНИКА =====
const selectStudent = (studentId) => {
  selectedStudentId.value = studentId
  loadStudentBalance()
}

// ===== ФОРМАТИРОВАНИЕ ДАТЫ =====
const formatDate = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }

  // Если передан studentId в параметрах маршрута
  const studentId = route.params.studentId
  if (studentId) {
    selectedStudentId.value = studentId
    loadStudentBalance()
  }

  loadAllStudents()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.manager-balance-page {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding: 0;
  margin: 0;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.page-header {
  padding: 20px 24px 0;
  margin-bottom: 24px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.title-block {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: #FFFFFF;
  letter-spacing: -1px;
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.balance-main {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px 32px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  overflow-y: visible;
  overflow-x: hidden;
  box-sizing: border-box;
}

.balance-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.balance-card:hover {
  box-shadow: 0 12px 30px rgba(255, 215, 0, 0.3);
  border-color: #FF8C00;
  transform: translateY(-2px);
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
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  flex-wrap: wrap;
}

.card-icon {
  font-size: 2rem;
}

.card-title {
  font-size: 1.75rem;
  font-weight: 900;
  margin: 0;
  color: #FFFFFF;
  flex: 1;
}

.search-card {
  grid-column: 1 / -1;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.search-input,
.search-select {
  width: 100%;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus,
.search-select:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
  transform: translateY(-2px);
}

.search-select option {
  background: #667eea;
  color: #ffffff;
}

.balance-info-card {
  grid-column: 1 / 2;
}

.balance-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(50, 50, 50, 0.6);
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.balance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  gap: 12px;
}

.balance-item .label {
  flex-shrink: 0;
  min-width: 0;
}

.balance-item .value {
  flex-shrink: 0;
  text-align: right;
}

.balance-item.highlight {
  border-top: 2px solid rgba(255, 255, 255, 0.3);
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  padding: 16px 0;
}

.balance-item .label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.balance-item .value.large {
  font-size: 2.5rem;
  color: #FFD700;
  font-weight: 900;
}

.balance-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
}

.actions-title {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.balance-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.label-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-weight: 600;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.form-input {
  width: 100%;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-input:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
  transform: translateY(-2px);
}

.or-divider {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 600;
  margin: 4px 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
  white-space: nowrap;
  flex-shrink: 0;
  box-sizing: border-box;
}

.btn.primary {
  background: #FFD700;
  color: #1A1A1A;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.btn.secondary {
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
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

.btn.primary:hover:not(:disabled) {
  background: #FF8C00;
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  margin-top: 16px;
  font-size: 0.95rem;
  font-weight: 600;
}

.error-message {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
  border: 2px solid rgba(255, 68, 68, 0.4);
}

.success-message {
  background: rgba(76, 175, 80, 0.2);
  color: #a5d6a7;
  border: 2px solid rgba(76, 175, 80, 0.4);
}

.error-icon,
.success-icon {
  font-size: 1.2rem;
}

.students-list-card {
  grid-column: 2 / 3;
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
  overflow-y: visible;
  margin-top: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: rgba(40, 40, 40, 0.5);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.5);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.7);
}

.students-table {
  width: 100%;
  min-width: 600px;
  border-collapse: collapse;
  font-size: 0.95rem;
  table-layout: auto;
}

.students-table th,
.students-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.students-table th {
  white-space: nowrap;
}

.students-table td {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.students-table thead {
  background: rgba(255, 215, 0, 0.1);
}

.students-table th {
  font-weight: 700;
  color: #FFFFFF;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  font-size: 1rem;
}

.students-table td {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
}

.students-table tbody tr:hover {
  background: rgba(255, 215, 0, 0.1);
}

.balance-cell {
  font-weight: 700;
  font-size: 1.1rem;
  color: #ffffff;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  justify-content: flex-start;
  align-items: center;
}

.actions .btn {
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .balance-main {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 0 20px 28px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
    margin-bottom: 20px;
  }

  .page-title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 0.9rem;
  }

  .balance-main {
    padding: 0 16px 24px;
    gap: 16px;
  }

  .balance-card {
    padding: 20px;
  }

  .card-header {
    margin-bottom: 20px;
    padding-bottom: 16px;
    gap: 10px;
  }

  .card-icon {
    font-size: 1.5rem;
  }

  .card-title {
    font-size: 1.5rem;
  }

  .card-header .btn {
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }

  .search-form {
    gap: 12px;
  }

  .search-input,
  .search-select {
    font-size: 0.95rem;
  }

  .balance-info {
    padding: 16px;
    gap: 12px;
  }

  .balance-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 0;
  }

  .balance-item .label {
    font-size: 0.9rem;
  }

  .balance-item .value {
    text-align: left;
    font-size: 0.95rem;
  }

  .balance-item .value.large {
    font-size: 2rem;
  }

  .balance-actions {
    margin-top: 20px;
    padding-top: 20px;
  }

  .actions-title {
    font-size: 1.3rem;
  }

  .balance-form {
    gap: 12px;
  }

  .form-input {
    font-size: 0.95rem;
    padding: 10px 14px;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .table-container {
    margin-top: 12px;
    margin-left: -20px;
    margin-right: -20px;
    padding: 0 20px;
  }

  .students-table {
    min-width: 700px;
    font-size: 0.85rem;
  }

  .students-table th,
  .students-table td {
    padding: 10px 12px;
  }

  .students-table th {
    font-size: 0.9rem;
  }

  .actions {
    flex-direction: column;
    gap: 6px;
  }

  .actions .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 12px 0;
    margin-bottom: 16px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.85rem;
  }

  .balance-main {
    padding: 0 12px 20px;
    gap: 12px;
  }

  .balance-card {
    padding: 16px;
    border-width: 2px;
  }

  .card-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    gap: 8px;
  }

  .card-icon {
    font-size: 1.3rem;
  }

  .card-title {
    font-size: 1.2rem;
  }

  .search-form {
    gap: 10px;
  }

  .search-input,
  .search-select {
    font-size: 0.9rem;
    padding: 10px 12px;
  }

  .balance-info {
    padding: 12px;
    gap: 10px;
  }

  .balance-item {
    padding: 8px 0;
  }

  .balance-item .label {
    font-size: 0.85rem;
  }

  .balance-item .value {
    font-size: 0.9rem;
  }

  .balance-item .value.large {
    font-size: 1.5rem;
  }

  .balance-actions {
    margin-top: 16px;
    padding-top: 16px;
  }

  .actions-title {
    font-size: 1.1rem;
    margin-bottom: 16px;
  }

  .balance-form {
    gap: 10px;
  }

  .label-text {
    font-size: 0.85rem;
  }

  .form-input {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .or-divider {
    font-size: 0.85rem;
    margin: 2px 0;
  }

  .btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }

  .btn.small {
    padding: 8px 14px;
    font-size: 0.8rem;
  }

  .table-container {
    margin-top: 10px;
    margin-left: -16px;
    margin-right: -16px;
    padding: 0 16px;
  }

  .students-table {
    min-width: 600px;
    font-size: 0.8rem;
  }

  .students-table th,
  .students-table td {
    padding: 8px 10px;
  }

  .students-table th {
    font-size: 0.85rem;
  }

  .students-table td {
    max-width: 150px;
    font-size: 0.75rem;
  }

  .balance-cell {
    font-size: 0.9rem;
  }

  .error-message,
  .success-message {
    padding: 10px 12px;
    font-size: 0.85rem;
    margin-top: 12px;
  }

  .loading-state,
  .empty-state {
    padding: 30px 20px;
    font-size: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border-width: 3px;
  }
}
</style>
