<!-- src/components/ScheduleView.vue -->
<template>
  <div class="schedule-view">
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
            >
              <!-- Контейнер для всех карточек уроков (80% ширины) -->
              <div class="slot-lessons-container">
                <div
                  v-for="lesson in lessonsBySlot[day.iso + '-' + hour] || []"
                  :key="lesson.id"
                  :class="['lesson-card', `lesson-card--${lesson.status?.toLowerCase() || 'planned'}`]"
                  @click.stop="selectLesson(lesson)"
                >
                  <div class="lesson-time">
                    {{ formatLessonTime(lesson.scheduled_at) }}
                  </div>
                  <div class="lesson-student">
                    {{ lesson.student_email || ('Уч. ID ' + lesson.student) }}
                  </div>
                </div>
              </div>
              <!-- Пустое место для добавления еще одного урока (20% ширины, справа) -->
              <div 
                class="slot-empty-area" 
                @click.stop="openCreate(day.iso, hour)"
                :title="'Добавить урок на ' + formatHour(hour) + ' ' + day.display"
              ></div>
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
      <p v-if="activeLesson.parent_full_name"><strong>Родитель:</strong> {{ activeLesson.parent_full_name }}</p>
      <p><strong>Преподаватель:</strong> {{ activeLesson.teacher_email }}</p>
      <p>
        <strong>Баланс занятий:</strong> 
        <span :class="{'balance-zero': activeLesson.student_balance === 0, 'balance-positive': activeLesson.student_balance > 0}">
          {{ activeLesson.student_balance || 0 }}
        </span>
      </p>
      <p>
        <strong>Статус:</strong> 
        <span :class="['status-badge', `status-badge--${activeLesson.status?.toLowerCase() || 'planned'}`]">
          {{ activeLesson.status }}
        </span>
      </p>
      <p v-if="activeLesson.is_trial" class="trial-badge">
        <strong>Пробное занятие</strong>
      </p>
      <p><strong>Время:</strong> {{ formatDateTime(activeLesson.scheduled_at) }}</p>
      <p>
        <strong>Ссылка:</strong>
        <span v-if="activeLesson.link">
          <a :href="activeLesson.link" target="_blank">{{ activeLesson.link }}</a>
        </span>
        <span v-else>—</span>
      </p>
      <p><strong>Комментарий:</strong> {{ activeLesson.comment || '—' }}</p>
      <div v-if="canEditLesson" class="lesson-actions">
        <button class="btn small" @click="openEditLesson">Редактировать</button>
      </div>
    </section>

    <!-- Модальное окно создания урока -->
    <div v-if="showCreateModal" class="modal-backdrop" @click="closeCreate">
      <div class="modal" @click.stop>
        <h2>Создать урок</h2>
        <form @submit.prevent="handleCreate">
          <!-- Поле для ученика (по email) -->
          <label class="field">
            <span>Email ученика *</span>
            <div class="email-input-wrapper">
              <input
                v-model="formStudentEmail"
                type="email"
                :list="`student-email-list-${isManager ? 'manager' : 'teacher'}`"
                placeholder="student@example.com"
                required
                @blur="validateStudentEmail"
                @input="handleStudentEmailInput"
                autocomplete="off"
              />
              <datalist :id="`student-email-list-${isManager ? 'manager' : 'teacher'}`">
                <option
                  v-for="student in studentAutocompleteList"
                  :key="student.id"
                  :value="student.email"
                >
                  {{ student.student_full_name || student.email }}
                </option>
              </datalist>
              <button
                type="button"
                class="btn-search"
                @click="searchStudent"
                :disabled="searchingStudent"
              >
                {{ searchingStudent ? '...' : 'Найти' }}
              </button>
            </div>
            <span v-if="foundStudent" class="found-user">
              ✓ Найден: {{ foundStudent.student_full_name || foundStudent.email }}
            </span>
            <span v-if="studentError" class="error-text">{{ studentError }}</span>
          </label>

          <!-- Поле для учителя (только для менеджера) -->
          <label v-if="isManager" class="field">
            <span>Email учителя *</span>
            <div class="email-input-wrapper">
              <input
                v-model="formTeacherEmail"
                type="email"
                list="teacher-email-list-manager"
                placeholder="teacher@example.com"
                required
                @blur="validateTeacherEmail"
                @input="handleTeacherEmailInput"
                autocomplete="off"
              />
              <datalist id="teacher-email-list-manager">
                <option
                  v-for="teacher in teacherAutocompleteList"
                  :key="teacher.id"
                  :value="teacher.email"
                >
                  {{ teacher.email }}
                </option>
              </datalist>
              <button
                type="button"
                class="btn-search"
                @click="searchTeacher"
                :disabled="searchingTeacher"
              >
                {{ searchingTeacher ? '...' : 'Найти' }}
              </button>
            </div>
            <span v-if="foundTeacher" class="found-user">
              ✓ Найден: {{ foundTeacher.email }}
            </span>
            <span v-if="teacherError" class="error-text">{{ teacherError }}</span>
          </label>

          <!-- Для учителя показываем информацию о текущем учителе -->
          <div v-if="isTeacher" class="field">
            <span>Учитель</span>
            <input :value="currentUserEmail" type="email" disabled />
          </div>

          <label class="field">
            <span>Дата *</span>
            <input v-model="formDate" type="date" required />
          </label>

          <label class="field">
            <span>Время *</span>
            <input v-model="formTime" type="time" required />
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
            <button type="submit" :disabled="createLoading || !canCreateLesson">
              {{ createLoading ? 'Создаём...' : 'Создать' }}
            </button>
            <button type="button" @click="closeCreate">Отмена</button>
          </div>

          <p v-if="createError" class="error">{{ createError }}</p>
        </form>
      </div>
    </div>

    <!-- Модальное окно редактирования урока -->
    <div v-if="showEditModal && activeLesson" class="modal-backdrop" @click="closeEdit">
      <div class="modal" @click.stop>
        <h2>Редактировать урок</h2>
        <form @submit.prevent="handleUpdate">
          <label class="field">
            <span>Статус</span>
            <select v-model="editForm.status">
              <option value="PLANNED">Запланировано</option>
              <option value="DONE">Проведено</option>
              <option value="CANCELLED">Отменено</option>
            </select>
          </label>

          <div v-if="canEditTime" class="field-row">
            <label class="field field--half">
              <span>Дата</span>
              <input v-model="editForm.date" type="date" />
            </label>

            <label class="field field--half">
              <span>Время</span>
              <input v-model="editForm.time" type="time" />
            </label>
          </div>

          <label class="field">
            <span>Ссылка</span>
            <input v-model="editForm.link" type="text" placeholder="https://..." />
          </label>

          <label class="field">
            <span>Комментарий</span>
            <textarea v-model="editForm.comment" rows="3" placeholder="Комментарий к уроку"></textarea>
          </label>

          <!-- Поле причины отмены (показывается только при статусе CANCELLED) -->
          <label v-if="editForm.status === 'CANCELLED'" class="field field--required">
            <span>Причина отмены <span class="required-mark">*</span></span>
            <textarea 
              v-model="editForm.cancellation_reason" 
              rows="4" 
              placeholder="Укажите причину отмены занятия"
              required
            ></textarea>
          </label>

          <!-- Поле обратной связи (показывается только при статусе DONE) -->
          <label v-if="editForm.status === 'DONE'" class="field field--required">
            <span>Обратная связь по уроку <span class="required-mark">*</span></span>
            <textarea 
              v-model="editForm.feedback" 
              rows="5" 
              placeholder="Опишите, что было на уроке, какие темы разобрали, что нужно повторить и т.д."
              required
            ></textarea>
          </label>

          <div class="modal-actions">
            <button type="submit" :disabled="updateLoading">
              {{ updateLoading ? 'Сохраняем...' : 'Сохранить' }}
            </button>
            <button type="button" @click="closeEdit">Отмена</button>
          </div>

          <p v-if="updateError" class="error">{{ updateError }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  lessons: {
    type: Array,
    default: () => []
  },
  lessonsLoading: {
    type: Boolean,
    default: false
  },
  lessonsError: {
    type: String,
    default: null
  },
  onCreateLesson: {
    type: Function,
    required: true
  },
  onUpdateLesson: {
    type: Function,
    default: null
  },
  onSearchUser: {
    type: Function,
    default: null
  },
  onGetAutocomplete: {
    type: Function,
    default: null
  },
  userRole: {
    type: String,
    default: 'manager' // 'manager' или 'teacher'
  },
  currentUserEmail: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['lesson-selected', 'week-changed'])

