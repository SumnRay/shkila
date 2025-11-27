<!-- src/pages/admin/AdminScheduleView.vue -->
<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>Календарь уроков</h1>

      <div class="admin-info" v-if="auth.user">
        <span>{{ auth.user.email }}</span>
        <span class="role-badge">ADMIN</span>

        <router-link class="btn" :to="{ name: 'admin-dashboard' }">
          Панель
        </router-link>

        <button class="btn" @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="admin-main">
      <!-- Панель управления неделей -->
      <section class="admin-card controls-card">
        <div class="controls-row">
          <button @click="shiftWeek(-1)">‹ Предыдущая неделя</button>
          <button @click="goToday">Сегодня</button>
          <button @click="shiftWeek(1)">Следующая неделя ›</button>
        </div>
        <div class="week-label">
          Неделя: {{ weekRangeLabel }}
        </div>
        <p class="hint">
          Клик по пустой ячейке создаёт урок на выбранные дату и время.
        </p>
      </section>

      <!-- КАЛЕНДАРЬ -->
      <section class="admin-card calendar-card">
        <div class="calendar">

          <!-- Заголовки дней -->
          <div class="calendar-header-row">
            <div class="calendar-cell time-col"></div>

            <div
              v-for="day in weekDays"
              :key="day.iso"
              class="calendar-cell day-col"
            >
              <div class="day-name">{{ day.weekday }}</div>
              <div class="day-date">{{ day.display }}</div>
            </div>
          </div>

          <!-- Тело календаря -->
          <div class="calendar-body">
            <div v-for="hour in timeSlots" :key="hour" class="calendar-row">

              <div class="calendar-cell time-col">
                {{ formatHour(hour) }}
              </div>

              <div
                v-for="day in weekDays"
                :key="day.iso + '-' + hour"
                class="calendar-cell slot"
                @click="openCreate(day.iso, hour)"
              >
                <div
                  v-for="lesson in lessonsBySlot[day.iso + '-' + hour] || []"
                  :key="lesson.id"
                  class="lesson-card"
                  @click.stop="selectLesson(lesson)"
                >
                  <div class="lesson-title">
                    {{ lesson.student_email || ('Уч. ID ' + lesson.student) }}
                  </div>
                  <div class="lesson-sub">
                    Препод: {{ lesson.teacher_email || ('ID ' + lesson.teacher) }}
                  </div>
                  <div class="lesson-status">
                    {{ lesson.status }}
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>

        <p v-if="lessonsLoading" class="status-text">Загружаем уроки...</p>
        <p v-if="lessonsError" class="error">{{ lessonsError }}</p>
      </section>

      <!-- ДЕТАЛИ УРОКА -->
      <section v-if="activeLesson" class="admin-card lesson-info-card">
        <h2>Информация об уроке</h2>

        <p><strong>Ученик:</strong> {{ activeLesson.student_email }}</p>
        <p><strong>Родитель:</strong> {{ activeLesson.parent_full_name }}</p>
        <p><strong>Преподаватель:</strong> {{ activeLesson.teacher_email }}</p>
        <p><strong>Статус:</strong> {{ activeLesson.status }}</p>
        <p><strong>Время:</strong> {{ formatDateTime(activeLesson.scheduled_at) }}</p>

        <p>
          <strong>Ссылка:</strong>
          <span v-if="activeLesson.link">
            <a :href="activeLesson.link" target="_blank">{{ activeLesson.link }}</a>
          </span>
          <span v-else>—</span>
        </p>

        <p><strong>Комментарий:</strong> {{ activeLesson.comment || '—' }}</p>
      </section>

      <!-- Модальное окно создания урока -->
      <div v-if="showCreateModal" class="modal-backdrop">
        <div class="modal">
          <h2>Создать урок</h2>

          <form @submit.prevent="handleCreate">

            <label class="field">
              <span>Дата</span>
              <input v-model="formDate" type="date" required />
            </label>

            <label class="field">
              <span>Время</span>
              <input v-model="formTime" type="time" required />
            </label>

            <label class="field">
              <span>ID ученика</span>
              <input v-model="formStudentId" type="number" min="1" required />
            </label>

            <label class="field">
              <span>ID учителя</span>
              <input v-model="formTeacherId" type="number" min="1" required />
            </label>

            <label class="field">
              <span>Ссылка (необязательно)</span>
              <input v-model="formLink" type="text" />
            </label>

            <label class="field">
              <span>Комментарий</span>
              <textarea v-model="formComment" rows="2"></textarea>
            </label>

            <div class="modal-actions">
              <button type="submit" :disabled="createLoading">
                {{ createLoading ? 'Создаём...' : 'Создать' }}
              </button>
              <button type="button" @click="closeCreate">Отмена</button>
            </div>

            <p v-if="createError" class="error">{{ createError }}</p>
          </form>
        </div>
      </div>

    </main>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

import { adminGetLessons, adminCreateLesson } from '../../api/lessons'

const auth = useAuthStore()
const router = useRouter()

// =====================================
// ДАТЫ
// =====================================

function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay() || 7
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - (day - 1))
  return d
}

function addDays(date, n) {
  const d = new Date(date)
  d.setDate(d.getDate() + n)
  return d
}

