<!-- src/pages/admin/AdminCoursesView.vue -->
<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>Управление курсами</h1>
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
      <!-- Список курсов -->
      <section class="admin-card">
        <div class="section-header">
          <h2>Курсы</h2>
          <button class="btn" @click="openCreateCourseModal">+ Создать курс</button>
        </div>

        <p v-if="loading" class="status-text">Загружаем курсы...</p>
        <p v-if="error" class="error">{{ error }}</p>

        <div v-if="!loading && courses.length" class="courses-list">
          <div
            v-for="course in courses"
            :key="course.id"
            class="course-item"
            @click="selectCourse(course)"
          >
            <div class="course-item-header">
              <h3>{{ course.title }}</h3>
              <div class="course-item-actions">
                <button class="btn-icon" @click.stop="editCourse(course)" title="Редактировать">
                  ✏️
                </button>
                <button class="btn-icon" @click.stop="deleteCourse(course.id)" title="Удалить">
                  🗑️
                </button>
              </div>
            </div>
            <div class="course-meta">
              <span>Модулей: {{ course.modules_count || 0 }}</span>
            </div>
          </div>
        </div>

        <p v-if="!loading && !courses.length" class="empty-state">
          Курсов пока нет. Создайте первый курс.
        </p>
      </section>

      <!-- Детали выбранного курса -->
      <section v-if="selectedCourse" class="admin-card">
        <div class="section-header">
          <h2>Модули курса: {{ selectedCourse.title }}</h2>
          <button class="btn" @click="openCreateModuleModal">+ Добавить модуль</button>
        </div>

        <div v-if="selectedCourseModules.length" class="modules-list">
          <div
            v-for="module in selectedCourseModules"
            :key="module.id"
            class="module-item"
          >
            <div class="module-item-header">
              <h4>{{ module.title }}</h4>
              <div class="module-item-actions">
                <button class="btn-icon" @click="editModule(module)" title="Редактировать">
                  ✏️
                </button>
                <button class="btn-icon" @click="deleteModule(module.id)" title="Удалить">
                  🗑️
                </button>
              </div>
            </div>
            <p v-if="module.description" class="module-description">{{ module.description }}</p>
            <div class="module-meta">
              <span>Тем: {{ module.topics_count || 0 }}</span>
              <span>Порядок: {{ module.order }}</span>
            </div>

            <!-- Темы модуля -->
            <div class="topics-section">
              <div class="topics-header">
                <h5>Темы занятий</h5>
                <button class="btn-small" @click="openCreateTopicModal(module.id)">
                  + Добавить тему
                </button>
              </div>
              <div v-if="module.topics && module.topics.length" class="topics-list">
                <div
                  v-for="topic in module.topics"
                  :key="topic.id"
                  class="topic-item"
                >
                  <div class="topic-item-content">
                    <span class="topic-order">{{ topic.order }}.</span>
                    <div>
                      <strong>{{ topic.title }}</strong>
                      <p v-if="topic.description" class="topic-description">{{ topic.description }}</p>
                    </div>
                  </div>
                  <div class="topic-item-actions">
                    <button class="btn-icon" @click="editTopic(topic)" title="Редактировать">
                      ✏️
                    </button>
                    <button class="btn-icon" @click="deleteTopic(topic.id)" title="Удалить">
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
              <p v-else class="empty-topics">Тем пока нет</p>
            </div>
          </div>
        </div>

        <p v-else class="empty-state">Модулей пока нет. Добавьте первый модуль.</p>
      </section>
    </main>

    <!-- Модальное окно создания/редактирования курса -->
    <div v-if="showCourseModal" class="modal-backdrop" @click="closeCourseModal">
      <div class="modal" @click.stop>
        <h2>{{ editingCourse ? 'Редактировать курс' : 'Создать курс' }}</h2>
        <form @submit.prevent="saveCourse">
          <label class="field">
            <span>Название *</span>
            <input v-model="courseForm.title" type="text" required />
          </label>
          <div class="modal-actions">
            <button type="submit" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button type="button" @click="closeCourseModal">Отмена</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования модуля -->
    <div v-if="showModuleModal" class="modal-backdrop" @click="closeModuleModal">
      <div class="modal" @click.stop>
        <h2>{{ editingModule ? 'Редактировать модуль' : 'Создать модуль' }}</h2>
        <form @submit.prevent="saveModule">
          <label class="field">
            <span>Название *</span>
            <input v-model="moduleForm.title" type="text" required />
          </label>
          <label class="field">
            <span>Описание</span>
            <textarea v-model="moduleForm.description" rows="3"></textarea>
          </label>
          <label class="field">
            <span>Порядок</span>
            <input v-model.number="moduleForm.order" type="number" min="0" />
          </label>
          <div class="modal-actions">
            <button type="submit" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button type="button" @click="closeModuleModal">Отмена</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования темы -->
    <div v-if="showTopicModal" class="modal-backdrop" @click="closeTopicModal">
      <div class="modal" @click.stop>
        <h2>{{ editingTopic ? 'Редактировать тему' : 'Создать тему' }}</h2>
        <form @submit.prevent="saveTopic">
          <label class="field">
            <span>Название *</span>
            <input v-model="topicForm.title" type="text" required />
          </label>
          <label class="field">
            <span>Описание</span>
            <textarea v-model="topicForm.description" rows="3"></textarea>
          </label>
          <label class="field">
            <span>Порядок</span>
            <input v-model.number="topicForm.order" type="number" min="0" />
          </label>
          <div class="modal-actions">
            <button type="submit" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button type="button" @click="closeTopicModal">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import {
  adminGetCourses,
  adminCreateCourse,
  adminUpdateCourse,
  adminDeleteCourse,
  adminGetModules,
  adminCreateModule,
  adminUpdateModule,
  adminDeleteModule,
  adminGetLessonTopics,
  adminCreateLessonTopic,
  adminUpdateLessonTopic,
  adminDeleteLessonTopic,
} from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const courses = ref([])
const selectedCourse = ref(null)
const selectedCourseModules = ref([])
const loading = ref(false)
const error = ref(null)
const saving = ref(false)