const auth = useAuthStore()

const isManager = computed(() => props.userRole === 'manager')
const isTeacher = computed(() => props.userRole === 'teacher')
const canEditTime = computed(() => isManager.value)
const canEditLesson = computed(() => props.onUpdateLesson !== null)

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

const activeLesson = ref(null)

const lessonsBySlot = computed(() => {
  const map = {}
  for (const L of props.lessons) {
    if (!L.scheduled_at) continue
    const dt = new Date(L.scheduled_at)
    const key = `${toISO(dt)}-${dt.getHours()}`
    if (!map[key]) map[key] = []
    map[key].push(L)
  }
  return map
})

const formatHour = (h) => `${String(h).padStart(2, '0')}:00`

const formatLessonTime = (scheduledAt) => {
  if (!scheduledAt) return ''
  const dt = new Date(scheduledAt)
  const startHour = dt.getHours()
  const startMin = dt.getMinutes()
  const endHour = (startHour + 1) % 24
  const startStr = `${String(startHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`
  const endStr = `${String(endHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`
  return `${startStr} - ${endStr}`
}

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
const formStudentEmail = ref('')
const formTeacherEmail = ref('')
const formLink = ref('')
const formComment = ref('')

const foundStudent = ref(null)
const foundTeacher = ref(null)
const searchingStudent = ref(false)
const searchingTeacher = ref(false)
const studentError = ref('')
const teacherError = ref('')

