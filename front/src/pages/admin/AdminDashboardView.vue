<!-- src/pages/admin/AdminDashboardView.vue -->
<template>
  <div class="admin-page">
    <TopNavigationBar />

    <!-- ОСНОВНОЙ КОНТЕНТ -->
    <main class="admin-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">Админ-панель</h1>
          <p class="subtitle">
            Управление пользователями, расписанием и журналом логов.
          </p>
        </div>
      </div>
      <!-- ВЕРХНИЕ КАРТОЧКИ (навигаторы) -->
      <section class="admin-card quick-links-card">
        <div class="card-header">
          <div class="card-icon">⚡</div>
          <h2 class="card-title">Быстрые действия</h2>
        </div>
        <div class="quick-links">
          <div class="quick-link" @click="goToSchedule">
            <div class="ql-icon">📅</div>
            <div class="ql-content">
              <div class="ql-title">Календарь уроков</div>
              <div class="ql-desc">
                Смотреть расписание, создавать и переносить занятия для учеников и преподавателей.
              </div>
            </div>
          </div>

          <div class="quick-link" @click="goToLogs">
            <div class="ql-icon">📋</div>
            <div class="ql-content">
              <div class="ql-title">Система логов</div>
              <div class="ql-desc">
                История действий: создание и изменение уроков, аккаунтов и ролей.
              </div>
            </div>
          </div>

          <div class="quick-link" @click="loadUsers">
            <div class="ql-icon">👥</div>
            <div class="ql-content">
              <div class="ql-title">Управление пользователями</div>
              <div class="ql-desc">
                Список всех пользователей: роли, контакты, редактирование и удаление.
              </div>
            </div>
          </div>

          <div class="quick-link" @click="goToCourses">
            <div class="ql-icon">📚</div>
            <div class="ql-content">
              <div class="ql-title">Управление курсами</div>
              <div class="ql-desc">
                Создание и редактирование курсов, модулей и тем занятий.
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ПОЛЬЗОВАТЕЛИ -->
      <section class="admin-card users-card">
        <div class="card-header">
          <div class="card-icon">👥</div>
          <h2 class="card-title">Пользователи</h2>
        </div>

        <div class="section-header">
          <div class="filters">
            <div class="filter-group">
              <input
                v-model="search"
                type="text"
                placeholder="Поиск по email / ФИО"
                class="filter-input"
              />
            </div>

            <div class="filter-group">
              <select v-model="roleFilter" class="filter-select">
                <option value="">Все роли</option>
                <option value="ADMIN">ADMIN</option>
                <option value="MANAGER">MANAGER</option>
                <option value="TEACHER">TEACHER</option>
                <option value="STUDENT">STUDENT</option>
                <option value="APPLICANT">APPLICANT</option>
              </select>
            </div>

            <button class="btn small" @click="loadUsers" :disabled="loadingUsers">
              {{ loadingUsers ? '⏳ Обновляем...' : '🔄 Обновить' }}
            </button>
          </div>
        </div>

        <div v-if="usersError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ usersError }}</span>
        </div>

        <div v-if="loadingUsers" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем пользователей...</p>
        </div>

        <div v-if="!loadingUsers && users.length" class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Телефон</th>
                <th>ФИО ученика</th>
                <th>ФИО родителя</th>
                <th>Роль</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.phone || '—' }}</td>
                <td>{{ u.student_full_name || '—' }}</td>
                <td>{{ u.parent_full_name || '—' }}</td>
                <td>
                  <select
                    v-model="u.role"
                    class="role-select"
                    @change="handleChangeRole(u)"
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="MANAGER">MANAGER</option>
                    <option value="TEACHER">TEACHER</option>
                    <option value="STUDENT">STUDENT</option>
                    <option value="APPLICANT">APPLICANT</option>
                  </select>
                </td>
                <td class="actions">
                  <button class="btn-icon edit" @click="openEdit(u)" title="Изменить">
                    ✏️
                  </button>
                  <button class="btn-icon delete" @click="handleDelete(u)" title="Удалить">
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="!loadingUsers && !users.length" class="empty-state">
          <p>Пользователей пока нет.</p>
        </div>

        <!-- ПАНЕЛЬ РЕДАКТИРОВАНИЯ -->
        <div v-if="editUser" class="edit-panel">
          <div class="edit-panel-header">
            <h3>Редактирование пользователя #{{ editUser.id }}</h3>
            <button class="btn-icon close" @click="cancelEdit">×</button>
          </div>
          <form @submit.prevent="handleSave">
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">📧 Email</span>
                <input v-model="editForm.email" type="email" required class="form-input" />
              </label>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">📱 Телефон</span>
                <input v-model="editForm.phone" type="text" class="form-input" />
              </label>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">🎓 ФИО ученика</span>
                <input v-model="editForm.student_full_name" type="text" class="form-input" />
              </label>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">👨‍👩‍👧 ФИО родителя</span>
                <input v-model="editForm.parent_full_name" type="text" class="form-input" />
              </label>
            </div>

            <div class="edit-actions">
              <button class="btn primary" type="submit" :disabled="savingUser">
                {{ savingUser ? '⏳ Сохраняем...' : '💾 Сохранить' }}
              </button>
              <button class="btn secondary" type="button" @click="cancelEdit">
                Отмена
              </button>
            </div>

            <div v-if="editError" class="error-message">
              <span class="error-icon">⚠️</span>
              <span>{{ editError }}</span>
            </div>
          </form>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import {
  adminGetUsers,
  adminUpdateUser,
  adminDeleteUser,
  adminSetUserRole,
} from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const users = ref([])
const loadingUsers = ref(false)
const usersError = ref(null)

