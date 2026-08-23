<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
<<<<<<< HEAD
=======
import { LogIn, Lock, User, AlertCircle, Eye, EyeOff } from 'lucide-vue-next'
>>>>>>> main

const auth = useAuthStore()
const router = useRouter()

<<<<<<< HEAD
const email = ref('')
const password = ref('')
=======
const identifier = ref('')
const password = ref('')
const showPassword = ref(false)
>>>>>>> main
const isLoading = ref(false)
const errorMessage = ref('')

onMounted(() => {
<<<<<<< HEAD
  // اگر پیام انقضای کلمه عبور موجود باشد، آن را نمایش دهد
=======
>>>>>>> main
  if (auth.sessionExpiredMessage) {
    errorMessage.value = `⚠️ ${auth.sessionExpiredMessage}`
  }
})

<<<<<<< HEAD
=======
// تبدیل هوشمند ارقام فارسی/عربی کیبورد موبایل به انگلیسی
const normalizeInput = (str) => {
  if (!str) return ''
  return String(str)
    .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧۸٩'.indexOf(d))
    .trim()
}

>>>>>>> main
const handleLogin = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
<<<<<<< HEAD
    if (!email.value.trim()) {
      errorMessage.value = '⚠️ لطفاً ایمیل را وارد کنید'
      isLoading.value = false
      return
    }
    if (!password.value.trim()) {
      errorMessage.value = '⚠️ لطفاً رمز عبور را وارد کنید'
=======
    const cleanIdentifier = normalizeInput(identifier.value)
    const cleanPassword = normalizeInput(password.value)

    if (!cleanIdentifier) {
      errorMessage.value = '⚠️ لطفاً ایمیل یا شماره موبایل خود را وارد کنید.'
      isLoading.value = false
      return
    }
    if (!cleanPassword) {
      errorMessage.value = '⚠️ لطفاً کلمه عبور را وارد کنید.'
>>>>>>> main
      isLoading.value = false
      return
    }
    
<<<<<<< HEAD
    await auth.login(email.value, password.value)
=======
    await auth.login(cleanIdentifier, cleanPassword)
>>>>>>> main
    router.push('/')
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    
    if (status === 401) {
<<<<<<< HEAD
      errorMessage.value = '❌ ایمیل یا رمز عبور اشتباه است'
    } else if (status === 404) {
      errorMessage.value = '❌ کاربری با این ایمیل یافت نشد'
    } else if (status === 422) {
      errorMessage.value = '⚠️ لطفاً ایمیل معتبر وارد کنید'
=======
      errorMessage.value = '❌ ایمیل/شماره موبایل یا رمز عبور اشتباه است.'
    } else if (status === 404) {
      errorMessage.value = '❌ کاربری با این مشخصات یافت نشد.'
>>>>>>> main
    } else {
      errorMessage.value = detail || '❌ خطا در برقراری ارتباط با سرور'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
<<<<<<< HEAD
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
=======
  <div class="min-h-[100dvh] w-full bg-slate-950 flex items-center justify-center p-4 md:p-6 text-right" dir="rtl">
    <div class="w-full max-w-md mx-auto">
      
      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-2xl shadow-purple-500/30">
          <span class="text-white text-3xl font-black">P</span>
        </div>
        <h2 class="text-2xl md:text-3xl font-black text-white">خوش آمدید</h2>
        <p class="text-gray-400 text-xs md:text-sm mt-1">ورود به پنل مدیریت شخصی</p>
      </div>

      <div class="glass-card rounded-3xl border border-white/10 p-6 md:p-8 bg-slate-900/90 shadow-2xl backdrop-blur-xl">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <User class="w-4 h-4 text-purple-400" /> ایمیل یا شماره موبایل
            </label>
            <input 
              v-model="identifier"
              type="text" 
              required 
              autocapitalize="none"
              autocorrect="off"
              spellcheck="false"
              placeholder="you@example.com یا 0912..."
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none transition text-right text-white text-base font-bold dir-ltr placeholder-gray-500"
>>>>>>> main
            />
          </div>

          <div>
<<<<<<< HEAD
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
=======
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center justify-between">
              <span class="flex items-center gap-1.5"><Lock class="w-4 h-4 text-blue-400" /> رمز عبور</span>
              <button type="button" @click="showPassword = !showPassword" class="text-gray-400 hover:text-white text-[11px] flex items-center gap-1">
                <component :is="showPassword ? EyeOff : Eye" class="w-3.5 h-3.5" />
                <span>{{ showPassword ? 'مخفی' : 'نمایش' }}</span>
              </button>
            </label>
            <input 
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required 
              autocapitalize="none"
              autocorrect="off"
              spellcheck="false"
              placeholder="********"
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none transition text-right text-white text-base font-bold dir-ltr placeholder-gray-500"
            />
          </div>

          <div v-if="errorMessage" class="text-xs p-3 rounded-xl font-bold flex items-center gap-2" :class="errorMessage.startsWith('⚠️') ? 'bg-yellow-500/10 border border-yellow-500/20 text-yellow-400' : 'bg-red-500/10 border border-red-500/20 text-red-400'">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{{ errorMessage }}</span>
>>>>>>> main
          </div>

          <button 
            type="submit" 
            :disabled="isLoading"
<<<<<<< HEAD
            class="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:shadow-purple-500/20 transition-all duration-200 disabled:opacity-50"
          >
            <span v-if="!isLoading">ورود</span>
=======
            class="w-full py-3.5 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-black rounded-xl shadow-lg transition duration-200 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
          >
            <LogIn class="w-4 h-4" />
            <span v-if="!isLoading">ورود به حساب</span>
>>>>>>> main
            <span v-else>در حال ورود...</span>
          </button>
        </form>

<<<<<<< HEAD
        <p class="text-center text-sm text-gray-500 mt-4">
          <router-link to="/forgot-password" class="text-purple-400 hover:text-purple-300 transition">رمز عبور رو فراموش کردی؟</router-link>
        </p>

        <p class="text-center text-sm text-gray-500 mt-3">
          حساب کاربری نداری؟
          <router-link to="/register" class="text-purple-400 hover:text-purple-300 font-medium transition">ثبت‌نام کن</router-link>
        </p>
      </div>
=======
        <p class="text-center text-xs text-gray-400 mt-5">
          <router-link to="/forgot-password" class="text-purple-400 hover:text-purple-300 font-bold transition">رمز عبور را فراموش کردی؟</router-link>
        </p>

        <p class="text-center text-xs text-gray-400 mt-3 pt-3 border-t border-white/5">
          حساب کاربری نداری؟
          <router-link to="/register" class="text-purple-400 hover:text-purple-300 font-bold transition">ثبت‌نام کن</router-link>
        </p>
      </div>

>>>>>>> main
    </div>
  </div>
</template>