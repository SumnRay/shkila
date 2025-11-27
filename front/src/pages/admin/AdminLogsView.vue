<!-- src/pages/admin/AdminLogsView.vue -->
<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>Система логов</h1>

      <div class="admin-info" v-if="auth.user">
        <span>{{ auth.user.email }}</span>
        <span class="role-badge">ADMIN</span>
        <button @click="goDashboard">В админ-панель</button>
        <button @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="admin-main">
      <section class="admin-card filters-card">
        <h2>Фильтры</h2>

        <div class="filters-row">
          <div class="filter-item">
            <label>
              <span>Поиск</span>
              <input
                v-model="search"
                type="text"
                placeholder="Email пользователя, тип действия..."
              />
            </label>
          </div>

          <div class="filter-item">
            <label>
              <span>Тип действия</span>
              <select v-model="actionFilter">
                <option value="">Все действия</option>
                <option
                  v-for="act in availableActions"
                  :key="act"
                  :value="act"
                >
                  {{ act }}
                </option>
              </select>
            </label>
          </div>

          <div class="filter-item">
            <label>
              <span>Сортировка</span>
              <select v-model="ordering" @change="loadLogs">
                <option value="-created_at">Новые сверху</option>
                <option value="created_at">Старые сверху</option>
              </select>
            </label>
          </div>

          <div class="filter-item buttons">
            <button @click="loadLogs" :disabled="loading">
              {{ loading ? 'Обновляем...' : 'Обновить' }}
            </button>
          </div>
        </div>

        <p class="hint">
          Лог фиксирует: создание/изменение/удаление пользователей, уроков,
          подтверждение оплат и другие важные действия. Поле
          <strong>actor_email</strong> — это кто именно сделал действие.
        </p>
      </section>

      <section class="admin-card logs-card">
        <h2>История действий</h2>

        <p v-if="error" class="error">
          {{ error }}
        </p>
        <p v-if="loading" class="status-text">
          Загружаем логи...
        </p>

        <table v-if="!loading && filteredLogs.length" class="logs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Время</th>
              <th>Пользователь</th>
              <th>Действие</th>
              <th>Детали (meta)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filteredLogs" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ formatDateTime(log.created_at) }}</td>
              <td>
                <div class="actor-email">
                  {{ log.actor_email || ('ID ' + log.actor) }}
                </div>
              </td>
              <td>
                <span class="action-tag">
                  {{ log.action }}
                </span>
              </td>
              <td>
                <pre class="meta-pre">{{ prettyMeta(log.meta) }}</pre>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else-if="!loading && !filteredLogs.length">
          Логи не найдены (по текущим фильтрам).
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminGetAuditLogs } from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const logs = ref([])
const loading = ref(false)
const error = ref(null)

const search = ref('')
const actionFilter = ref('')
const ordering = ref('-created_at')

// загрузка логов с бэка
const loadLogs = async () => {
  loading.value = true
  error.value = null

  try {
    const params = {
      ordering: ordering.value,
    }
    if (search.value) {
      params.search = search.value
    }

    const { data } = await adminGetAuditLogs(params)
    // если включена пагинация: data.results, если нет: список
    logs.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('Ошибка загрузки логов:', err)
    error.value =
      err?.response?.data?.detail ||
      'Не удалось загрузить логи. Проверьте права и токен.'
  } finally {
    loading.value = false
  }
}

// доступные типы действий (на основе полученных логов)
const availableActions = computed(() => {
  const set = new Set()
  for (const log of logs.value) {
    if (log.action) set.add(log.action)
  }
  return Array.from(set).sort()
})

// фильтрация по типу действия (клиентская)
const filteredLogs = computed(() => {
  if (!actionFilter.value) return logs.value
  return logs.value.filter((log) => log.action === actionFilter.value)
})

// форматирование даты
const formatDateTime = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// красивый вывод meta
const prettyMeta = (meta) => {
  if (!meta) return '—'
  try {
    return JSON.stringify(meta, null, 2)
  } catch (e) {
    return String(meta)
  }
}

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

const goDashboard = () => {
  router.push({ name: 'admin-dashboard' })
}

// При первом заходе: проверяем auth и грузим логи
onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
  } else {
    loadLogs()
  }
})

// Если меняем строку поиска — просто не автоматически дергаем бэкенд каждую букву.
// Можно сделать debounce, но пока — ручная кнопка "Обновить".

// Если хочешь автообновление при изменении search — раскомментируй:
// watch(search, () => {
//   loadLogs()
// })
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
  margin-bottom: 16px;
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

.admin-info button {
  padding: 6px 10px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid #444;
  font-size: 12px;
  text-transform: uppercase;
}

.admin-main {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 3fr;
  gap: 16px;
}

.admin-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}

.filters-card h2,
.logs-card h2 {
  margin-bottom: 8px;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 180px;
}

.filter-item input,
.filter-item select {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
  font-size: 13px;
}

.filter-item.buttons {
  justify-content: flex-end;
}

.filter-item.buttons button {
  margin-top: 18px;
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: #1e88e5;
  color: #fff;
  cursor: pointer;
}

.hint {
  font-size: 13px;
  color: #aaa;
  margin-top: 4px;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 8px;
}

.logs-table th,
.logs-table td {
  border-bottom: 1px solid #333;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}

.logs-table th {
  font-weight: 600;
}

.actor-email {
  word-break: break-all;
}

.action-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 999px;
  border: 1px solid #555;
  font-size: 11px;
  text-transform: uppercase;
}

.meta-pre {
  margin: 0;
  font-size: 11px;
  max-height: 120px;
  overflow: auto;
  background: #050505;
  border-radius: 4px;
  padding: 4px 6px;
  border: 1px solid #222;
}

.error {
  color: #ff6b6b;
  font-size: 13px;
}

.status-text {
  font-size: 13px;
}

@media (max-width: 900px) {
  .admin-main {
    grid-template-columns: 1fr;
  }
}
</style>
