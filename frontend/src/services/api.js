import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // اگر درخواست به لاگین یا ثبت‌نام نبوده و توکن منقضی شده باشد
      const isAuthEndpoint = error.config.url.includes('/auth/login') || error.config.url.includes('/auth/register')
      
      if (!isAuthEndpoint) {
        const authStore = useAuthStore()
        // فعال‌سازی مدال انقضا و تنظیم پیام
        authStore.expireSession()
      }
    }
    return Promise.reject(error)
  }
)

export default api