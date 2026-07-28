<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const fullName = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    if (!fullName.value.trim()) {
      errorMessage.value = '⚠️ لطفاً نام خود را وارد کنید'
      isLoading.value = false; return
    }
    if (!email.value.trim() || !email.value.includes('@')) {
      errorMessage.value = '⚠️ لطفاً ایمیل معتبر وارد کنید'
      isLoading.value = false; return
    }
    if (!phone.value.trim()) {
      errorMessage.value = '⚠️ لطفاً شماره موبایل را وارد کنید'
      isLoading.value = false; return
    }
    if (!password.value.trim() || password.value.length < 6) {
      errorMessage.value = '⚠️ رمز عبور باید حداقل ۶ کاراکتر باشد'
      isLoading.value = false; return
    }
    
    await auth.register(email.value, password.value, fullName.value, phone.value)
    router.push('/')
  } catch (error) {
    const status = error.response?.status
    if (status === 400) errorMessage.value = '❌ این ایمیل قبلاً ثبت شده است'
    else if (status === 422) errorMessage.value = '⚠️ لطفاً ایمیل معتبر وارد کنید'
    else errorMessage.value = '❌ خطا در برقراری ارتباط با سرور'
  } finally { isLoading.value = false }
}
</script>

<template>
  <div class="min-h-screen bg-surface-dark flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-2xl shadow-purple-500/30">
          <span class="text-white text-3xl font-extrabold">P</span>
        </div>
        <h2 class="text-3xl font-extrabold text-white">ثبت‌نام</h2>
        <p class="text-gray-500 mt-1">حساب کاربری جدید بساز</p>
      </div>

      <div class="bg-surface-card rounded-2xl border border-white/5 p-8">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-400 mb-2">نام کامل *</label>
            <input v-model="fullName" required placeholder="نام و نام خانوادگی"
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-right text-gray-200" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">ایمیل *</label>
            <input v-model="email" type="email" required placeholder="you@example.com"
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-right text-gray-200" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">شماره موبایل *</label>
            <input v-model="phone" type="tel" required placeholder="09123456789"
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-right text-gray-200" dir="ltr" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">رمز عبور *</label>
            <input v-model="password" type="password" required placeholder="حداقل ۶ کاراکتر"
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-right text-gray-200" />
          </div>

          <div v-if="errorMessage" class="text-sm p-3 rounded-xl" :class="errorMessage.startsWith('⚠️') ? 'bg-yellow-500/10 text-yellow-400' : 'bg-red-500/10 text-red-400'">
            {{ errorMessage }}
          </div>

          <button type="submit" :disabled="isLoading"
                  class="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl transition disabled:opacity-50">
            {{ isLoading ? 'در حال ثبت‌نام...' : 'ثبت‌نام' }}
          </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-6">
          حساب کاربری داری؟ <router-link to="/login" class="text-purple-400 hover:text-purple-300 font-medium transition">وارد شو</router-link>
        </p>
      </div>
    </div>
  </div>
</template>