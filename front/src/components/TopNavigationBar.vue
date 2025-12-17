<!-- src/components/TopNavigationBar.vue -->
<template>
  <header class="top-navigation-bar">
    <!-- Левая часть - Название школы -->
    <div class="nav-left">
      <router-link :to="{ name: 'home' }" class="school-logo">
        <span class="logo-text">F.L.A.R.E.</span>
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
              <router-link :to="{ name: 'manager-balance' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">💰</span>
                <span>Управление балансами</span>
              </router-link>
              <router-link :to="{ name: 'manager-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📅</span>
                <span>Календарь занятий</span>
              </router-link>
              <router-link :to="{ name: 'manager-requests' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">💬</span>
                <span>Сообщения клиентов</span>
              </router-link>
            </template>
            <template v-else-if="isTeacher">
              <router-link :to="{ name: 'teacher-students' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">👥</span>
                <span>Список учеников</span>
              </router-link>
              <router-link :to="{ name: 'teacher-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                <span class="item-icon">📅</span>
                <span>Расписание занятий</span>
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
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 215, 0, 0.2);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  min-height: 64px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: visible;
  position: relative;
}

.nav-left {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  flex-shrink: 0;
  z-index: 1002;
}

.school-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #FFFFFF;
  font-weight: 900;
  font-size: 1.5rem;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 8px;
  letter-spacing: 1px;
}

.school-logo:hover {
  color: #FFD700;
  transform: translateY(-1px) translateX(0);
}

.logo-text {
  letter-spacing: 2px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 1;
  min-width: 0;
  justify-content: flex-end;
  margin-left: auto;
}

/* Кнопка администрирования */
.admin-section {
  position: relative;
  flex-shrink: 0;
}

.admin-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #FFD700;
  border-radius: 8px;
  color: #FFD700;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-sizing: border-box;
}

.admin-toggle-btn:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.admin-toggle-btn.active {
  background: rgba(255, 215, 0, 0.15);
  border-color: #FFD700;
  color: #FFD700;
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
  max-width: calc(100vw - 48px);
  background: rgba(40, 40, 40, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 1001;
  box-sizing: border-box;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
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
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: rgba(255, 215, 0, 0.15);
  color: #FFD700;
}

.item-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

/* Меню пользователя */
.auth-section {
  position: relative;
  flex-shrink: 0;
}

.user-menu-wrapper {
  position: relative;
  flex-shrink: 0;
}

.user-menu-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-sizing: border-box;
  max-width: 100%;
}

.user-menu-btn:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FFD700;
  color: #FFD700;
}

.user-email {
  color: #FFFFFF;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.user-role-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  box-sizing: border-box;
  white-space: nowrap;
}

.user-role-badge.role-admin {
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  border: 1px solid rgba(255, 215, 0, 0.4);
}

.user-role-badge.role-manager {
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  border: 1px solid rgba(255, 215, 0, 0.4);
}

.user-role-badge.role-teacher {
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  border: 1px solid rgba(255, 215, 0, 0.4);
}

.user-role-badge.role-student,
.user-role-badge.role-applicant {
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  border: 1px solid rgba(255, 215, 0, 0.4);
}

.user-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
  color: rgba(255, 255, 255, 0.7);
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
  max-width: calc(100vw - 48px);
  background: rgba(40, 40, 40, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 1001;
  box-sizing: border-box;
  overflow: hidden;
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
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.user-info-role {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  font-weight: 500;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

.logout-item {
  color: rgba(255, 255, 255, 0.8);
}

.logout-item:hover {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
}

/* Кнопки входа и регистрации */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.auth-btn {
  padding: 8px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap;
  box-sizing: border-box;
  flex-shrink: 0;
}

.login-btn {
  color: #FFD700;
  background: transparent;
  border-color: #FFD700;
}

.login-btn:hover {
  background: rgba(255, 215, 0, 0.1);
  color: #FF8C00;
  border-color: #FF8C00;
}

.register-btn {
  color: #1A1A1A;
  background: #FFD700;
  border-color: #FFD700;
}

.register-btn:hover {
  background: #FF8C00;
  border-color: #FF8C00;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
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
    flex-wrap: nowrap;
  }

  .nav-left {
    left: 16px;
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

  .admin-dropdown,
  .user-dropdown {
    right: 0;
    max-width: calc(100vw - 32px);
  }
}

@media (max-width: 480px) {
  .top-navigation-bar {
    padding: 8px 12px;
    gap: 8px;
  }

  .nav-left {
    left: 12px;
  }


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

  .admin-dropdown,
  .user-dropdown {
    right: 0;
    max-width: calc(100vw - 24px);
    min-width: 200px;
  }

  .nav-right {
    gap: 8px;
  }
}
</style>
