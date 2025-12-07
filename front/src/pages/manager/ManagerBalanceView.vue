<!-- src/pages/manager/ManagerBalanceView.vue -->
<template>
  <div class="manager-balance-page">
    <header class="manager-header">
      <div class="title-block">
        <h1>Управление балансом</h1>
        <p class="subtitle">
          Просмотр и изменение баланса уроков у учеников.
        </p>
      </div>

      <div class="manager-info" v-if="auth.user">
        <div class="manager-user">
          <span class="manager-email">{{ auth.user.email }}</span>
          <span class="role-badge">MANAGER</span>
        </div>

        <div class="manager-actions">
          <button class="btn secondary" @click="goToDashboard">
            Панель менеджера
          </button>
          <button class="btn" @click="handleLogout">
            Выйти
          </button>
        </div>
      </div>
    </header>

    <main class="manager-main">
      <!-- ПОИСК УЧЕНИКА -->
      <section class="manager-card search-card">
        <h2>Поиск ученика</h2>
        <div class="search-form">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Email или ФИО ученика"
            @input="searchStudents"
          />
          <select v-model="selectedStudentId" @change="loadStudentBalance">
            <option value="">Выберите ученика</option>
            <option v-for="student in searchResults" :key="student.id" :value="student.id">
              {{ student.email }} - {{ student.student_full_name || 'Без ФИО' }}
            </option>
          </select>
        </div>
      </section>

      <!-- БАЛАНС УЧЕНИКА -->
      <section v-if="currentBalance" class="manager-card balance-card">
        <h2>Баланс ученика</h2>
        <div class="balance-info">
          <div class="balance-item">
            <span class="label">Email:</span>
            <span class="value">{{ currentBalance.student_email }}</span>
          </div>
          <div class="balance-item">
            <span class="label">Доступно уроков:</span>
            <span class="value large">{{ currentBalance.lessons_available }}</span>
          </div>
          <div class="balance-item">
            <span class="label">Обновлено:</span>
            <span class="value">{{ formatDate(currentBalance.updated_at) }}</span>
          </div>
        </div>

        <div class="balance-actions">
          <h3>Изменить баланс</h3>
          <div class="balance-form">
            <label>
              <span>Установить новое значение:</span>
              <input
                v-model.number="newBalance"
                type="number"
                min="0"
                placeholder="Количество уроков"
              />
            </label>
            <div class="or-divider">или</div>
            <label>
              <span>Изменить на:</span>
              <input
                v-model.number="balanceDelta"
                type="number"
                placeholder="+5 или -3"
              />
            </label>
            <button
              class="btn"
              @click="updateBalance"
              :disabled="updatingBalance || (!newBalance && !balanceDelta)"
            >
              {{ updatingBalance ? 'Сохраняем...' : 'Сохранить' }}
            </button>
          </div>
          <p v-if="updateError" class="error">{{ updateError }}</p>
          <p v-if="updateSuccess" class="success">{{ updateSuccess }}</p>
        </div>
      </section>

      <!-- СПИСОК ВСЕХ УЧЕНИКОВ С БАЛАНСОМ -->
      <section class="manager-card students-list-card">
        <div class="section-header">
          <h2>Все ученики</h2>
          <button class="btn small" @click="loadAllStudents" :disabled="loadingStudents">
            {{ loadingStudents ? 'Обновляем...' : 'Обновить' }}
          </button>
        </div>

        <p v-if="studentsError" class="error">{{ studentsError }}</p>
        <p v-if="loadingStudents" class="status-text">Загружаем учеников...</p>

        <table v-if="!loadingStudents && allStudents.length" class="students-table">
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
              <td>{{ student.balance || 0 }}</td>
              <td class="actions">
                <button class="btn small secondary" @click="selectStudent(student.id)">
                  Выбрать
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else-if="!loadingStudents && !allStudents.length" class="status-text">
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

// ===== НАВИГАЦИЯ =====
const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

const goToDashboard = () => {
  router.push({ name: 'manager-dashboard' })
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
.manager-balance-page {
  min-height: 100vh;
  background: #080808;
  color: #f5f5f5;
  padding: 24px;
  box-sizing: border-box;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.title-block h1 {
  font-size: 26px;
  font-weight: 600;
}

.subtitle {
  margin-top: 4px;
  font-size: 14px;
  color: #aaa;
}

.manager-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.manager-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.manager-email {
  font-size: 14px;
}

.role-badge {
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #444;
  font-size: 11px;
  text-transform: uppercase;
  background: #2e7d32;
}

.manager-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  background: #1e88e5;
  color: #fff;
  font-size: 13px;
}

.btn.secondary {
  background: #333;
  color: #f5f5f5;
}

.btn.small {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.manager-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.manager-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}

.search-card {
  grid-column: 1 / -1;
}

.balance-card {
  grid-column: 1 / 2;
}

.students-list-card {
  grid-column: 2 / 3;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.search-form input,
.search-form select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
  font-size: 14px;
}

.balance-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
  padding: 16px;
  background: #151515;
  border-radius: 8px;
}

.balance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-item .label {
  color: #aaa;
  font-size: 14px;
}

.balance-item .value {
  font-weight: 600;
  font-size: 14px;
}

.balance-item .value.large {
  font-size: 24px;
  color: #1e88e5;
}

.balance-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #333;
}

.balance-actions h3 {
  margin-top: 0;
  margin-bottom: 16px;
}

.balance-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.balance-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.balance-form label span {
  color: #aaa;
  font-size: 13px;
}

.balance-form input {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
  font-size: 14px;
}

.or-divider {
  text-align: center;
  color: #666;
  font-size: 12px;
  margin: 4px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 13px;
}

.students-table th,
.students-table td {
  border-bottom: 1px solid #333;
  padding: 8px;
  text-align: left;
}

.students-table th {
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 6px;
}

.error {
  color: #ff6b6b;
  font-size: 13px;
  margin-top: 8px;
}

.success {
  color: #4caf50;
  font-size: 13px;
  margin-top: 8px;
}

.status-text {
  font-size: 13px;
  color: #bbb;
  margin-top: 8px;
}

@media (max-width: 900px) {
  .manager-main {
    grid-template-columns: 1fr;
  }

  .balance-card,
  .students-list-card {
    grid-column: 1 / -1;
  }

  .manager-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .manager-info {
    align-items: flex-start;
  }
}
</style>
