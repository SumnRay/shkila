<!-- src/pages/common/PaymentCalculatorView.vue -->
<template>
  <div class="payment-calculator">
    <TopNavigationBar />

    <div class="calculator-content">
      <div class="page-header">
        <h1 class="page-title">💳 Оплата занятий</h1>
        <p class="page-subtitle">Выберите пакет занятий и следуйте инструкциям</p>
      </div>

      <div class="main-layout">
        <!-- Левая колонка - Калькулятор -->
        <div class="calculator-section">
          <div class="card calculator-card">
            <div class="card-title">
              <span>🧮</span>
              <h3>Калькулятор стоимости</h3>
            </div>
            <div class="calculator-form">
              <div class="form-group">
                <label class="form-label">Выберите пакет занятий</label>
                <div class="packages-grid">
                  <button
                    v-for="pkg in packages"
                    :key="pkg.id"
                    @click="selectPackage(pkg)"
                    :class="['package-btn', { active: selectedPackage?.id === pkg.id }]"
                  >
                    <div class="package-lessons">{{ pkg.lessons }}</div>
                    <div class="package-label">занятий</div>
                    <div class="package-price">{{ formatPrice(pkg.price) }} ₽</div>
                  </button>
                </div>
              </div>
              <div v-if="selectedPackage" class="calculation-result">
                <div class="result-item">
                  <span class="result-label">Количество занятий:</span>
                  <span class="result-value">{{ selectedPackage.lessons }}</span>
                </div>
                <div class="result-item">
                  <span class="result-label">Стоимость за занятие:</span>
                  <span class="result-value">{{ formatPrice(selectedPackage.pricePerLesson) }} ₽</span>
                </div>
                <div class="result-item total">
                  <span class="result-label">Итого к оплате:</span>
                  <span class="result-value">{{ formatPrice(selectedPackage.price) }} ₽</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Правая колонка - Инструкции -->
        <div class="instructions-section">
          <div class="card instructions-card">
            <div class="card-title">
              <span>📋</span>
              <h3>Инструкция по оплате</h3>
            </div>
            <div class="instructions-content">
              <div class="instruction-step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h4>Выберите пакет занятий</h4>
                  <p>Выберите подходящий пакет занятий в калькуляторе слева</p>
                </div>
              </div>
              <div class="instruction-step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h4>Оплатите через СБП</h4>
                  <p>Переведите сумму на наш номер телефона через систему быстрых платежей (СБП)</p>
                  <div class="payment-details">
                    <div class="payment-item">
                      <span class="payment-label">Номер телефона:</span>
                      <span class="payment-value">{{ paymentPhone }}</span>
                    </div>
                    <div class="payment-item">
                      <span class="payment-label">Сумма к оплате:</span>
                      <span class="payment-value" v-if="selectedPackage">{{ formatPrice(selectedPackage.price) }} ₽</span>
                      <span class="payment-value" v-else>—</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="instruction-step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <h4>Отправьте чек менеджеру</h4>
                  <p>После оплаты обязательно отправьте скриншот или фото чека менеджеру для подтверждения оплаты и начисления занятий на ваш баланс</p>
                  <div class="contact-info">
                    <p><strong>Способы связи с менеджером:</strong></p>
                    <ul>
                      <li>Email: {{ managerEmail }}</li>
                      <li>Телефон: {{ managerPhone }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="instruction-step">
                <div class="step-number">4</div>
                <div class="step-content">
                  <h4>Получите занятия на баланс</h4>
                  <p>После подтверждения оплаты менеджером занятия будут начислены на ваш баланс в личном кабинете</p>
                </div>
              </div>
            </div>
            <div class="important-note">
              <div class="note-icon">⚠️</div>
              <div class="note-text">
                <strong>Важно:</strong> Занятия будут начислены только после подтверждения оплаты менеджером. 
                Пожалуйста, сохраните чек об оплате до получения подтверждения.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import TopNavigationBar from '../../components/TopNavigationBar.vue'

const auth = useAuthStore()

// Пакеты занятий (можно будет получать с бэкенда в будущем)
const packages = ref([
  { id: 1, lessons: 4, price: 4000, pricePerLesson: 1000 },
  { id: 2, lessons: 8, price: 7200, pricePerLesson: 900 },
  { id: 3, lessons: 12, price: 10200, pricePerLesson: 850 },
  { id: 4, lessons: 16, price: 12800, pricePerLesson: 800 },
  { id: 5, lessons: 20, price: 15000, pricePerLesson: 750 },
])

const selectedPackage = ref(null)

// Реквизиты для оплаты (можно вынести в конфиг или получать с бэкенда)
const paymentPhone = ref('+7 (999) 123-45-67')
const managerEmail = ref('manager@school.ru')
const managerPhone = ref('+7 (999) 123-45-68')

const selectPackage = (packageOption) => {
  selectedPackage.value = packageOption
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}
</script>

<style scoped>
.payment-calculator {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  position: relative;
}

.payment-calculator::before {
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

.calculator-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  position: relative;
  z-index: 1;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.page-header {
  text-align: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 4px 0;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.main-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: start;
  flex: 1;
  overflow: hidden;
}

.card {
  background: rgba(76, 68, 118, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  background: rgba(76, 68, 118, 0.95);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.6);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.card-title span {
  font-size: 1.2rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.card-title h3 {
  margin: 0;
  font-size: 1rem;
  color: #ffffff;
  flex: 1;
  font-weight: 800;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Калькулятор */
.calculator-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow-y: auto;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 6px;
}

.package-btn {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 8px 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;
}

.package-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.package-btn.active {
  background: rgba(102, 126, 234, 0.6);
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.package-lessons {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.package-label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.package-price {
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin-top: 2px;
}

.calculation-result {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.result-item:last-child {
  border-bottom: none;
}

.result-item.total {
  margin-top: 4px;
  padding-top: 8px;
  border-top: 2px solid rgba(255, 255, 255, 0.3);
  border-bottom: none;
}

.result-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.85);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.result-item.total .result-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #ffffff;
}

.result-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.result-item.total .result-value {
  font-size: 1.2rem;
  font-weight: 800;
  color: #ffffff;
}

/* Инструкции */
.instructions-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  overflow-y: auto;
}

.instruction-step {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.step-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: rgba(102, 126, 234, 0.6);
  border: 2px solid rgba(102, 126, 234, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 4px 0;
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.step-content p {
  margin: 0 0 6px 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.4;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.payment-details {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px;
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.payment-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.payment-value {
  font-size: 0.8rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.contact-info {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px;
  margin-top: 6px;
}

.contact-info p {
  margin: 0 0 4px 0;
  font-weight: 600;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.95);
}

.contact-info ul {
  margin: 0;
  padding-left: 16px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.7rem;
}

.contact-info li {
  margin: 2px 0;
  line-height: 1.4;
}

.important-note {
  margin-top: 10px;
  padding: 8px;
  background: rgba(255, 193, 7, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 193, 7, 0.4);
  border-radius: 8px;
  border-left: 3px solid rgba(255, 193, 7, 0.6);
  display: flex;
  gap: 6px;
  align-items: flex-start;
  flex-shrink: 0;
}

.note-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.note-text {
  flex: 1;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.4;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.note-text strong {
  color: #ffffff;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .calculator-content {
    height: calc(100vh - 60px);
  }
}

@media (max-width: 768px) {
  .calculator-content {
    padding: 12px;
    height: calc(100vh - 60px);
  }

  .page-header {
    margin-bottom: 12px;
  }

  .page-title {
    font-size: 1.25rem;
  }

  .page-subtitle {
    font-size: 0.75rem;
  }

  .main-layout {
    gap: 10px;
  }

  .card {
    padding: 10px;
  }

  .card-title {
    margin-bottom: 8px;
    padding-bottom: 6px;
  }

  .card-title h3 {
    font-size: 0.9rem;
  }

  .packages-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }

  .package-btn {
    padding: 6px 4px;
  }

  .instruction-step {
    flex-direction: row;
    gap: 6px;
  }

  .step-number {
    width: 24px;
    height: 24px;
    font-size: 0.75rem;
  }
}
</style>

