<!-- src/pages/admin/AdminDashboardView.vue -->
<template>
  <div class="admin-page">
    <!-- ШАПКА -->
    <header class="admin-header">
      <div class="title-block">
        <h1>Админ-панель</h1>
        <p class="subtitle">
          Управление пользователями, расписанием и журналом логов.
        </p>
      </div>

      <div class="admin-info" v-if="auth.user">
        <div class="admin-user">
          <span class="admin-email">{{ auth.user.email }}</span>
          <span class="role-badge">ADMIN</span>
        </div>

        <div class="admin-actions">
          <button class="btn secondary" @click="goToSchedule">
            Календарь уроков
          </button>
          <button class="btn secondary" @click="goToLogs">
            Система логов
          </button>
          <button class="btn" @click="handleLogout">
            Выйти
          </button>
        </div>
      </div>
    </header>

    <!-- ОСНОВНОЙ КОНТЕНТ -->
    <main class="admin-main">
      <!-- ВЕРХНИЕ КАРТОЧКИ (навигаторы) -->
      <section class="admin-card quick-links-card">
        <h2>Быстрые действия</h2>
        <div class="quick-links">
          <div class="quick-link" @click="goToSchedule">
            <div class="ql-title">Календарь уроков</div>
            <div class="ql-desc">
              Смотреть расписание, создавать и переносить занятия для учеников
              и преподавателей.
            </div>
          </div>

          <div class="quick-link" @click="goToLogs">
            <div class="ql-title">Система логов</div>
            <div class="ql-desc">
              История действий: создание и изменение уроков, аккаунтов и ролей.
            </div>
          </div>

          <div class="quick-link" @click="loadUsers">
            <div class="ql-title">Управление пользователями</div>
            <div class="ql-desc">
              Список всех пользователей: роли, контакты, редактирование и
              удаление.
            </div>
          </div>
        </div>
      </section>

      <!-- ПОЛЬЗОВАТЕЛИ -->
      <section class="admin-card users-card">
        <div class="section-header">
          <h2>Пользователи</h2>
          <button class="btn small" @click="loadUsers" :disabled="loadingUsers">
            {{ loadingUsers ? 'Обновляем...' : 'Обновить список' }}
          </button>
        </div>

        <div class="filters">
          <input
            v-model="search"
            type="text"
            placeholder="Поиск по email / ФИО"
          />

          <select v-model="roleFilter">
            <option value="">Все роли</option>
            <option value="ADMIN">ADMIN</option>
            <option value="MANAGER">MANAGER</option>
            <option value="TEACHER">TEACHER</option>
            <option value="STUDENT">STUDENT</option>
            <option value="APPLICANT">APPLICANT</option>
          </select>
        </div>

        <p v-if="usersError" class="error">
          {{ usersError }}
        </p>

        <p v-if="loadingUsers" class="status-text">
          Загружаем пользователей...
        </p>

        <table
          v-if="!loadingUsers && users.length"
          class="users-table"
        >
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
                <button class="btn small secondary" @click="openEdit(u)">
                  Изменить
                </button>
                <button class="btn small danger" @click="handleDelete(u)">
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else-if="!loadingUsers && !users.length" class="status-text">
          Пользователей пока нет.
        </p>

        <!-- ПАНЕЛЬ РЕДАКТИРОВАНИЯ -->
        <div v-if="editUser" class="edit-panel">
          <h3>Редактирование пользователя #{{ editUser.id }}</h3>
          <form @submit.prevent="handleSave">
            <label>
              <span>Email</span>
              <input v-model="editForm.email" type="email" required />
            </label>

            <label>
              <span>Телефон</span>
              <input v-model="editForm.phone" type="text" />
            </label>

            <label>
              <span>ФИО ученика</span>
              <input v-model="editForm.student_full_name" type="text" />
            </label>

            <label>
              <span>ФИО родителя</span>
              <input v-model="editForm.parent_full_name" type="text" />
            </label>

            <div class="edit-actions">
              <button class="btn small" type="submit" :disabled="savingUser">
                {{ savingUser ? 'Сохраняем...' : 'Сохранить' }}
              </button>
              <button class="btn small secondary" type="button" @click="cancelEdit">
                Отмена
              </button>
            </div>

            <p v-if="editError" class="error">
              {{ editError }}
            </p>
          </form>
        </div>
      </section>

      <!-- ЗАГЛУШКИ ПОД ДРУГИЕ РАЗДЕЛЫ (платежи, логи и т.п. можно потом оживить) -->
      <section class="admin-card">
        <h2>Платежи</h2>
        <p class="muted">
          Здесь позже будет раздел работы с пакетами, оплатами и балансами уроков.
        </p>
      </section>

      <section class="admin-card">
        <h2>Прочее</h2>
        <p class="muted">
          Дополнительные сервисы админ-панели можно будет добавить сюда.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
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
const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

const goToSchedule = () => {
  router.push({ name: 'admin-schedule' })
}

const goToLogs = () => {
  router.push({ name: 'admin-logs' })
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
/* тот же стиль, что и раньше, без изменений по сути */
.admin-page {
  min-height: 100vh;
  background: #080808;
  color: #f5f5f5;
  padding: 24px;
  box-sizing: border-box;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.admin-header {
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

.admin-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-email {
  font-size: 14px;
}

.role-badge {
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #444;
  font-size: 11px;
  text-transform: uppercase;
}

.admin-actions {
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

.btn.danger {
  background: #c62828;
}

.btn.small {
  padding: 4px 8px;
  font-size: 12px;
}

/* layout */
.admin-main {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  grid-auto-rows: min-content;
  gap: 16px;
}

.admin-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}

.quick-links-card {
  grid-column: 1 / -1;
}

.users-card {
  grid-column: 1 / 3;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.quick-link {
  border-radius: 10px;
  border: 1px solid #333;
  padding: 10px 12px;
  background: #151515;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s, border-color 0.15s;
}

.quick-link:hover {
  background: #1c1c1c;
  border-color: #1e88e5;
  transform: translateY(-1px);
}

.ql-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.ql-desc {
  font-size: 13px;
  color: #bbb;
}

/* users table */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.filters input,
.filters select {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
  font-size: 13px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 4px;
  font-size: 13px;
}

.users-table th,
.users-table td {
  border-bottom: 1px solid #333;
  padding: 6px 8px;
  text-align: left;
}

.users-table th {
  font-weight: 600;
}

.role-select {
  padding: 4px 6px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 6px;
}

/* edit panel */
.edit-panel {
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid #333;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-panel form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-panel label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.edit-panel input {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
}

.edit-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.error {
  color: #ff6b6b;
  font-size: 13px;
  margin-top: 4px;
}

.status-text {
  font-size: 13px;
  color: #bbb;
  margin-top: 4px;
}

.muted {
  font-size: 13px;
  color: #999;
}

@media (max-width: 900px) {
  .admin-main {
    grid-template-columns: 1fr;
  }

  .users-card {
    grid-column: 1 / -1;
  }

  .admin-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-info {
    align-items: flex-start;
  }
}
</style>
