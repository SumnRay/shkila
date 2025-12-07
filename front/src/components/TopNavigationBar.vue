<!-- src/components/TopNavigationBar.vue -->
<template>
  <header class="top-navigation-bar">
    <!-- Левая часть - Название школы -->
    <div class="nav-left">
      <router-link :to="{ name: 'home' }" class="school-logo">
        <span class="logo-icon">🎓</span>
        <span class="logo-text">Онлайн Школа</span>
      </router-link>
    </div>

    <!-- Правая часть -->
    <div class="nav-right">
      <!-- Кнопка администрирования (для admin, manager и teacher) -->
      <div v-if="hasAdminAccess || isTeacher" class="admin-section">
        <button 
          class="admin-toggle-btn" 
          @click="toggleAdminMenu"
          :class="{ 'active': showAdminMenu }"
        >
          <span class="admin-icon">⚙️</span>
          <span class="admin-text">Администрирование</span>
          <span class="admin-arrow" :class="{ 'rotated': showAdminMenu }">▼</span>
        </button>

        <!-- Выпадающее меню администрирования -->
        <transition name="fade-slide">
          <div v-if="showAdminMenu" class="admin-dropdown" @click.stop>
            <template v-if="isAdmin">
              <router-link :to="{ name: 'admin-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">👥</span>
                <span>Управление пользователями</span>
              </router-link>
              <router-link :to="{ name: 'admin-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📅</span>
                <span>Расписание</span>
              </router-link>
              <router-link :to="{ name: 'admin-courses' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📚</span>
                <span>Курсы</span>
              </router-link>
              <router-link :to="{ name: 'admin-logs' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📋</span>
                <span>Логи</span>
              </router-link>
            </template>
            <template v-else-if="isManager">
              <router-link :to="{ name: 'manager-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📊</span>
                <span>Панель управления</span>
              </router-link>
              <router-link :to="{ name: 'manager-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📅</span>
                <span>Календарь</span>
              </router-link>
              <router-link :to="{ name: 'manager-balance' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">💰</span>
                <span>Балансы</span>
              </router-link>
            </template>
            <template v-else-if="isTeacher">
              <router-link :to="{ name: 'teacher-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📊</span>
                <span>Панель учителя</span>
              </router-link>
              <router-link :to="{ name: 'teacher-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📅</span>
                <span>Мое расписание</span>
              </router-link>
            </template>
          </div>
        </transition>
      </div>

      <!-- Информация об аккаунте / Кнопки входа -->
      <div class="auth-section">
        <template v-if="auth.isAuthenticated && auth.user">
          <!-- Профиль пользователя -->
          <div class="user-menu-wrapper">
            <button class="user-menu-btn" @click="toggleUserMenu">
              <span class="user-email">{{ auth.user.email }}</span>
              <span class="user-role-badge" :class="`role-${auth.normalizedRole}`">
                {{ roleDisplayName }}
              </span>
              <span class="user-arrow" :class="{ 'rotated': showUserMenu }">▼</span>
            </button>

            <!-- Выпадающее меню пользователя -->
            <transition name="fade-slide">
              <div v-if="showUserMenu" class="user-dropdown" @click.stop>
                <div class="dropdown-item user-info">
                  <div class="user-info-email">{{ auth.user.email }}</div>
                  <div class="user-info-role">{{ roleDisplayName }}</div>
                </div>
                <div class="dropdown-divider"></div>
                <router-link 
                  v-if="isTeacher" 
                  :to="{ name: 'teacher-dashboard' }" 
                  class="dropdown-item" 
                  @click="closeUserMenu"
                >
                  <span class="item-icon">📊</span>
                  <span>Панель учителя</span>
                </router-link>
                <router-link 
                  v-if="isTeacher" 
                  :to="{ name: 'teacher-schedule' }" 
                  class="dropdown-item" 
                  @click="closeUserMenu"
                >
                  <span class="item-icon">📅</span>
                  <span>Мое расписание</span>
                </router-link>
                <router-link 
                  v-if="isStudent" 
                  :to="{ name: 'student-dashboard' }" 
                  class="dropdown-item" 
                  @click="closeUserMenu"
                >
                  <span class="item-icon">📊</span>
                  <span>Личный кабинет</span>
                </router-link>
                <router-link 
                  v-if="isApplicant" 
                  :to="{ name: 'applicant-dashboard' }" 
                  class="dropdown-item" 
                  @click="closeUserMenu"
                >
                  <span class="item-icon">📊</span>
                  <span>Личный кабинет</span>
                </router-link>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout-item" @click="handleLogout">
                  <span class="item-icon">🚪</span>
                  <span>Выйти</span>
                </button>
              </div>
            </transition>
          </div>
        </template>
        <template v-else>
          <!-- Кнопки входа и регистрации -->
          <div class="auth-buttons">
            <router-link :to="{ name: 'login' }" class="auth-btn login-btn">
              Войти
            </router-link>
            <router-link :to="{ name: 'register' }" class="auth-btn register-btn">
              Зарегистрироваться
            </router-link>
          </div>
        </template>
      </div>
    </div>

    <!-- Overlay для закрытия меню при клике вне его -->
    <transition name="fade">
      <div 
        v-if="showAdminMenu || showUserMenu" 
        class="menu-overlay" 
        @click="closeAllMenus"
      ></div>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const showAdminMenu = ref(false)