// Автодополнение
const studentAutocompleteList = ref([])
const teacherAutocompleteList = ref([])
const autocompleteLoading = ref(false)
let studentAutocompleteTimeout = null
let teacherAutocompleteTimeout = null

const createLoading = ref(false)
const createError = ref('')

const openCreate = (iso, hour) => {
  formDate.value = iso
  formTime.value = `${String(hour).padStart(2, '0')}:00`
  formStudentEmail.value = ''
  formTeacherEmail.value = ''
  formLink.value = ''
  formComment.value = ''
  foundStudent.value = null
  foundTeacher.value = null
  studentError.value = ''
  teacherError.value = ''
  createError.value = ''
  showCreateModal.value = true
  
  // Загружаем начальные списки для автодополнения
  if (props.onGetAutocomplete) {
    loadStudentAutocomplete('')
    if (isManager.value) {
      loadTeacherAutocomplete('')
    }
  }
}

const closeCreate = () => {
  showCreateModal.value = false
}

const searchStudent = async () => {
  if (!formStudentEmail.value || !props.onSearchUser) return
  
  searchingStudent.value = true
  studentError.value = ''
  foundStudent.value = null

  try {
    const result = await props.onSearchUser(formStudentEmail.value, 'student')
    if (result && result.is_my_student !== false) {
      foundStudent.value = result
    } else {
      studentError.value = 'Этот ученик не назначен вам. Обратитесь к менеджеру.'
    }
  } catch (err) {
    console.error('search student error:', err)
    const errorDetail = err?.response?.data?.detail
    if (errorDetail === 'this student is not assigned to you') {
      studentError.value = 'Этот ученик не назначен вам. Обратитесь к менеджеру.'
    } else {
      studentError.value = errorDetail || 'Ученик не найден'
    }
  } finally {
    searchingStudent.value = false
  }
}