// Модальные окна
const showCourseModal = ref(false)
const showModuleModal = ref(false)
const showTopicModal = ref(false)
const editingCourse = ref(false)
const editingModule = ref(false)
const editingTopic = ref(false)

// Формы
const courseForm = ref({
  title: '',
  description: '',
  default_lessons: 4,
  default_price: 0,
  is_active: true,
})

const moduleForm = ref({
  title: '',
  description: '',
  order: 0,
})

const topicForm = ref({
  title: '',
  description: '',
  order: 0,
})

let currentModuleId = null

// Загрузка курсов
const loadCourses = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await adminGetCourses()
    courses.value = data
  } catch (err) {
    console.error('Ошибка загрузки курсов:', err)
    error.value = 'Ошибка загрузки курсов'
  } finally {
    loading.value = false
  }
}

// Выбор курса
const selectCourse = async (course) => {
  // Используем объект из списка курсов, чтобы иметь актуальные данные
  const courseFromList = courses.value.find(c => c.id === course.id) || course
  selectedCourse.value = { ...courseFromList }
  await loadModules(course.id)
}

// Загрузка модулей курса
const loadModules = async (courseId) => {
  try {
    const { data } = await adminGetModules({ course_id: courseId })
    selectedCourseModules.value = data
  } catch (err) {
    console.error('Ошибка загрузки модулей:', err)
  }
}

// Курсы
const openCreateCourseModal = () => {
  editingCourse.value = false
  courseForm.value = {
    title: '',
  }
  showCourseModal.value = true
}

const closeCourseModal = () => {
  showCourseModal.value = false
  editingCourse.value = false
  currentEditingCourseId = null
}

let currentEditingCourseId = null

const editCourse = (course) => {
  editingCourse.value = true
  currentEditingCourseId = course.id
  courseForm.value = {
    title: course.title,
  }
  showCourseModal.value = true
}