const showUserMenu = ref(false)

const normalizedRole = computed(() => auth.normalizedRole)
const isAdmin = computed(() => normalizedRole.value === 'admin')
const isManager = computed(() => normalizedRole.value === 'manager')
const isTeacher = computed(() => normalizedRole.value === 'teacher')
const isStudent = computed(() => normalizedRole.value === 'student')
const isApplicant = computed(() => normalizedRole.value === 'applicant')

const hasAdminAccess = computed(() => isAdmin.value || isManager.value)

const canEditProfile = computed(() => isApplicant.value || isStudent.value)

const roleDisplayName = computed(() => {
  const roleNames = {
    admin: 'ADMIN',
    manager: 'MANAGER',
    teacher: 'УЧИТЕЛЬ',
    student: 'УЧЕНИК',
    applicant: 'АБИТУРИЕНТ'
  }
  return roleNames[normalizedRole.value] || 'ПОЛЬЗОВАТЕЛЬ'
})

const toggleAdminMenu = () => {
  showAdminMenu.value = !showAdminMenu.value
  showUserMenu.value = false
}

const closeAdminMenu = () => {
  showAdminMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showAdminMenu.value = false
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const closeAllMenus = () => {
  showAdminMenu.value = false
  showUserMenu.value = false
}

const handleLogout = () => {
  closeAllMenus()
  auth.logout()
  router.push({ name: 'home' })
}

// Закрытие меню при клике вне области или при переходе на другую страницу
const handleClickOutside = (event) => {
  if (!event.target.closest('.admin-section') && !event.target.closest('.user-menu-wrapper')) {
    closeAllMenus()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.top-navigation-bar {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(25, 30, 45, 0.95);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  min-height: 64px;
}

.nav-left {
  display: flex;
  align-items: center;
}

.school-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #e8eaf6;
  font-weight: 700;
  font-size: 1.25rem;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 8px;
}

.school-logo:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  letter-spacing: -0.5px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Кнопка администрирования */
.admin-section {
  position: relative;
}

.admin-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 8px;
  color: #c5cae9;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.admin-toggle-btn:hover {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.6);
  color: #e8eaf6;
}

.admin-toggle-btn.active {
  background: rgba(102, 126, 234, 0.4);
  border-color: rgba(102, 126, 234, 0.8);
  color: #ffffff;
}

.admin-icon {
  font-size: 1.1rem;
}

.admin-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
}

.admin-arrow.rotated {
  transform: rotate(180deg);
}

/* Выпадающее меню администрирования */
.admin-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: rgba(30, 35, 50, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 1001;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #c5cae9;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(102, 126, 234, 0.2);
  color: #e8eaf6;
}

.item-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

/* Меню пользователя */
.auth-section {
  position: relative;
}

.user-menu-wrapper {
  position: relative;
}

.user-menu-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #e8eaf6;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-menu-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.user-email {
  color: #e8eaf6;
  font-weight: 600;
}

.user-role-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.user-role-badge.role-admin {
  background: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.5);
}

.user-role-badge.role-manager {
  background: rgba(59, 130, 246, 0.3);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.5);
}

.user-role-badge.role-teacher {
  background: rgba(34, 197, 94, 0.3);
  color: #86efac;
  border: 1px solid rgba(34, 197, 94, 0.5);
}

.user-role-badge.role-student,
.user-role-badge.role-applicant {
  background: rgba(147, 51, 234, 0.3);
  color: #c4b5fd;
  border: 1px solid rgba(147, 51, 234, 0.5);
}

.user-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
  color: #c5cae9;
}

.user-arrow.rotated {
  transform: rotate(180deg);
}

/* Выпадающее меню пользователя */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 240px;
  background: rgba(30, 35, 50, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 1001;
}

.user-info {
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 12px 16px;
  cursor: default;
}

.user-info:hover {
  background: transparent;
}

.user-info-email {
  color: #e8eaf6;
  font-weight: 600;
  font-size: 0.95rem;
}

.user-info-role {
  color: #c5cae9;
  font-size: 0.8rem;
  font-weight: 500;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

.logout-item {
  color: #fca5a5;
}

.logout-item:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #fee2e2;
}

/* Кнопки входа и регистрации */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auth-btn {
  padding: 8px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.login-btn {
  color: #c5cae9;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #e8eaf6;
  border-color: rgba(255, 255, 255, 0.3);
}

.register-btn {
  color: #ffffff;
  background: rgba(102, 126, 234, 0.8);
  border-color: rgba(102, 126, 234, 1);
}

.register-btn:hover {
  background: rgba(102, 126, 234, 1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Overlay */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: transparent;
}

/* Анимации */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .top-navigation-bar {
    padding: 10px 16px;
    gap: 12px;
  }

  .logo-text {
    display: none;
  }

  .admin-text {
    display: none;
  }

  .user-email {
    display: none;
  }

  .auth-buttons {
    gap: 8px;
  }

  .auth-btn {
    padding: 8px 16px;
    font-size: 0.85rem;
  }

  .register-btn .auth-btn-text {
    display: none;
  }
}

@media (max-width: 480px) {
  .school-logo {
    padding: 6px;
  }

  .admin-toggle-btn,
  .user-menu-btn {
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .user-role-badge {
    font-size: 0.7rem;
    padding: 3px 8px;
  }
}
</style>