const searchTeacher = async () => {
  if (!formTeacherEmail.value || !props.onSearchUser) return
  
  searchingTeacher.value = true
  teacherError.value = ''
  foundTeacher.value = null

  try {
    const result = await props.onSearchUser(formTeacherEmail.value, 'teacher')
    foundTeacher.value = result
  } catch (err) {
    console.error('search teacher error:', err)
    teacherError.value = err?.response?.data?.detail || 'Учитель не найден'
  } finally {
    searchingTeacher.value = false
  }
}

const validateStudentEmail = () => {
  if (formStudentEmail.value && props.onSearchUser) {
    searchStudent()
  }
}

const validateTeacherEmail = () => {
  if (formTeacherEmail.value && props.onSearchUser) {
    searchTeacher()
  }
}

const clearStudentError = () => {
  studentError.value = ''
  foundStudent.value = null
}

const clearTeacherError = () => {
  teacherError.value = ''
  foundTeacher.value = null
}

// Загрузка списков для автодополнения
const loadStudentAutocomplete = async (search = '') => {
  if (!props.onGetAutocomplete) return
  
  try {
    autocompleteLoading.value = true
    const result = await props.onGetAutocomplete('student', search)
    studentAutocompleteList.value = Array.isArray(result) ? result : result.data || []
  } catch (err) {
    console.error('load student autocomplete error:', err)
    studentAutocompleteList.value = []
  } finally {
    autocompleteLoading.value = false
  }
}

const loadTeacherAutocomplete = async (search = '') => {
  if (!props.onGetAutocomplete || !isManager.value) return
  
  try {
    autocompleteLoading.value = true
    const result = await props.onGetAutocomplete('teacher', search)
    teacherAutocompleteList.value = Array.isArray(result) ? result : result.data || []
  } catch (err) {
    console.error('load teacher autocomplete error:', err)
    teacherAutocompleteList.value = []
  } finally {
    autocompleteLoading.value = false
  }
}

// Обработка ввода для автодополнения (с debounce)
const handleStudentEmailInput = (event) => {
  const value = event.target.value.trim()
  clearStudentError()
  
  // Очищаем предыдущий таймер
  if (studentAutocompleteTimeout) {
    clearTimeout(studentAutocompleteTimeout)
  }
  
  // Загружаем подсказки при вводе (с задержкой 300ms)
  if (value.length >= 2) {
    studentAutocompleteTimeout = setTimeout(() => {
      loadStudentAutocomplete(value)
    }, 300)
  } else {
    studentAutocompleteList.value = []
  }
}

const handleTeacherEmailInput = (event) => {
  const value = event.target.value.trim()
  clearTeacherError()
  
  // Очищаем предыдущий таймер
  if (teacherAutocompleteTimeout) {
    clearTimeout(teacherAutocompleteTimeout)
  }
  
  // Загружаем подсказки при вводе (с задержкой 300ms)
  if (value.length >= 2) {
    teacherAutocompleteTimeout = setTimeout(() => {
      loadTeacherAutocomplete(value)
    }, 300)
  } else {
    teacherAutocompleteList.value = []
  }
}

const canCreateLesson = computed(() => {
  if (isManager.value) {
    return foundStudent.value && foundTeacher.value
  } else if (isTeacher.value) {
    return foundStudent.value
  }
  return false
})

