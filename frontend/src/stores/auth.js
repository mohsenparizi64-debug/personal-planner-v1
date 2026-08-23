import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const sessionExpiredMessage = ref('') // پیام انقضای کلمه عبور
  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    sessionExpiredMessage.value = '' // پاک‌سازی پیام انقضا در صورت ورود موفق
    await fetchUser()
  }

  async function register(email, password, fullName, phone) {
    await api.post('/auth/register', { email, password, full_name: fullName, phone })
    await login(email, password)
  }

  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (e) {
      user.value = null
    }
  }

  async function updateProfile(data) {
    const response = await api.put('/auth/me', data)
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete api.defaults.headers.common['Authorization']
  }

  // انقضای نشست/کلمه عبور پس از ۵ دقیقه عدم فعالیت
  function expireSession() {
    logout()
    sessionExpiredMessage.value = 'با توجه به منقضی شدن کلمه عبور مجددا وارد شوید.'
  }

  function clearExpiredMessage() {
    sessionExpiredMessage.value = ''
  }

  return { 
    token, 
    user, 
    isAuthenticated, 
    sessionExpiredMessage,
    login, 
    register, 
    logout, 
    fetchUser, 
    updateProfile,
    expireSession,
    clearExpiredMessage
  }
})