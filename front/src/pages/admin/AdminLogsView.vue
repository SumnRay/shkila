<!-- src/pages/admin/AdminLogsView.vue -->
<template>
  <div class="admin-page">
    <TopNavigationBar />

    <main class="admin-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">📋 Система логов</h1>
          <p class="subtitle">История всех действий в системе</p>
        </div>
      </div>
      <section class="admin-card filters-card">
        <div class="card-header">
          <div class="card-icon">🔍</div>
          <h2 class="card-title">Фильтры</h2>
        </div>

        <div class="filters-row">
          <div class="filter-item">
            <label class="form-label">
              <span class="label-icon">🔎</span>
              <span>Поиск</span>
            </label>
            <input
              v-model="search"
              type="text"
              placeholder="Email пользователя, тип действия..."
              class="filter-input"
            />
          </div>

          <div class="filter-item">
            <label class="form-label">
              <span class="label-icon">⚡</span>
              <span>Тип действия</span>
            </label>
            <select v-model="actionFilter" class="filter-select">
              <option value="">Все действия</option>
              <option
                v-for="act in availableActions"
                :key="act"
                :value="act"
              >
                {{ act }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label class="form-label">
              <span class="label-icon">📊</span>
              <span>Сортировка</span>
            </label>
            <select v-model="ordering" @change="loadLogs" class="filter-select">
              <option value="-created_at">Новые сверху</option>
              <option value="created_at">Старые сверху</option>
            </select>
          </div>

          <div class="filter-item buttons">
            <button class="btn primary" @click="loadLogs" :disabled="loading">
              {{ loading ? '⏳ Обновляем...' : '🔄 Обновить' }}
            </button>
          </div>
        </div>

        <div class="hint-box">
          <p class="hint">
            <strong>💡 Подсказка:</strong> Лог фиксирует: создание/изменение/удаление пользователей, уроков,
            подтверждение оплат и другие важные действия. Поле
            <strong>actor_email</strong> — это кто именно сделал действие.
          </p>
        </div>
      </section>

      <section class="admin-card logs-card">
        <div class="card-header">
          <div class="card-icon">📜</div>
          <h2 class="card-title">История действий</h2>
        </div>

        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ error }}</span>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем логи...</p>
        </div>

        <div v-if="!loading && filteredLogs.length" class="table-container">
          <table class="logs-table">
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
        </div>

        <div v-else-if="!loading && !filteredLogs.length" class="empty-state">
          <p>Логи не найдены (по текущим фильтрам).</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
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
* {
  box-sizing: border-box;
}

.admin-page {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: rgba(40, 40, 40, 0.8);
  border-bottom: 1px solid rgba(255, 215, 0, 0.3);
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  flex-shrink: 0;
}

.title-block {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  letter-spacing: -1px;
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}

.admin-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-email {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.role-badge {
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.admin-actions {
  display: flex;
  gap: 10px;
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

.btn.danger {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
  border: 1px solid rgba(255, 68, 68, 0.4);
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

.btn.danger:hover:not(:disabled) {
  background: rgba(255, 68, 68, 0.3);
  border-color: rgba(255, 68, 68, 0.6);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.admin-main {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 24px 32px;
  display: grid;
  grid-template-columns: minmax(300px, 1fr) 2.5fr;
  gap: 20px;
  position: relative;
  z-index: 1;
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

.filters-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.label-icon {
  font-size: 1.1rem;
}

.filter-input,
.filter-select {
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

.filter-item.buttons {
  margin-top: 8px;
}

.hint-box {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hint {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.hint strong {
  color: #ffffff;
  font-weight: 700;
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

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.logs-table thead {
  background: rgba(255, 255, 255, 0.1);
}

.logs-table th {
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

.logs-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  vertical-align: top;
}

.logs-table tbody tr {
  transition: background 0.2s;
}

.logs-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.1);
}

.actor-email {
  word-break: break-all;
  font-weight: 500;
}

.action-tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #ffffff;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  letter-spacing: 0.5px;
}

.meta-pre {
  margin: 0;
  font-size: 0.75rem;
  max-height: 120px;
  overflow: auto;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Courier New', monospace;
  line-height: 1.5;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

@media (max-width: 1200px) {
  .admin-main {
    grid-template-columns: 1fr;
    padding: 0 24px 32px;
  }
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 20px 24px;
  }

  .page-title {
    font-size: 2rem;
  }

  .admin-info {
    align-items: flex-start;
    width: 100%;
  }

  .admin-actions {
    width: 100%;
    flex-direction: column;
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

  .table-container {
    overflow-x: scroll;
  }

  .logs-table {
    min-width: 800px;
  }
}
</style>