const search = ref('')
const roleFilter = ref('')

const editUser = ref(null)
const editForm = ref({
  email: '',
  phone: '',
  student_full_name: '',
  parent_full_name: '',
})
const savingUser = ref(false)
const editError = ref(null)

// ===== ЗАГРУЗКА ПОЛЬЗОВАТЕЛЕЙ =====
const loadUsers = async () => {
  loadingUsers.value = true
  usersError.value = null
  try {
    const params = {}
    if (search.value) params.search = search.value
    if (roleFilter.value) params.role = roleFilter.value

    const { data } = await adminGetUsers(params)
    users.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('admin users load error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось загрузить пользователей'
  } finally {
    loadingUsers.value = false
  }
}

// ===== СМЕНА РОЛИ =====
const handleChangeRole = async (user) => {
  try {
    await adminSetUserRole(user.id, user.role)
  } catch (err) {
    console.error('set role error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось изменить роль пользователя'
    await loadUsers()
  }
}

// ===== РЕДАКТИРОВАНИЕ =====
const openEdit = (user) => {
  editUser.value = { ...user }
  editForm.value = {
    email: user.email || '',
    phone: user.phone || '',
    student_full_name: user.student_full_name || '',
    parent_full_name: user.parent_full_name || '',
  }
  editError.value = null
}

const cancelEdit = () => {
  editUser.value = null
  editError.value = null
}

const handleSave = async () => {
  if (!editUser.value) return
  savingUser.value = true
  editError.value = null

  try {
    const payload = { ...editForm.value }
    const { data } = await adminUpdateUser(editUser.value.id, payload)
    const idx = users.value.findIndex((u) => u.id === data.id)
    if (idx !== -1) {
      users.value[idx] = data
    }
    editUser.value = null
  } catch (err) {
    console.error('update user error:', err)
    editError.value =
      err?.response?.data?.detail || 'Не удалось сохранить изменения'
  } finally {
    savingUser.value = false
  }
}

// ===== УДАЛЕНИЕ =====
const handleDelete = async (user) => {
  if (!confirm(`Удалить пользователя ${user.email}?`)) return
  try {
    await adminDeleteUser(user.id)
    users.value = users.value.filter((u) => u.id !== user.id)
    if (editUser.value?.id === user.id) {
      editUser.value = null
    }
  } catch (err) {
    console.error('delete user error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось удалить пользователя'
  }
}

// ===== НАВИГАЦИЯ / АВТОРИЗАЦИЯ =====
const goToSchedule = () => {
  router.push({ name: 'admin-schedule' })
}

const goToLogs = () => {
  router.push({ name: 'admin-logs' })
}

const goToCourses = () => {
  router.push({ name: 'admin-courses' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadUsers()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.admin-page {
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

.admin-page::before {
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
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: #c5cae9;
  font-weight: 500;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.btn.primary {
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

.btn.secondary {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn.danger {
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border: 1px solid rgba(255, 107, 107, 0.4);
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

.btn.danger:hover:not(:disabled) {
  background: rgba(255, 107, 107, 0.3);
  border-color: rgba(255, 107, 107, 0.6);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.admin-main {
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

.admin-card {
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
  letter-spacing: -0.5px;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.quick-link {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.quick-link:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.ql-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
  flex-shrink: 0;
}

.ql-content {
  flex: 1;
}

.ql-title {
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 8px;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.ql-desc {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.section-header {
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-input,
.filter-select {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
}

.filter-select {
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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
  margin-bottom: 20px;
}

.error-icon {
  font-size: 1.2rem;
}

.table-container {
  overflow-x: auto;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.users-table thead {
  background: rgba(255, 255, 255, 0.1);
}

.users-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.users-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.users-table tbody tr {
  transition: background 0.2s;
}

.users-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.1);
}

.role-select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.role-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.25);
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-icon.edit:hover {
  background: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

.btn-icon.delete:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: translateY(-2px);
}

.btn-icon.close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
}

.btn-icon.close:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.edit-panel {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
}

.edit-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.edit-panel-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.form-row {
  margin-bottom: 16px;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-text {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.form-input {
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 0.95rem;
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
}

.edit-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

@media (max-width: 1200px) {
  .admin-main {
    padding: 0 24px 32px;
  }

  .quick-links {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
  }

  .page-title {
    font-size: 2rem;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .admin-main {
    padding: 0 16px 24px;
  }

  .admin-card {
    padding: 24px 20px;
  }

  .quick-links {
    grid-template-columns: 1fr;
  }

  .table-container {
    overflow-x: scroll;
  }

  .users-table {
    min-width: 800px;
  }
}
</style>
