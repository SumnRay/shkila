<!-- src/pages/common/PaymentCalculatorView.vue -->
<template>
  <div class="payment-page">
    <!-- Верхняя навигация -->
    <nav class="top-nav-bar">
      <div class="nav-left">
        <router-link :to="{ name: 'home' }" class="nav-link">На главную</router-link>
        <router-link v-if="auth.isAuthenticated" :to="dashboardRoute" class="nav-link">Личный кабинет</router-link>
      </div>
      <div class="nav-right">
        <button v-if="auth.isAuthenticated" class="logout-btn" @click="handleLogout">Выход</button>
        <router-link v-else :to="{ name: 'login' }" class="nav-link">Войти</router-link>
      </div>
    </nav>

    <div class="payment-content">
      <h1 class="page-title">Оплата занятий</h1>

      <div class="cards-grid">
        <!-- Карточка с ценой -->
        <div class="card price-card">
          <h2 class="card-title">Стоимость</h2>
          <div class="price-block">
            <div class="price-value">800 ₽</div>
            <div class="price-label">за 1 урок</div>
          </div>
        </div>

        <!-- Карточка с реквизитами -->
        <div class="card payment-card">
          <h2 class="card-title">Реквизиты для оплаты</h2>
          <div class="payment-info">
            <div class="payment-row">
              <span class="payment-label">Способ оплаты:</span>
              <span class="payment-value">СБП (Система быстрых платежей)</span>
            </div>
            <div class="payment-row">
              <span class="payment-label">Банк:</span>
              <span class="payment-value">ВТБ</span>
            </div>
            <div class="payment-row">
              <span class="payment-label">Номер телефона:</span>
              <span class="payment-value phone-number">+7 978 474 13 26</span>
            </div>
            <div class="payment-row">
              <span class="payment-label">Получатель:</span>
              <span class="payment-value">Семененко Никита Сергеевич</span>
            </div>
          </div>
        </div>

        <!-- Информационная карточка -->
        <div class="card info-card">
          <h2 class="card-title">Важная информация</h2>
          <div class="info-block warning">
            <div class="info-icon">⚠️</div>
            <div class="info-text">
              На данный момент на платформе нет менеджеров. Чек об оплате необходимо отправлять лично преподавателю, по совместительству менеджеру и администратору.
            </div>
          </div>
        </div>

        <!-- Карточка с контактами -->
        <div class="card contact-card">
          <h2 class="card-title">Отправка чека</h2>
          <p class="contact-description">
            После оплаты отправьте скриншот или фото чека преподавателю для подтверждения и начисления занятий на ваш баланс.
          </p>
          <div class="contact-info">
            <div class="contact-row">
              <span class="contact-label">Telegram:</span>
              <a href="https://t.me/nikiticko" target="_blank" class="contact-link">@nikiticko</a>
            </div>
            <div class="contact-row">
              <span class="contact-label">Телефон:</span>
              <span class="contact-value">+7 978 474 13 26</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Инструкция -->
      <div class="card instructions-card">
        <h2 class="card-title">Как оплатить</h2>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-text">Откройте приложение вашего банка и выберите оплату по СБП</div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-text">Введите номер телефона <strong>+7 978 474 13 26</strong> и выберите банк <strong>ВТБ</strong></div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-text">Укажите сумму (800₽ × количество уроков) и выполните перевод</div>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <div class="step-text">Отправьте скриншот чека в Telegram <strong>@nikiticko</strong></div>
          </div>
          <div class="step">
            <div class="step-number">5</div>
            <div class="step-text">После подтверждения занятия будут начислены на ваш баланс</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const dashboardRoute = computed(() => {
  if (!auth.user) return { name: 'login' }
  const role = auth.user.role
  if (role === 'STUDENT') return { name: 'student-dashboard' }
  if (role === 'APPLICANT') return { name: 'applicant-dashboard' }
  if (role === 'TEACHER') return { name: 'teacher-dashboard' }
  if (role === 'MANAGER') return { name: 'manager-dashboard' }
  if (role === 'ADMIN') return { name: 'admin-dashboard' }
  return { name: 'home' }
})

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<style scoped>
.payment-page {
  min-height: 100vh;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding-bottom: 60px;
}

/* Верхняя навигация */
.top-nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 215, 0, 0.3);
  padding: 12px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-left {
  display: flex;
  gap: 24px;
  align-items: center;
}

.nav-link {
  color: #FFFFFF;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 4px 0;
}

.nav-link:hover {
  color: #FFD700;
  transform: translateY(-1px);
}

.logout-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFFFFF;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.logout-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

/* Контент */
.payment-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  color: #FFFFFF;
  text-align: center;
  margin: 0 0 32px 0;
}

/* Сетка карточек */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

/* Карточки */
.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
}

.card-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

/* Карточка с ценой */
.price-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.price-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.price-value {
  font-size: 3.5rem;
  font-weight: 900;
  color: #FFD700;
  text-shadow: 0 4px 20px rgba(255, 215, 0, 0.4);
}

.price-label {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

/* Карточка с реквизитами */
.payment-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.payment-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.payment-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.payment-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #FFFFFF;
}

.phone-number {
  font-size: 1.3rem;
  color: #FFD700;
  font-weight: 700;
}

/* Информационная карточка */
.info-block {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
  border-radius: 8px;
}

.info-block.warning {
  background: rgba(255, 193, 7, 0.15);
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-text {
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
}

/* Карточка с контактами */
.contact-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
}

.contact-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contact-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.contact-value {
  font-size: 1rem;
  font-weight: 600;
  color: #FFFFFF;
}

.contact-link {
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFD700;
  text-decoration: none;
  transition: all 0.3s ease;
}

.contact-link:hover {
  color: #FF8C00;
  text-decoration: underline;
}

/* Карточка с инструкцией */
.instructions-card {
  grid-column: 1 / -1;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.step-number {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: rgba(255, 215, 0, 0.2);
  border: 2px solid #FFD700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  color: #FFD700;
}

.step-text {
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  padding-top: 6px;
}

.step-text strong {
  color: #FFD700;
}

/* Адаптивность */
@media (max-width: 768px) {
  .payment-content {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 1.8rem;
    margin-bottom: 24px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .card {
    padding: 20px;
  }

  .card-title {
    font-size: 1.1rem;
    margin-bottom: 16px;
  }

  .price-value {
    font-size: 2.5rem;
  }

  .price-label {
    font-size: 1rem;
  }

  .top-nav-bar {
    padding: 10px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .nav-left {
    gap: 16px;
  }

  .nav-link {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .payment-content {
    padding: 16px 12px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .card {
    padding: 16px;
  }

  .price-value {
    font-size: 2rem;
  }

  .step {
    gap: 12px;
  }

  .step-number {
    width: 30px;
    height: 30px;
    font-size: 0.9rem;
  }

  .step-text {
    font-size: 0.9rem;
  }
}
</style>