const handleCreate = async () => {
  createError.value = ''

  // Проверяем, что найдены необходимые пользователи
  if (!foundStudent.value) {
    createError.value = 'Сначала найдите ученика по email'
    return
  }

  if (isManager.value && !foundTeacher.value) {
    createError.value = 'Сначала найдите учителя по email'
    return
  }

  // Формируем правильный формат даты и времени (ISO 8601 с секундами и часовым поясом)
  // formTime может быть в формате "HH:MM" или "HH:MM:SS", добавляем секунды если нужно
  let timeStr = formTime.value
  if (timeStr && timeStr.split(':').length === 2) {
    timeStr = `${timeStr}:00` // Добавляем секунды если их нет
  }
  
  // Создаем объект Date с локальной датой и временем
  const localDateTime = new Date(`${formDate.value}T${timeStr}`)
  
  // Получаем смещение часового пояса в формате +HH:MM или -HH:MM
  const timezoneOffset = -localDateTime.getTimezoneOffset()
  const offsetHours = Math.floor(Math.abs(timezoneOffset) / 60)
  const offsetMinutes = Math.abs(timezoneOffset) % 60
  const offsetSign = timezoneOffset >= 0 ? '+' : '-'
  const offsetStr = `${offsetSign}${String(offsetHours).padStart(2, '0')}:${String(offsetMinutes).padStart(2, '0')}`
  
  // Формируем ISO строку с часовым поясом
  const isoString = `${formDate.value}T${timeStr}${offsetStr}`
  
  const payload = {
    student_email: formStudentEmail.value.trim(),
    scheduled_at: isoString,
  }

  // Добавляем comment только если он не пустой
  if (formComment.value?.trim()) {
    payload.comment = formComment.value.trim()
  } else {
    payload.comment = ''
  }

  // Добавляем link только если он не пустой
  if (formLink.value?.trim()) {
    payload.link = formLink.value.trim()
  }

  // Для менеджера добавляем teacher_email
  if (isManager.value) {
    payload.teacher_email = formTeacherEmail.value.trim()
  }

  console.log('Creating lesson with payload:', payload)

  createLoading.value = true

  try {
    await props.onCreateLesson(payload)
    showCreateModal.value = false
    // Очищаем форму после успешного создания
    formStudentEmail.value = ''
    formTeacherEmail.value = ''
    formLink.value = ''
    formComment.value = ''
    foundStudent.value = null
    foundTeacher.value = null
  } catch (err) {
    console.error('create lesson error:', err)
    console.error('Error response data:', err?.response?.data)
    const errorData = err?.response?.data
    if (errorData) {
      if (errorData.student_email) {
        createError.value = `Ошибка с учеником: ${Array.isArray(errorData.student_email) ? errorData.student_email[0] : errorData.student_email}`
      } else if (errorData.teacher_email) {
        createError.value = `Ошибка с учителем: ${Array.isArray(errorData.teacher_email) ? errorData.teacher_email[0] : errorData.teacher_email}`
      } else if (errorData.student) {
        createError.value = `Ошибка с учеником: ${Array.isArray(errorData.student) ? errorData.student[0] : errorData.student}`
      } else if (errorData.teacher) {
        createError.value = `Ошибка с учителем: ${Array.isArray(errorData.teacher) ? errorData.teacher[0] : errorData.teacher}`
      } else if (errorData.detail) {
        createError.value = errorData.detail
      } else {
        // Показываем первую ошибку из объекта
        const firstErrorKey = Object.keys(errorData)[0]
        const firstError = errorData[firstErrorKey]
        createError.value = `${firstErrorKey}: ${Array.isArray(firstError) ? firstError[0] : firstError}`
      }
    } else {
      createError.value = 'Ошибка создания урока. Проверьте подключение к серверу.'
    }
  }

  createLoading.value = false
}

const selectLesson = (lesson) => {
  activeLesson.value = lesson
  emit('lesson-selected', lesson)
}

// =====================================
// РЕДАКТИРОВАНИЕ УРОКА
// =====================================

const showEditModal = ref(false)

const editForm = ref({
  status: '',
  date: '',
  time: '',
  link: '',
  comment: '',
  cancellation_reason: '',
  feedback: ''
})

const updateLoading = ref(false)
const updateError = ref(null)

const openEditLesson = () => {
  if (!activeLesson.value) return
  
  const lesson = activeLesson.value
  const scheduledDate = new Date(lesson.scheduled_at)
  
  editForm.value = {
    status: lesson.status,
    date: toISO(scheduledDate),
    time: `${String(scheduledDate.getHours()).padStart(2, '0')}:${String(scheduledDate.getMinutes()).padStart(2, '0')}`,
    link: lesson.link || '',
    comment: lesson.comment || '',
    cancellation_reason: lesson.cancellation_reason || '',
    feedback: lesson.feedback || '',
  }
  updateError.value = null
  showEditModal.value = true
}

