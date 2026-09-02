import axios from 'axios'

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
// (اول از sessionStorage، سپس از localStorage — برای پشتیبانی از «مرا بخاطر بسپار»)
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default api
