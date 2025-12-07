<!-- src/pages/teacher/TeacherDashboardView.vue -->
<template>
  <div class="teacher-page">
    <!-- ШАПКА -->
    <header class="teacher-header">
      <div class="title-block">
        <h1>Панель учителя</h1>
        <p class="subtitle">
          Управление расписанием занятий для ваших учеников.
        </p>
      </div>

      <div class="teacher-info" v-if="auth.user">
        <div class="teacher-user">
          <span class="teacher-email">{{ auth.user.email }}</span>
          <span class="role-badge">TEACHER</span>
        </div>

        <div class="teacher-actions">
          <button class="btn secondary" @click="goToSchedule">
            Расписание занятий
          </button>
          <button class="btn" @click="handleLogout">
            Выйти
          </button>
        </div>
      </div>
    </header>

    <!-- ОСНОВНОЙ КОНТЕНТ -->
    <main class="teacher-main">
      <!-- ВЕРХНИЕ КАРТОЧКИ (навигаторы) -->
      <section class="teacher-card quick-links-card">
        <h2>Быстрые действия</h2>
        <div class="quick-links">
          <div class="quick-link" @click="goToSchedule">
            <div class="ql-title">Расписание занятий</div>
            <div class="ql-desc">
              Проставлять расписание занятий для ваших учеников, просматривать и редактировать уроки.
            </div>
          </div>

          <div class="quick-link" @click="loadStudents">
            <div class="ql-title">Мои ученики</div>
            <div class="ql-desc">
              Просмотр списка всех ваших учеников, назначенных менеджером.
            </div>
          </div>
        </div>
      </section>

      <!-- СПИСОК УЧЕНИКОВ -->
      <section class="teacher-card students-card">
        <div class="section-header">
          <h2>Мои ученики</h2>
          <button class="btn small" @click="loadStudents" :disabled="loadingStudents">
            {{ loadingStudents ? 'Обновляем...' : 'Обновить список' }}
          </button>
        </div>

        <div class="filters">
          <input
            v-model="search"
            type="text"
            placeholder="Поиск по email / ФИО"
            @input="loadStudents"
          />
        </div>

        <p v-if="studentsError" class="error">
          {{ studentsError }}
        </p>

        <p v-if="loadingStudents" class="status-text">
          Загружаем учеников...
        </p>

        <table
          v-if="!loadingStudents && students.length"
          class="students-table"
        >
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>ФИО ученика</th>
              <th>ФИО родителя</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id">
              <td>{{ student.id }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.student_full_name || '—' }}</td>
              <td>{{ student.parent_full_name || '—' }}</td>
              <td class="actions">
                <button class="btn small secondary" @click="viewStudentSchedule(student)">
                  Расписание
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else-if="!loadingStudents && !students.length" class="status-text">
          У вас пока нет назначенных учеников. Обратитесь к менеджеру для назначения учеников.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { teacherGetStudents } from '../../api/teacher'

const auth = useAuthStore()
const router = useRouter()

const students = ref([])
const loadingStudents = ref(false)
const studentsError = ref(null)

const search = ref('')

// ===== ЗАГРУЗКА УЧЕНИКОВ =====
const loadStudents = async () => {
  loadingStudents.value = true
  studentsError.value = null
  try {
    const params = {}
    if (search.value) params.search = search.value

    const { data } = await teacherGetStudents(params)
    students.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('teacher students load error:', err)
    studentsError.value =
      err?.response?.data?.detail || 'Не удалось загрузить учеников'
  } finally {
    loadingStudents.value = false
  }
}

// ===== ПРОСМОТР РАСПИСАНИЯ УЧЕНИКА =====
const viewStudentSchedule = (student) => {
  router.push({ name: 'teacher-schedule', query: { studentId: student.id } })
}

// ===== НАВИГАЦИЯ / АВТОРИЗАЦИЯ =====
const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}

const goToSchedule = () => {
  router.push({ name: 'teacher-schedule' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadStudents()
})
</script>

<style scoped>
.teacher-page {
  min-height: 100vh;
  background: #080808;
  color: #f5f5f5;
  padding: 24px;
  box-sizing: border-box;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.teacher-header {
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

.teacher-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.teacher-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.teacher-email {
  font-size: 14px;
}

.role-badge {
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #444;
  font-size: 11px;
  text-transform: uppercase;
  background: #ff9800;
}

.teacher-actions {
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

/* layout */
.teacher-main {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  grid-auto-rows: min-content;
  gap: 16px;
}

.teacher-card {
  border-radius: 12px;
  border: 1px solid #333;
  padding: 16px;
  background: #111;
}

.quick-links-card {
  grid-column: 1 / -1;
}

.students-card {
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

/* students table */
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

.filters input {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #444;
  background: #000;
  color: #f5f5f5;
  font-size: 13px;
  flex: 1;
  min-width: 200px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 4px;
  font-size: 13px;
}

.students-table th,
.students-table td {
  border-bottom: 1px solid #333;
  padding: 6px 8px;
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
  margin-top: 4px;
}

.status-text {
  font-size: 13px;
  color: #bbb;
  margin-top: 4px;
}

@media (max-width: 900px) {
  .teacher-main {
    grid-template-columns: 1fr;
  }

  .students-card {
    grid-column: 1 / -1;
  }

  .teacher-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .teacher-info {
    align-items: flex-start;
  }
}
</style>