const closeEdit = () => {
  showEditModal.value = false
}

const handleUpdate = async () => {
  if (!activeLesson.value || !props.onUpdateLesson) return

  updateLoading.value = true
  updateError.value = null

  // Валидация на фронтенде
  if (editForm.value.status === 'CANCELLED' && !editForm.value.cancellation_reason?.trim()) {
    updateError.value = 'Причина отмены обязательна при отмене занятия'
    updateLoading.value = false
    return
  }

  if (editForm.value.status === 'DONE' && !editForm.value.feedback?.trim()) {
    updateError.value = 'Обратная связь обязательна при завершении занятия'
    updateLoading.value = false
    return
  }

  try {
    const payload = {
      status: editForm.value.status,
      link: editForm.value.link || null,
      comment: editForm.value.comment || '',
    }

    // Всегда передаем cancellation_reason и feedback, если они есть в форме
    // Это позволяет обновлять их значения независимо от статуса
    // Важно: передаем даже пустые строки, чтобы можно было очистить поля
    if ('cancellation_reason' in editForm.value) {
      payload.cancellation_reason = editForm.value.cancellation_reason || ''
    }
    
    if ('feedback' in editForm.value) {
      payload.feedback = editForm.value.feedback || ''
    }

    if (canEditTime.value && editForm.value.date && editForm.value.time) {
      // Формируем правильный формат даты и времени (ISO 8601 с секундами и часовым поясом)
      let timeStr = editForm.value.time
      if (timeStr && timeStr.split(':').length === 2) {
        timeStr = `${timeStr}:00` // Добавляем секунды если их нет
      }
      
      // Создаем объект Date с локальной датой и временем
      const localDateTime = new Date(`${editForm.value.date}T${timeStr}`)
      
      // Получаем смещение часового пояса в формате +HH:MM или -HH:MM
      const timezoneOffset = -localDateTime.getTimezoneOffset()
      const offsetHours = Math.floor(Math.abs(timezoneOffset) / 60)
      const offsetMinutes = Math.abs(timezoneOffset) % 60
      const offsetSign = timezoneOffset >= 0 ? '+' : '-'
      const offsetStr = `${offsetSign}${String(offsetHours).padStart(2, '0')}:${String(offsetMinutes).padStart(2, '0')}`
      
      // Формируем ISO строку с часовым поясом
      payload.scheduled_at = `${editForm.value.date}T${timeStr}${offsetStr}`
    }

    console.log('Updating lesson with payload:', payload)
    const updatedLesson = await props.onUpdateLesson(activeLesson.value.id, payload)
    
    // Обновляем activeLesson с новыми данными
    if (updatedLesson) {
      activeLesson.value = updatedLesson
    } else {
      // Если обновленный урок не возвращен, обновляем из списка уроков
      const lessonId = activeLesson.value.id
      const refreshedLesson = props.lessons.find(l => l.id === lessonId)
      if (refreshedLesson) {
        activeLesson.value = refreshedLesson
      }
    }
    
    showEditModal.value = false
  } catch (err) {
    console.error('update lesson error:', err)
    console.error('error response:', err?.response?.data)
    const errorData = err?.response?.data
    if (errorData) {
      // Обрабатываем ошибки валидации
      if (errorData.cancellation_reason) {
        updateError.value = Array.isArray(errorData.cancellation_reason) 
          ? errorData.cancellation_reason[0] 
          : errorData.cancellation_reason
      } else if (errorData.feedback) {
        updateError.value = Array.isArray(errorData.feedback) 
          ? errorData.feedback[0] 
          : errorData.feedback
      } else if (errorData.detail) {
        updateError.value = errorData.detail
      } else {
        // Показываем первую ошибку из объекта или общее сообщение
        const errorKeys = Object.keys(errorData)
        if (errorKeys.length > 0) {
          const firstError = errorData[errorKeys[0]]
          updateError.value = `${errorKeys[0]}: ${Array.isArray(firstError) ? firstError[0] : firstError}`
        } else {
          updateError.value = 'Ошибка обновления урока'
        }
      }
    } else {
      updateError.value = 'Ошибка обновления урока'
    }
  } finally {
    updateLoading.value = false
  }
}

