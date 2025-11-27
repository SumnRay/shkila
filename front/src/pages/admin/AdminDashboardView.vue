<!-- src/pages/admin/AdminDashboardView.vue -->
<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>Админ-панель</h1>
      <div class="admin-info" v-if="auth.user">
        <span>{{ auth.user.email }}</span>
        <span class="role-badge">ADMIN</span>
        <button @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="admin-main">
      <!-- Пользователи -->
      <section class="admin-card users-card">
        <h2>Пользователи</h2>

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
          <button @click="loadUsers" :disabled="loadingUsers">
            {{ loadingUsers ? 'Обновляем...' : 'Обновить' }}
          </button>
        </div>

        <p v-if="usersError" class="error">
          {{ usersError }}
        </p>

        <p v-if="loadingUsers">Загружаем пользователей...</p>

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
                <button @click="openEdit(u)">Изменить</button>
                <button class="danger" @click="handleDelete(u)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else-if="!loadingUsers && !users.length">
          Пользователей пока нет.
        </p>

        <!-- Панель редактирования -->
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
              <button type="submit" :disabled="savingUser">
                {{ savingUser ? 'Сохраняем...' : 'Сохранить' }}
              </button>
              <button type="button" @click="cancelEdit">Отмена</button>
            </div>

            <p v-if="editError" class="error">
              {{ editError }}
            </p>
          </form>
        </div>
      </section>

      <!-- Заглушка под будущие разделы -->
      <section class="admin-card">
        <h2>Платежи</h2>
        <p>Функционал работы с платежами будет добавлен позже.</p>
      </section>

      <section class="admin-card">
        <h2>Логи</h2>
        <p>Здесь будет отображаться история действий в системе.</p>
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

const loadUsers = async () => {
  loadingUsers.value = true
  usersError.value = null
  try {
    const params = {}
    if (search.value) params.search = search.value
    if (roleFilter.value) params.role = roleFilter.value

    const { data } = await adminGetUsers(params)
    // бэк возвращает обычный список без пагинации
    users.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('admin users load error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось загрузить пользователей'
  } finally {
    loadingUsers.value = false
  }
}

const handleChangeRole = async (user) => {
  try {
    await adminSetUserRole(user.id, user.role)
  } catch (err) {
    console.error('set role error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось изменить роль пользователя'
    // откатим на актуальные данные с сервера
    await loadUsers()
  }
}

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

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
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
.admin-page {
  min-height: 100vh;
  background: #080808;
  color: #f5f5f5;
  padding: 24px;
  box-sizing: border-box;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.admin-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid #444;
  font-size: 12px;
  text-transform: uppercase;
}

.admin-header button {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.admin-main {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.admin-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}

.users-card {
  grid-column: 1 / -1;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.filters input,
.filters select {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
}

.filters button {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: #1e88e5;
  color: #fff;
  cursor: pointer;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 14px;
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

.actions button {
  padding: 4px 8px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 12px;
}

.actions .danger {
  background: #c62828;
  color: #fff;
}

.edit-panel {
  margin-top: 16px;
  padding-top: 12px;
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
  font-size: 14px;
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

.edit-actions button {
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}

.error {
  color: #ff6b6b;
  font-size: 13px;
  margin-top: 4px;
}
</style>
