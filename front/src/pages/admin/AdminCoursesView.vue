<!-- src/pages/admin/AdminCoursesView.vue -->
<template>
  <div class="admin-page">
    <TopNavigationBar />

    <main class="admin-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">📚 Управление курсами</h1>
          <p class="subtitle">Создание и редактирование курсов, модулей и тем</p>
        </div>
      </div>
      <!-- Список курсов -->
      <section class="admin-card">
        <div class="section-header">
          <div class="section-title-group">
            <div class="section-icon">📚</div>
            <h2>Курсы</h2>
          </div>
          <button class="btn primary" @click="openCreateCourseModal">+ Создать курс</button>
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
          <div class="section-title-group">
            <div class="section-icon">📖</div>
            <h2>Модули курса: {{ selectedCourse.title }}</h2>
          </div>
          <button class="btn primary" @click="openCreateModuleModal">+ Добавить модуль</button>
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
import TopNavigationBar from '../../components/TopNavigationBar.vue'
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


onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadCourses()
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

.admin-header {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
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
  text-decoration: none;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.section-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.status-text {
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 40px;
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.error {
  color: #ffffff;
  text-align: center;
  padding: 20px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.4);
  border-radius: 12px;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.empty-state {
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 40px;
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.courses-list {
  display: grid;
  gap: 20px;
}

.course-item {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.course-item:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.course-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.course-item-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.course-item-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 8px 12px;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.course-meta {
  display: flex;
  gap: 16px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.modules-list {
  display: grid;
  gap: 20px;
}

.module-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}

.module-item:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.module-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.module-item-header h4 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.module-description {
  color: rgba(255, 255, 255, 0.85);
  margin: 12px 0;
  font-size: 0.95rem;
  line-height: 1.6;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.module-meta {
  display: flex;
  gap: 20px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 16px;
  font-weight: 500;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.topics-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
}

.topics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.topics-header h5 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.btn-small {
  padding: 8px 16px;
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-small:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

.topics-list {
  display: grid;
  gap: 12px;
}

.topic-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.topic-item:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateX(4px);
}

.topic-item-content {
  display: flex;
  gap: 12px;
  flex: 1;
  align-items: flex-start;
}

.topic-order {
  color: #ffffff;
  font-weight: 700;
  font-size: 1rem;
  min-width: 24px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.topic-item-content strong {
  display: block;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.topic-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin: 4px 0 0 0;
  line-height: 1.5;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.topic-item-actions {
  display: flex;
  gap: 8px;
}

.empty-topics {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-align: center;
  padding: 20px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px) saturate(180%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal {
  width: 100%;
  max-width: 520px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  padding: 32px;
  color: #212529;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  gap: 8px;
}

.field span {
  color: #495057;
  font-size: 0.95rem;
  font-weight: 600;
}

.field.checkbox-field {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.field input[type="text"],
.field input[type="number"],
.field textarea {
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  background: #ffffff;
  color: #212529;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.field textarea {
  resize: vertical;
  min-height: 100px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-actions button {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.modal-actions button[type="submit"] {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.modal-actions button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.modal-actions button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.modal-actions button[type="button"] {
  background: rgba(0, 0, 0, 0.05);
  color: #495057;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-actions button[type="button"]:hover {
  background: rgba(0, 0, 0, 0.1);
}

@media (max-width: 1200px) {
  .admin-main {
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

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .section-header .btn {
    width: 100%;
  }
}
</style>
