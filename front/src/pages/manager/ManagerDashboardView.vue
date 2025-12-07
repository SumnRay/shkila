<!-- src/pages/manager/ManagerDashboardView.vue -->
<template>
  <div class="manager-page">
    <!-- ШАПКА -->
    <header class="manager-header">
      <div class="title-block">
        <h1>Панель менеджера</h1>
        <p class="subtitle">
          Управление уроками и балансом учеников.
        </p>
      </div>

      <div class="manager-info" v-if="auth.user">
        <div class="manager-user">
          <span class="manager-email">{{ auth.user.email }}</span>
          <span class="role-badge">MANAGER</span>
        </div>

        <div class="manager-actions">
          <button class="btn secondary" @click="goToSchedule">
            Календарь уроков
          </button>
          <button class="btn secondary" @click="goToBalance">
            Управление балансом
          </button>
          <button class="btn" @click="handleLogout">
            Выйти
          </button>
        </div>
      </div>
    </header>

    <!-- ОСНОВНОЙ КОНТЕНТ -->
    <main class="manager-main">
      <!-- ВЕРХНИЕ КАРТОЧКИ (навигаторы) -->
      <section class="manager-card quick-links-card">
        <h2>Быстрые действия</h2>
        <div class="quick-links">
          <div class="quick-link" @click="goToSchedule">
            <div class="ql-title">Календарь уроков</div>
            <div class="ql-desc">
              Смотреть расписание, создавать и редактировать занятия для учеников
              и преподавателей.
            </div>
          </div>

          <div class="quick-link" @click="goToBalance">
            <div class="ql-title">Управление балансом</div>
            <div class="ql-desc">
              Просмотр и изменение баланса уроков у учеников, подтверждение платежей.
            </div>
          </div>

          <div class="quick-link" @click="loadClients">
            <div class="ql-title">Список клиентов</div>
            <div class="ql-desc">
              Просмотр всех клиентов (учеников и абитуриентов) с возможностью поиска.
            </div>
          </div>
        </div>
      </section>

      <!-- КЛИЕНТЫ -->
      <section class="manager-card clients-card">
        <div class="section-header">
          <h2>Клиенты</h2>
          <button class="btn small" @click="loadClients" :disabled="loadingClients">
            {{ loadingClients ? 'Обновляем...' : 'Обновить список' }}
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
            <option value="STUDENT">STUDENT</option>
            <option value="APPLICANT">APPLICANT</option>
          </select>
        </div>

        <p v-if="clientsError" class="error">
          {{ clientsError }}
        </p>

        <p v-if="loadingClients" class="status-text">
          Загружаем клиентов...
        </p>

        <table
          v-if="!loadingClients && clients.length"
          class="clients-table"
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
            <tr v-for="c in clients" :key="c.id">
              <td>{{ c.id }}</td>
              <td>{{ c.email }}</td>
              <td>{{ c.phone || '—' }}</td>
              <td>{{ c.student_full_name || '—' }}</td>
              <td>{{ c.parent_full_name || '—' }}</td>
              <td>{{ c.role }}</td>
              <td class="actions">
                <button class="btn small secondary" @click="viewBalance(c)">
                  Баланс
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else-if="!loadingClients && !clients.length" class="status-text">
          Клиентов пока нет.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { managerGetClients } from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()

const clients = ref([])
const loadingClients = ref(false)
const clientsError = ref(null)

const search = ref('')
const roleFilter = ref('')

// ===== ЗАГРУЗКА КЛИЕНТОВ =====
const loadClients = async () => {
  loadingClients.value = true
  clientsError.value = null
  try {
    const params = {}
    if (search.value) params.search = search.value
    if (roleFilter.value) params.role = roleFilter.value

    const { data } = await managerGetClients(params)
    clients.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('manager clients load error:', err)
    clientsError.value =
      err?.response?.data?.detail || 'Не удалось загрузить клиентов'
  } finally {
    loadingClients.value = false
  }
}

// ===== ПРОСМОТР БАЛАНСА =====
const viewBalance = (client) => {
  router.push({ name: 'manager-balance', params: { studentId: client.id } })
}

// ===== НАВИГАЦИЯ / АВТОРИЗАЦИЯ =====
const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

const goToSchedule = () => {
  router.push({ name: 'manager-schedule' })
}

const goToBalance = () => {
  router.push({ name: 'manager-balance' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadClients()
})
</script>

<style scoped>
.manager-page {
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

.btn:hover {
  opacity: 0.9;
}

/* layout */
.manager-main {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  grid-auto-rows: min-content;
  gap: 16px;
}

.manager-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}

.quick-links-card {
  grid-column: 1 / -1;
}

.clients-card {
  grid-column: 1 / -1;
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

/* clients table */
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

.clients-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 4px;
  font-size: 13px;
}

.clients-table th,
.clients-table td {
  border-bottom: 1px solid #333;
  padding: 6px 8px;
  text-align: left;
}

.clients-table th {
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 6px;
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

@media (max-width: 900px) {
  .manager-main {
    grid-template-columns: 1fr;
  }

  .clients-card {
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


