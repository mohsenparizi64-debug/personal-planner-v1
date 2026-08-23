import axios from 'axios'
<<<<<<< HEAD
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
=======

// شناسایی هوشمند و دقیق هاست/آی‌پی برای اتصال به بک‌اند
const getBaseURL = () => {
  // اگر متغیر محیطی Vite تنظیم شده باشد از آن استفاده می‌کند
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  const hostname = window.location.hostname || 'localhost'
  
  // اگر در لوکال‌هاست یا 127.0.0.1 بودیم
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `http://${hostname}:8000/api/v1`
  }
  
  // برای دسترسی از طریق IP سرور VPS یا مرورگرهای خارجی
  return `http://${hostname}:8000/api/v1`
}

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json'
  }
})

// ارسال خودکار توکن JWT در تمامی درخواست‌ها
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
>>>>>>> main
    return Promise.reject(error)
  }
)

export default api