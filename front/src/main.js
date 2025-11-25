// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// если есть токен в localStorage — сразу пытаемся подтянуть пользователя
const auth = useAuthStore(pinia)
if (auth.access && !auth.user) {
  auth.fetchMe()
}

app.mount('#app')
