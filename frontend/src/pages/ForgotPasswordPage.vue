<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const step = ref(1)
const email = ref('')
const token = ref('')
const newPassword = ref('')
const message = ref('')
const messageType = ref('success')
const isLoading = ref(false)

const sendResetEmail = async () => {
  isLoading.value = true
  try {
    const res = await api.post('/auth/forgot-password', { email: email.value })
    token.value = res.data.token
    message.value = '✅ لینک بازیابی آماده است. توکن رو وارد کن.'
    messageType.value = 'success'
    step.value = 2
  } catch (e) {
    message.value = '❌ ایمیلی با این آدرس یافت نشد'
    messageType.value = 'error'
  } finally { isLoading.value = false }
}

const resetPassword = async () => {
  if (newPassword.value.length < 6) {
    message.value = '❌ رمز عبور حداقل ۶ کاراکتر باشد'
    messageType.value = 'error'
    return
  }
  isLoading.value = true
  try {
    await api.post('/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value
    })
    message.value = '✅ رمز عبور با موفقیت تغییر کرد!'
    messageType.value = 'success'
    setTimeout(() => router.push('/login'), 2000)
  } catch (e) {
    message.value = '❌ توکن نامعتبر یا منقضی شده'
    messageType.value = 'error'
  } finally { isLoading.value = false }
}
</script>

<template>
  <div class="min-h-screen bg-surface-dark flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-2xl shadow-purple-500/30">
          <span class="text-white text-3xl font-extrabold">🔑</span>
        </div>
        <h2 class="text-3xl font-extrabold text-white">بازیابی رمز عبور</h2>
        <p class="text-gray-500 mt-1">{{ step === 1 ? 'ایمیلت رو وارد کن' : 'توکن و رمز جدید رو وارد کن' }}</p>
      </div>

      <div class="bg-surface-card rounded-2xl border border-white/5 p-8">
        <div v-if="message" :class="messageType === 'error' ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'" class="p-3 rounded-xl mb-4 text-sm">{{ message }}</div>

        <form v-if="step === 1" @submit.prevent="sendResetEmail" class="space-y-5">
          <div>
            <label class="block text-sm text-gray-400 mb-2">ایمیل</label>
            <input v-model="email" type="email" required placeholder="you@example.com"
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-right text-gray-200" />
          </div>
          <button type="submit" :disabled="isLoading"
                  class="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl transition disabled:opacity-50">
            {{ isLoading ? 'در حال ارسال...' : 'ارسال لینک بازیابی' }}
          </button>
        </form>

        <form v-if="step === 2" @submit.prevent="resetPassword" class="space-y-5">
          <div>
            <label class="block text-sm text-gray-400 mb-2">توکن بازیابی</label>
            <input v-model="token" type="text" required
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-left text-gray-200 font-mono text-sm" dir="ltr" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-2">رمز عبور جدید</label>
            <input v-model="newPassword" type="password" required placeholder="حداقل ۶ کاراکتر"
                   class="block w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 text-right text-gray-200" />
          </div>
          <button type="submit" :disabled="isLoading"
                  class="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl transition disabled:opacity-50">
            {{ isLoading ? 'در حال تغییر...' : 'تغییر رمز عبور' }}
          </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-6">
          <router-link to="/login" class="text-purple-400 hover:text-purple-300 transition">برگشت به ورود</router-link>
        </p>
      </div>
    </div>
  </div>
</template>