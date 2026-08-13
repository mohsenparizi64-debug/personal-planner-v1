<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

onMounted(() => {
  // اگر پیام انقضای کلمه عبور موجود باشد، آن را نمایش دهد
  if (auth.sessionExpiredMessage) {
    errorMessage.value = `⚠️ ${auth.sessionExpiredMessage}`
  }
})

const handleLogin = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    if (!email.value.trim()) {
      errorMessage.value = '⚠️ لطفاً ایمیل را وارد کنید'
      isLoading.value = false
      return
    }
    if (!password.value.trim()) {
      errorMessage.value = '⚠️ لطفاً رمز عبور را وارد کنید'
      isLoading.value = false
      return
    }
    
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    
    if (status === 401) {
      errorMessage.value = '❌ ایمیل یا رمز عبور اشتباه است'
    } else if (status === 404) {
      errorMessage.value = '❌ کاربری با این ایمیل یافت نشد'
    } else if (status === 422) {
      errorMessage.value = '⚠️ لطفاً ایمیل معتبر وارد کنید'
    } else {
      errorMessage.value = detail || '❌ خطا در برقراری ارتباط با سرور'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-surface-dark flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-2xl shadow-purple-500/30">
          <span class="text-white text-3xl font-extrabold">P</span>
        </div>
        <h2 class="text-3xl font-extrabold text-white">خوش برگشتی!</h2>
        <p class="text-gray-500 mt-1">به پلنر شخصی خود وارد شو</p>
      </div>

      <div class="bg-surface-card rounded-2xl border border-white/5 p-8">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm text-gray-400 mb-2">ایمیل</label>
            <input 
              v-model="email"
              type="email" 
              required 
              placeholder="you@example.com"
              class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition text-right text-gray-200 placeholder-gray-600"
            />
          </div>

          <div>
            <label class="block text-sm text-gray-400 mb-2">رمز عبور</label>
            <input 
              v-model="password"
              type="password"
              required 
              placeholder="********"
              class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition text-right text-gray-200 placeholder-gray-600"
            />
          </div>

          <!-- باکس پیام انقضا یا خطا -->
          <div v-if="errorMessage" class="text-sm p-3 rounded-xl font-bold" :class="errorMessage.startsWith('⚠️') ? 'bg-yellow-500/10 border border-yellow-500/20 text-yellow-400' : 'bg-red-500/10 border border-red-500/20 text-red-400'">
            {{ errorMessage }}
          </div>

          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:shadow-purple-500/20 transition-all duration-200 disabled:opacity-50"
          >
            <span v-if="!isLoading">ورود</span>
            <span v-else>در حال ورود...</span>
          </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-4">
          <router-link to="/forgot-password" class="text-purple-400 hover:text-purple-300 transition">رمز عبور رو فراموش کردی؟</router-link>
        </p>

        <p class="text-center text-sm text-gray-500 mt-3">
          حساب کاربری نداری؟
          <router-link to="/register" class="text-purple-400 hover:text-purple-300 font-medium transition">ثبت‌نام کن</router-link>
        </p>
      </div>
    </div>
  </div>
</template>