const saveCourse = async () => {
  saving.value = true
  try {
    if (editingCourse.value && currentEditingCourseId) {
      const { data } = await adminUpdateCourse(currentEditingCourseId, courseForm.value)
      // Обновляем список курсов
      await loadCourses()
      // Обновляем выбранный курс, если он был отредактирован
      if (selectedCourse.value?.id === currentEditingCourseId) {
        // Используем данные из ответа API (с модулями) или из обновленного списка
        const updatedCourse = courses.value.find(c => c.id === currentEditingCourseId)
        if (updatedCourse) {
          selectedCourse.value = { ...updatedCourse }
          // Перезагружаем модули для обновленного курса
          await loadModules(currentEditingCourseId)
        } else if (data) {
          selectedCourse.value = { ...data }
          await loadModules(currentEditingCourseId)
        }
      }
    } else {
      await adminCreateCourse(courseForm.value)
      await loadCourses()
    }
    closeCourseModal()
  } catch (err) {
    console.error('Ошибка сохранения курса:', err)
    alert('Ошибка сохранения курса: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  } finally {
    saving.value = false
  }
}

const deleteCourse = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот курс?')) return
  try {
    await adminDeleteCourse(id)
    if (selectedCourse.value?.id === id) {
      selectedCourse.value = null
      selectedCourseModules.value = []
    }
    await loadCourses()
  } catch (err) {
    console.error('Ошибка удаления курса:', err)
    alert('Ошибка удаления курса: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  }
}

// Модули
const openCreateModuleModal = () => {
  if (!selectedCourse.value) return
  editingModule.value = false
  moduleForm.value = {
    title: '',
    description: '',
    order: selectedCourseModules.value.length,
  }
  showModuleModal.value = true
}

let currentEditingModuleId = null

const editModule = (module) => {
  editingModule.value = true
  currentEditingModuleId = module.id
  moduleForm.value = {
    title: module.title,
    description: module.description || '',
    order: module.order || 0,
  }
  showModuleModal.value = true
}

const closeModuleModal = () => {
  showModuleModal.value = false
  editingModule.value = false
  currentEditingModuleId = null
}

const saveModule = async () => {
  if (!selectedCourse.value) return
  saving.value = true
  try {
    const payload = {
      ...moduleForm.value,
      course_id: selectedCourse.value.id,
    }
    if (editingModule.value && currentEditingModuleId) {
      await adminUpdateModule(currentEditingModuleId, moduleForm.value)
    } else {
      await adminCreateModule(payload)
    }
    // Всегда перезагружаем модули после сохранения, чтобы получить актуальные данные с темами
    await loadModules(selectedCourse.value.id)
    closeModuleModal()
  } catch (err) {
    console.error('Ошибка сохранения модуля:', err)
    alert('Ошибка сохранения модуля: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  } finally {
    saving.value = false
  }
}

const deleteModule = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот модуль?')) return
  try {
    await adminDeleteModule(id)
    await loadModules(selectedCourse.value.id)
  } catch (err) {
    console.error('Ошибка удаления модуля:', err)
    alert('Ошибка удаления модуля: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  }
}

// Темы
const openCreateTopicModal = (moduleId) => {
  currentModuleId = moduleId
  editingTopic.value = false
  const module = selectedCourseModules.value.find(m => m.id === moduleId)
  topicForm.value = {
    title: '',
    description: '',
    order: module?.topics?.length || 0,
  }
  showTopicModal.value = true
}

let currentEditingTopicId = null

const editTopic = (topic) => {
  editingTopic.value = true
  currentEditingTopicId = topic.id
  topicForm.value = {
    title: topic.title,
    description: topic.description || '',
    order: topic.order || 0,
  }
  // Находим модуль, которому принадлежит тема
  for (const module of selectedCourseModules.value) {
    if (module.topics?.some(t => t.id === topic.id)) {
      currentModuleId = module.id
      break
    }
  }
  showTopicModal.value = true
}

const closeTopicModal = () => {
  showTopicModal.value = false
  editingTopic.value = false
  currentModuleId = null
  currentEditingTopicId = null
}

const saveTopic = async () => {
  if (!currentModuleId || !selectedCourse.value) return
  saving.value = true
  try {
    const payload = {
      ...topicForm.value,
      module_id: currentModuleId,
    }
    if (editingTopic.value && currentEditingTopicId) {
      await adminUpdateLessonTopic(currentEditingTopicId, topicForm.value)
    } else {
      await adminCreateLessonTopic(payload)
    }
    // Всегда перезагружаем модули после сохранения темы, чтобы получить актуальные данные
    await loadModules(selectedCourse.value.id)
    closeTopicModal()
  } catch (err) {
    console.error('Ошибка сохранения темы:', err)
    alert('Ошибка сохранения темы: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  } finally {
    saving.value = false
  }
}

const deleteTopic = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить эту тему?')) return
  try {
    await adminDeleteLessonTopic(id)
    await loadModules(selectedCourse.value.id)
  } catch (err) {
    console.error('Ошибка удаления темы:', err)
    alert('Ошибка удаления темы: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
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
  loadCourses()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #202124;
  color: #e8eaed;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #202124;
  border-bottom: 1px solid #3c4043;
}

.admin-header h1 {
  font-size: 22px;
  font-weight: 400;
  margin: 0;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 16px;
  background: #fbbc04;
  color: #202124;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 500;
}

.btn {
  padding: 6px 12px;
  color: white;
  background: #1e88e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  font-size: 13px;
}

.btn:hover {
  background: #1565c0;
}

.admin-main {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.admin-card {
  background: #1a1a1a;
  border: 1px solid #3c4043;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
}

.status-text {
  color: #9aa0a6;
  text-align: center;
  padding: 20px;
}

.error {
  color: #ea4335;
  text-align: center;
  padding: 20px;
}

.empty-state {
  color: #9aa0a6;
  text-align: center;
  padding: 40px;
}

.courses-list {
  display: grid;
  gap: 16px;
}

.course-item {
  background: #2d2d2d;
  border: 1px solid #3c4043;
  border-radius: 6px;
  padding: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.course-item:hover {
  background: #353535;
}

.course-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.course-item-header h3 {
  margin: 0;
  font-size: 16px;
}

.course-item-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  opacity: 0.7;
}

.btn-icon:hover {
  opacity: 1;
}

.course-description {
  color: #9aa0a6;
  margin: 8px 0;
  font-size: 14px;
}

.course-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9aa0a6;
}

.course-meta .inactive {
  color: #ea4335;
}

.modules-list {
  display: grid;
  gap: 20px;
}

.module-item {
  background: #2d2d2d;
  border: 1px solid #3c4043;
  border-radius: 6px;
  padding: 16px;
}

.module-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.module-item-header h4 {
  margin: 0;
  font-size: 15px;
}

.module-item-actions {
  display: flex;
  gap: 8px;
}

.module-description {
  color: #9aa0a6;
  margin: 8px 0;
  font-size: 14px;
}

.module-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9aa0a6;
  margin-bottom: 16px;
}

.topics-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #3c4043;
}

.topics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.topics-header h5 {
  margin: 0;
  font-size: 14px;
  color: #9aa0a6;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small:hover {
  background: #35a372;
}

.topics-list {
  display: grid;
  gap: 8px;
}

.topic-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1a1a1a;
  border: 1px solid #3c4043;
  border-radius: 4px;
  padding: 12px;
}

.topic-item-content {
  display: flex;
  gap: 12px;
  flex: 1;
}

.topic-order {
  color: #9aa0a6;
  font-weight: 500;
}

.topic-description {
  color: #9aa0a6;
  font-size: 12px;
  margin: 4px 0 0 0;
}

.topic-item-actions {
  display: flex;
  gap: 8px;
}

.empty-topics {
  color: #9aa0a6;
  font-size: 12px;
  text-align: center;
  padding: 12px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 500px;
  background: #1a1a1a;
  border: 1px solid #3c4043;
  border-radius: 12px;
  padding: 24px;
  color: #f5f5f5;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.field span {
  margin-bottom: 6px;
  color: #ccc;
  font-size: 0.9rem;
}

.field.checkbox-field {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.field input[type="text"],
.field input[type="number"],
.field textarea {
  background: #2d2d2d;
  border: 1px solid #444;
  color: white;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
}

.field textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #3c4043;
}

.modal-actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.modal-actions button[type="submit"] {
  background: #1e88e5;
  color: white;
}

.modal-actions button[type="submit"]:hover:not(:disabled) {
  background: #1565c0;
}

.modal-actions button[type="submit"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-actions button[type="button"] {
  background: #333;
  color: white;
}

.modal-actions button[type="button"]:hover {
  background: #444;
}
</style>
