<!-- src/pages/manager/ManagerRequestsView.vue -->
<template>
  <div class="manager-requests-page">
    <TopNavigationBar />

    <main class="main-container">
      <div class="page-header">
        <h1>Связь с клиентами</h1>
        <div class="tabs">
          <button
            :class="['tab', { active: activeTab === 'active' }]"
            @click="activeTab = 'active'"
          >
            Новые обращения
          </button>
          <button
            :class="['tab', { active: activeTab === 'archive' }]"
            @click="activeTab = 'archive'"
          >
            Архив
          </button>
        </div>
      </div>

      <div class="content-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Загрузка обращений...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <span class="error-icon">⚠️</span>
          <span>{{ error }}</span>
        </div>

        <div v-else-if="requests.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>{{ activeTab === 'active' ? 'Нет новых обращений' : 'Архив пуст' }}</p>
        </div>

        <div v-else class="requests-list">
          <div
            v-for="request in requests"
            :key="request.id"
            class="request-card"
          >
            <div class="request-header">
              <div class="request-client">
                <div class="client-email">{{ request.client_email }}</div>
                <div class="request-date">{{ formatDate(request.created_at) }}</div>
              </div>
              <div class="request-status" :class="request.status.toLowerCase()">
                {{ getStatusText(request.status) }}
              </div>
            </div>

            <div v-if="request.comment" class="request-comment">
              {{ request.comment }}
            </div>
            <div v-else class="request-comment empty">
              Комментарий не указан
            </div>

            <div v-if="request.status === 'RESPONDED'" class="request-response-info">
              <div class="response-manager">
                <strong>Менеджер:</strong> {{ request.manager_email }}
              </div>
              <div class="response-date">
                <strong>Дата реакции:</strong> {{ formatDate(request.responded_at) }}
              </div>
            </div>

            <div v-if="request.status === 'SENT'" class="request-actions">
              <button
                class="btn-respond"
                @click="handleRespond(request.id)"
                :disabled="responding"
              >
                {{ responding ? 'Обработка...' : 'Отметить как обработанное' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'
import { managerGetClientRequests, managerUpdateClientRequest } from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()

const activeTab = ref('active')
const requests = ref([])
const loading = ref(false)
const error = ref(null)
const responding = ref(false)

const loadRequests = async () => {
  loading.value = true
  error.value = null

  try {
    const status = activeTab.value === 'archive' ? 'RESPONDED' : 'SENT'
    const { data } = await managerGetClientRequests({ status })
    requests.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load requests error:', err)
    error.value = 'Не удалось загрузить обращения'
  } finally {
    loading.value = false
  }
}

const handleRespond = async (requestId) => {
  responding.value = true
  try {
    await managerUpdateClientRequest(requestId, { status: 'RESPONDED' })
    // Если мы в активных, перезагружаем список
    if (activeTab.value === 'active') {
      await loadRequests()
    }
  } catch (err) {
    console.error('respond error:', err)
    error.value = 'Не удалось обновить статус обращения'
  } finally {
    responding.value = false
  }
}

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

const getStatusText = (status) => {
  const statusMap = {
    'SENT': 'Отправлено',
    'RESPONDED': 'Есть реакция на обращение',
  }
  return statusMap[status] || status
}

watch(activeTab, () => {
  loadRequests()
})

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadRequests()
})
</script>

<style scoped>
.manager-requests-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  position: relative;
}

.manager-requests-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
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

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  position: relative;
  z-index: 1;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 900;
  color: #ffffff;
  margin: 0 0 24px 0;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.tabs {
  display: flex;
  gap: 12px;
}

.tab {
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.tab:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.tab.active {
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border-color: rgba(255, 255, 255, 0.8);
}

.content-section {
  min-height: 400px;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.9);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  color: #ffb3b3;
}

.error-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 12px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  opacity: 0.7;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.request-card {
  background: rgba(76, 68, 118, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.request-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.6);
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.request-client {
  flex: 1;
}

.client-email {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 4px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.request-date {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.request-status {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.request-status.sent {
  background: rgba(255, 152, 0, 0.3);
  color: #ffcc80;
  border: 1px solid rgba(255, 152, 0, 0.5);
}

.request-status.responded {
  background: rgba(76, 175, 80, 0.3);
  color: #a5d6a7;
  border: 1px solid rgba(76, 175, 80, 0.5);
}

.request-comment {
  margin-bottom: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #ffffff;
  line-height: 1.6;
  white-space: pre-wrap;
}

.request-comment.empty {
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

.request-response-info {
  margin-bottom: 16px;
  padding: 16px;
  background: rgba(76, 175, 80, 0.15);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.9rem;
}

.response-manager,
.response-date {
  margin-bottom: 8px;
}

.response-manager:last-child,
.response-date:last-child {
  margin-bottom: 0;
}

.request-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-respond {
  padding: 10px 20px;
  background: rgba(76, 175, 80, 0.9);
  color: #ffffff;
  border: 1px solid rgba(76, 175, 80, 0.6);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-respond:hover:not(:disabled) {
  background: rgba(76, 175, 80, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-respond:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }

  .request-header {
    flex-direction: column;
    gap: 12px;
  }

  .request-status {
    align-self: flex-start;
  }
}
</style>



