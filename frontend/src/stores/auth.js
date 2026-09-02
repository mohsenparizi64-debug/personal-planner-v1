import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

// کلیدهای ذخیره‌سازی
const STORAGE_KEYS = {
  token: 'token',
  user: 'user',
  remember: 'rememberIdentifier',
  rememberPassword: 'rememberPassword',
}

export const useAuthStore = defineStore('auth', () => {
  // 🧠 بازیابی توکن: اول sessionStorage (اگر «مرا بخاطر بسپار» خاموش باشد)، سپس localStorage
  const token = ref(
    sessionStorage.getItem(STORAGE_KEYS.token) ||
    localStorage.getItem(STORAGE_KEYS.token) ||
    ''
  )
  const user = ref(
    JSON.parse(
      sessionStorage.getItem(STORAGE_KEYS.user) ||
      localStorage.getItem(STORAGE_KEYS.user) ||
      'null'
    )
  )
  const sessionExpiredMessage = ref('')
  const isAuthenticated = computed(() => !!token.value)

  // 🧹 پاک‌سازی همه‌ی جاهای ذخیره‌سازی
  const clearAllStorage = () => {
    sessionStorage.removeItem(STORAGE_KEYS.token)
    sessionStorage.removeItem(STORAGE_KEYS.user)
    localStorage.removeItem(STORAGE_KEYS.token)
    localStorage.removeItem(STORAGE_KEYS.user)
    localStorage.removeItem(STORAGE_KEYS.remember)
    localStorage.removeItem(STORAGE_KEYS.rememberPassword)
  }

  // 💾 ذخیره‌سازی بر اساس «مرا بخاطر بسپار»
  const persistAuth = (accessToken, userData, rememberMe) => {
    const userJson = JSON.stringify(userData)
    if (rememberMe) {
      // 🧠 ماندگار: حتی پس از بستن مرورگر هم باقی می‌ماند
      localStorage.setItem(STORAGE_KEYS.token, accessToken)
      localStorage.setItem(STORAGE_KEYS.user, userJson)
    } else {
      // ⏱ موقت: فقط تا بستن تب/مرورگر
      sessionStorage.setItem(STORAGE_KEYS.token, accessToken)
      sessionStorage.setItem(STORAGE_KEYS.user, userJson)
    }
  }

  async function login(email, password, rememberMe = false) {
    const response = await api.post('/auth/login', {
      email,
      password,
      remember_me: rememberMe,
    })
    token.value = response.data.access_token
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    sessionExpiredMessage.value = ''
    await fetchUser()

    // 🧠 ذخیره‌سازی یوزرنیم/پسورد فقط در صورت فعال بودن «مرا بخاطر بسپار»
    if (rememberMe) {
      localStorage.setItem(STORAGE_KEYS.remember, email)
      localStorage.setItem(STORAGE_KEYS.rememberPassword, password)
    } else {
      localStorage.removeItem(STORAGE_KEYS.remember)
      localStorage.removeItem(STORAGE_KEYS.rememberPassword)
    }
  }

  async function register(email, password, fullName, phone) {
    await api.post('/auth/register', { email, password, full_name: fullName, phone })
    await login(email, password, false) // ثبت‌نام = بدون مرا بخاطر بسپار
  }

  // 🛡️ ارسال کد تأیید OTP (برای ثبت‌نام با SMS/Email)
  async function sendRegistrationOTP(type, target, honeypot = '') {
    const response = await api.post('/auth/send-otp', {
      type,
      target,
      honeypot,
    })
    return response.data
  }

  // 🛡️ تأیید کد و تکمیل ثبت‌نام
  async function verifyAndRegister(payload) {
    const response = await api.post('/auth/verify-and-register', payload)
    if (response.data.access_token) {
      token.value = response.data.access_token
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      sessionStorage.setItem(STORAGE_KEYS.token, response.data.access_token)
    }
    await fetchUser()
    return response.data
  }

  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      // به‌روزرسانی در هر دو حافظه
      const userJson = JSON.stringify(response.data)
      if (localStorage.getItem(STORAGE_KEYS.token)) {
        localStorage.setItem(STORAGE_KEYS.user, userJson)
      }
      if (sessionStorage.getItem(STORAGE_KEYS.token)) {
        sessionStorage.setItem(STORAGE_KEYS.user, userJson)
      }
    } catch (e) {
      user.value = null
    }
  }

  async function updateProfile(data) {
    const response = await api.put('/auth/me', data)
    user.value = response.data
    const userJson = JSON.stringify(response.data)
    if (localStorage.getItem(STORAGE_KEYS.token)) {
      localStorage.setItem(STORAGE_KEYS.user, userJson)
    }
    if (sessionStorage.getItem(STORAGE_KEYS.token)) {
      sessionStorage.setItem(STORAGE_KEYS.user, userJson)
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    clearAllStorage()
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
    sendRegistrationOTP,
    verifyAndRegister,
    logout,
    fetchUser,
    updateProfile,
    expireSession,
    clearExpiredMessage,
  }
})