function toISO(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatRu(date) {
  const d = new Date(date)
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
}

const currentDate = ref(new Date())

const weekStart = computed(() => startOfWeek(currentDate.value))

const weekDays = computed(() => {
  const names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
  const arr = []
  for (let i = 0; i < 7; i++) {
    const d = addDays(weekStart.value, i)
    arr.push({
      date: d,
      iso: toISO(d),
      weekday: names[i],
      display: formatRu(d),
    })
  }
  return arr
})

const weekRangeLabel = computed(() => {
  const start = weekStart.value
  const end = addDays(start, 6)
  return `${formatRu(start)} — ${formatRu(end)}`
})

// =====================================
// УРОКИ
// =====================================

const timeSlots = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

const activeLesson = ref(null)

// Группируем уроки по слотам YYYY-MM-DD-HH
const lessonsBySlot = computed(() => {
  const map = {}
  for (const L of lessons.value) {
    if (!L.scheduled_at) continue
    const dt = new Date(L.scheduled_at)
    const key = `${toISO(dt)}-${dt.getHours()}`
    if (!map[key]) map[key] = []
    map[key].push(L)
  }
  return map
})

const loadLessons = async () => {
  lessonsLoading.value = true
  lessonsError.value = null

  try {
    const { data } = await adminGetLessons({
      date_from: toISO(weekStart.value),
      date_to: toISO(addDays(weekStart.value, 6)),
    })

    lessons.value = Array.isArray(data) ? data : data.results || []

  } catch (err) {
    lessonsError.value = 'Ошибка загрузки уроков'
    console.error(err)
  }

  lessonsLoading.value = false
}

const formatHour = (h) => `${String(h).padStart(2, '0')}:00`

const formatDateTime = (val) => {
  const d = new Date(val)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// =====================================
// СОЗДАНИЕ УРОКА
// =====================================

const showCreateModal = ref(false)
const formDate = ref('')
const formTime = ref('')
const formStudentId = ref('')
const formTeacherId = ref('')
const formLink = ref('')
const formComment = ref('')

const createLoading = ref(false)
const createError = ref('')

const openCreate = (iso, hour) => {
  formDate.value = iso
  formTime.value = `${String(hour).padStart(2, '0')}:00`
  formStudentId.value = ''
  formTeacherId.value = ''
  formLink.value = ''
  formComment.value = ''
  createError.value = ''
  showCreateModal.value = true
}

const closeCreate = () => {
  showCreateModal.value = false
}

const handleCreate = async () => {
  createError.value = ''

  const payload = {
    student: Number(formStudentId.value),
    teacher: Number(formTeacherId.value),
    scheduled_at: `${formDate.value}T${formTime.value}`,
    link: formLink.value || null,
    comment: formComment.value || '',
  }

  createLoading.value = true

  try {
    const { data } = await adminCreateLesson(payload)
    lessons.value.push(data)
    showCreateModal.value = false
  } catch (err) {
    console.error(err)
    createError.value = 'Ошибка создания урока'
  }

  createLoading.value = false
}

const selectLesson = (lesson) => {
  activeLesson.value = lesson
}

// =====================================
// НАВИГАЦИЯ НЕДЕЛИ
// =====================================

const shiftWeek = (delta) => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + delta * 7)
  currentDate.value = d
  loadLessons()
}

const goToday = () => {
  currentDate.value = new Date()
  loadLessons()
}

// =====================================
// АВТОРИЗАЦИЯ
// =====================================

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
  } else {
    loadLessons()
  }
})
</script>


<style scoped>
.admin-page {
  min-height: 100vh;
  background: #0a0a0a;
  color: #f5f5f5;
  padding: 24px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn {
  padding: 6px 12px;
  color: white;
  background: #1e88e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 8px;
  background: #333;
}

.admin-main {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.admin-card {
  background: #111;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #333;
}

.controls-card {
  grid-column: 1 / -1;
}

.calendar-card {
  grid-column: 1 / 2;
}

.lesson-info-card {
  grid-column: 2 / 3;
}

.controls-row button {
  margin-right: 8px;
  padding: 6px 10px;
  background: #1e88e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.calendar {
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
  font-size: 14px;
}

.calendar-header-row,
.calendar-row {
  display: grid;
  grid-template-columns: 70px repeat(7, 1fr);
}

.time-col {
  background: #101010;
  text-align: right;
  padding-right: 8px;
  color: #aaa;
}

.day-col {
  background: #151515;
  text-align: center;
  border-right: 1px solid #222;
}

.calendar-body {
  max-height: 600px;
  overflow-y: auto;
}

.slot {
  cursor: pointer;
  position: relative;
  min-height: 40px;
  border-right: 1px solid #222;
  border-bottom: 1px solid #222;
}

.slot:hover {
  background: #1a1a1a;
}

.lesson-card {
  background: #1e88e5;
  color: white;
  border-radius: 6px;
  padding: 4px 6px;
  margin: 2px 0;
  font-size: 12px;
}

.lesson-title {
  font-weight: bold;
}

.lesson-status {
  font-size: 11px;
  margin-top: 2px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  width: 340px;
  background: #111;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.field input,
.field textarea {
  background: #000;
  border: 1px solid #444;
  color: white;
  padding: 6px;
  border-radius: 6px;
}

.modal-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.error {
  color: #ff6b6b;
  margin-top: 8px;
}

.status-text {
  font-size: 13px;
  color: #aaa;
  margin-top: 8px;
}
</style>
