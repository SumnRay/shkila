<!-- src/components/ManagerRequestForm.vue -->
<template>
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Обратиться к менеджеру</h2>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="request-form">
        <div class="form-group">
          <label for="comment">Комментарий (необязательно)</label>
          <textarea
            id="comment"
            v-model="comment"
            rows="5"
            placeholder="Опишите ваш вопрос или проблему..."
            class="form-textarea"
          ></textarea>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="closeModal">
            Отмена
          </button>
          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? 'Отправка...' : 'Отправить запрос' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  onSubmit: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['close', 'success'])

const showModal = ref(props.show)
const comment = ref('')
const submitting = ref(false)
const error = ref(null)

watch(() => props.show, (newVal) => {
  showModal.value = newVal
  if (!newVal) {
    comment.value = ''
    error.value = null
  }
})

const closeModal = () => {
  showModal.value = false
  emit('close')
}

const handleSubmit = async () => {
  error.value = null
  submitting.value = true
  
  try {
    await props.onSubmit({ comment: comment.value })
    closeModal()
    emit('success')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Ошибка при отправке запроса'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: rgba(76, 68, 118, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #ffffff;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.close-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  line-height: 1;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.request-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.error-message {
  padding: 12px;
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.4);
  border-radius: 8px;
  color: #ffb3b3;
  margin-bottom: 20px;
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-submit {
  background: rgba(102, 126, 234, 0.9);
  color: #ffffff;
  border: 1px solid rgba(102, 126, 234, 0.6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-submit:hover:not(:disabled) {
  background: rgba(102, 126, 234, 1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