// =====================================
// НАВИГАЦИЯ НЕДЕЛИ
// =====================================

const shiftWeek = (delta) => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + delta * 7)
  currentDate.value = d
  emit('week-changed', {
    date_from: toISO(weekStart.value),
    date_to: toISO(addDays(weekStart.value, 6))
  })
}

const goToday = () => {
  currentDate.value = new Date()
  emit('week-changed', {
    date_from: toISO(weekStart.value),
    date_to: toISO(addDays(weekStart.value, 6))
  })
}

// Экспортируем функции для внешнего использования
defineExpose({
  weekStart,
  weekEnd: computed(() => addDays(weekStart.value, 6)),
  shiftWeek,
  goToday
})
</script>

<style scoped>
.schedule-view {
  display: grid;
  grid-template-columns: 1fr 160px;
  gap: 6px;
  width: 100%;
  max-width: 100%;
}

.admin-card {
  background: #202124;
  padding: 10px;
  border-radius: 0;
  border: none;
}

.calendar-card {
  min-width: 0;
  overflow: hidden;
  width: 100%;
}

.controls-card {
  grid-column: 1 / -1;
  background: #202124;
  border-bottom: 1px solid #3c4043;
  padding: 16px 24px;
}

.calendar-card {
  grid-column: 1 / 2;
}

.lesson-info-card {
  grid-column: 2 / 3;
  max-width: 160px;
  min-width: 0;
}

.controls-row button {
  margin-right: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #5f6368;
  border-radius: 4px;
  cursor: pointer;
  color: #e8eaed;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s, border-color 0.2s;
}

.controls-row button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #8ab4f8;
}

.week-label {
  margin: 12px 0;
  color: #aaa;
}

.hint {
  color: #9aa0a6;
  font-size: 12px;
  margin-top: 8px;
}

.calendar {
  border: none;
  border-radius: 0;
  overflow: hidden;
  font-size: 13px;
  width: 100%;
  min-width: 0;
  background: #1a1a1a;
}

.calendar-header-row,
.calendar-row {
  display: grid;
  grid-template-columns: 45px repeat(7, 1fr);
  width: 100%;
}

.time-col {
  background: #101010;
  text-align: right;
  padding-right: 4px;
  padding-left: 2px;
  color: #aaa;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.day-col {
  background: transparent;
  text-align: center;
  border-right: 1px solid #3c4043;
  padding: 8px 4px;
  min-width: 0;
  border-bottom: 1px solid #3c4043;
}

.day-name {
  font-weight: 500;
  color: #9aa0a6;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.day-date {
  font-size: 22px;
  color: #e8eaed;
  margin-top: 4px;
  font-weight: 400;
  line-height: 1.2;
}

.calendar-body {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  background: #1a1a1a;
}

.calendar-body::-webkit-scrollbar {
  width: 8px;
}

.calendar-body::-webkit-scrollbar-track {
  background: #202124;
}

.calendar-body::-webkit-scrollbar-thumb {
  background: #5f6368;
  border-radius: 4px;
}

.calendar-body::-webkit-scrollbar-thumb:hover {
  background: #80868b;
}

.calendar-row {
  height: 80px;
}

.slot {
  position: relative;
  height: 80px;
  border-right: 1px solid #3c4043;
  border-bottom: 1px solid #3c4043;
  padding: 1px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 1px;
  overflow: hidden;
  box-sizing: border-box;
  background: transparent;
}

.slot-lessons-container {
  flex: 0 0 80%;
  max-width: 80%;
  display: flex;
  flex-direction: row;
  gap: 3px;
  overflow: hidden;
  align-items: flex-start;
  min-width: 0;
}

.slot:hover {
  background: rgba(255, 255, 255, 0.03);
}

.slot-empty-area {
  flex: 0 0 20%;
  min-width: 30px;
  height: calc(100% - 2px);
  cursor: pointer;
  transition: all 0.15s;
  border-radius: 2px;
  align-self: stretch;
  margin-top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed rgba(154, 160, 166, 0.3);
  background: transparent;
}

.slot-empty-area:hover {
  background-color: rgba(138, 180, 248, 0.1);
  border-color: rgba(138, 180, 248, 0.5);
}

.slot-empty-area::before {
  content: '+';
  font-size: 18px;
  color: rgba(154, 160, 166, 0.6);
  font-weight: 300;
  line-height: 1;
}

.slot-empty-area:hover::before {
  color: #8ab4f8;
}

.lesson-card {
  color: #202124;
  border-radius: 3px;
  padding: 4px 6px;
  margin: 0;
  font-size: 12px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
  flex: 0 0 auto;
  min-width: 100px;
  max-width: 180px;
  height: auto;
  min-height: 20px;
  max-height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
  border-left: 3px solid transparent;
}

.lesson-card:hover {
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
  transform: translateY(-1px);
  z-index: 10;
  position: relative;
}

/* Запланировано - синий */
.lesson-card--planned {
  background: #4a90e2;
}

/* Проведено - зеленый (не яркий) */
.lesson-card--done {
  background: #66bb6a;
}

/* Отменено - светло-красный (не яркий) */
.lesson-card--cancelled {
  background: #e57373;
}

.lesson-time {
  font-weight: 500;
  font-size: 11px;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
  color: #202124;
}

.lesson-student {
  font-size: 11px;
  opacity: 0.9;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #5f6368;
}

.lesson-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #333;
}

.btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  background: #1e88e5;
  color: white;
  font-size: 13px;
}

.btn.small {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:hover:not(:disabled) {
  background: #1565c0;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 500px;
  background: #111;
  border: 1px solid #333;
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
  font-weight: 600;
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
  font-weight: 500;
}

.email-input-wrapper {
  display: flex;
  gap: 8px;
}

.email-input-wrapper input {
  flex: 1;
}

.btn-search {
  padding: 8px 12px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-search:hover:not(:disabled) {
  background: #35a372;
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.found-user {
  color: #4caf50;
  font-size: 0.85rem;
  margin-top: 4px;
}

.error-text {
  color: #ff6b6b;
  font-size: 0.85rem;
  margin-top: 4px;
}

.field input,
.field select,
.field textarea {
  background: #1a1a1a;
  border: 1px solid #444;
  color: white;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.field textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.field-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.field--half {
  flex: 1;
  margin-bottom: 0;
}

.field--required span {
  color: #fff;
}

.required-mark {
  color: #ff6b6b;
  margin-left: 2px;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: #1e88e5;
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
}

.field input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #333;
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

.error {
  color: #ff6b6b;
  margin-top: 8px;
  font-size: 0.9rem;
}

.status-text {
  font-size: 13px;
  color: #aaa;
  margin-top: 8px;
}

.lesson-info-card h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #fff;
}

.lesson-info-card p {
  margin: 8px 0;
  color: #ccc;
}

.lesson-info-card a {
  color: #1e88e5;
  text-decoration: none;
}

.lesson-info-card a:hover {
  text-decoration: underline;
}

.balance-zero {
  color: #ea4335;
  font-weight: 600;
}

.balance-positive {
  color: #34a853;
  font-weight: 500;
}

.trial-badge {
  background: rgba(251, 188, 4, 0.15);
  padding: 6px 10px;
  border-radius: 4px;
  border-left: 3px solid #fbbc04;
  margin: 8px 0;
}

.trial-badge strong {
  color: #fbbc04;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 8px;
}

/* Запланировано - синий */
.status-badge--planned {
  background: #4a90e2;
  color: white;
}

/* Проведено - зеленый (не яркий) */
.status-badge--done {
  background: #66bb6a;
  color: white;
}

/* Отменено - светло-красный (не яркий) */
.status-badge--cancelled {
  background: #e57373;
  color: white;
}
</style>
