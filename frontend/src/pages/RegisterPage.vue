<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Mail, Lock, User, Phone, KeyRound, ArrowRight, RefreshCw,
  CheckCircle2, AlertCircle, ShieldCheck, Smartphone
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

const regMethod = ref('sms')
const currentStep = ref(1)

const fullName = ref('')
const targetValue = ref('')
const password = ref('')
const otpCode = ref('')
const honeypot = ref('')

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const countdown = ref(0)
let countdownInterval = null

// 🔍 تبدیل خودکار ارقام فارسی/عربی کیبورد موبایل به انگلیسی و حذف فاصله
const normalizeInput = (str) => {
  if (!str) return ''
  return String(str)
    .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧۸٩'.indexOf(d))
    .trim()
}

const startCountdown = (seconds = 60) => {
  countdown.value = seconds
  if (countdownInterval) clearInterval(countdownInterval)
  countdownInterval = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(countdownInterval)
    }
  }, 1000)
}

onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval)
})

const handleSendCode = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  const cleanTarget = normalizeInput(targetValue.value)
  const cleanPass = normalizeInput(password.value)

  if (regMethod.value === 'sms') {
    if (!cleanTarget || !cleanTarget.startsWith('09') || cleanTarget.length !== 11) {
      errorMessage.value = '⚠️ لطفاً یک شماره موبایل معتبر ۱۱ رقمی (مثلاً 09123456789) وارد کنید.'
      return
    }
  } else {
    if (!cleanTarget || !cleanTarget.includes('@')) {
      errorMessage.value = '⚠️ لطفاً یک آدرس ایمیل معتبر وارد کنید.'
      return
    }
  }

  if (!cleanPass || cleanPass.length < 6) {
    errorMessage.value = '⚠️ کلمه عبور باید حداقل ۶ کاراکتر باشد.'
    return
  }

  try {
    isLoading.value = true
    const res = await auth.sendRegistrationOTP(
      regMethod.value,
      cleanTarget,
      honeypot.value
    )
    successMessage.value = res.message || 'کد تأیید با موفقیت ارسال شد.'
    currentStep.value = 2
    startCountdown(60)
  } catch (error) {
    const detail = error.response?.data?.detail
    errorMessage.value = detail || '❌ خطا در ارسال کد تأیید. لطفاً مجدداً تلاش کنید.'
  } finally {
    isLoading.value = false
  }
}

const handleVerifyAndRegister = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  const cleanOTP = normalizeInput(otpCode.value)
  const cleanTarget = normalizeInput(targetValue.value)
  const cleanPass = normalizeInput(password.value)

  if (!cleanOTP || cleanOTP.length !== 6) {
    errorMessage.value = '⚠️ لطفاً کد ۶ رقمی را به صورت کامل وارد کنید.'
    return
  }

  try {
    isLoading.value = true
    await auth.verifyAndRegister({
      type: regMethod.value,
      target: cleanTarget,
      code: cleanOTP,
      password: cleanPass,
      full_name: fullName.value.trim() || null,
      honeypot: honeypot.value
    })

    router.push('/')
  } catch (error) {
    const detail = error.response?.data?.detail
    errorMessage.value = detail || '❌ کد تأیید نامعتبر یا منقضی شده است.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-[100dvh] w-full bg-slate-950 flex items-center justify-center p-4 text-right" dir="rtl">
    <div class="w-full max-w-md mx-auto">

      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-2xl shadow-purple-500/30">
          <span class="text-white text-3xl font-black">P</span>
        </div>
        <h2 class="text-2xl md:text-3xl font-black text-white">ثبت‌نام در پلنر شخصی</h2>
        <p class="text-xs md:text-sm text-gray-400 mt-1">مدیریت هوشمند اهداف، تسک‌ها و سبک زندگی</p>
      </div>

      <div class="glass-card rounded-3xl border border-white/10 p-6 md:p-8 shadow-2xl bg-slate-900/90 backdrop-blur-xl">

        <div v-if="currentStep === 1" class="flex gap-1.5 p-1 bg-white/5 rounded-2xl border border-white/10 mb-6">
          <button
            type="button"
            @click="regMethod = 'sms'; targetValue = ''; errorMessage = ''"
            class="flex-1 py-2.5 rounded-xl text-xs font-black transition flex items-center justify-center gap-1.5"
            :class="regMethod === 'sms' ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'"
          >
            <Smartphone class="w-4 h-4" />
            <span>ثبت‌نام با پیامک</span>
          </button>

          <button
            type="button"
            @click="regMethod = 'email'; targetValue = ''; errorMessage = ''"
            class="flex-1 py-2.5 rounded-xl text-xs font-black transition flex items-center justify-center gap-1.5"
            :class="regMethod === 'email' ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'"
          >
            <Mail class="w-4 h-4" />
            <span>ثبت‌نام با ایمیل</span>
          </button>
        </div>

        <form v-if="currentStep === 1" @submit.prevent="handleSendCode" class="space-y-4">
          <input v-model="honeypot" type="text" tabindex="-1" autocomplete="off" class="opacity-0 absolute -z-50 h-0 w-0 pointer-events-none" />

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <User class="w-4 h-4 text-purple-400" /> نام و نام خانوادگی
            </label>
            <input
              v-model="fullName"
              type="text"
              placeholder="مثلاً: علی رضایی"
              class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-base font-bold outline-none focus:ring-2 focus:ring-purple-500 transition"
            />
          </div>

          <div v-if="regMethod === 'sms'">
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <Phone class="w-4 h-4 text-emerald-400" /> شماره موبایل *
            </label>
            <input
              v-model="targetValue"
              type="tel"
              required
              autocapitalize="none"
              autocorrect="off"
              placeholder="09123456789"
              maxlength="11"
              class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-base font-bold outline-none focus:ring-2 focus:ring-purple-500 transition dir-ltr text-right"
            />
          </div>

          <div v-else>
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <Mail class="w-4 h-4 text-blue-400" /> آدرس ایمیل *
            </label>
            <input
              v-model="targetValue"
              type="email"
              required
              autocapitalize="none"
              autocorrect="off"
              placeholder="you@example.com"
              class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-base font-bold outline-none focus:ring-2 focus:ring-purple-500 transition dir-ltr text-right"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <Lock class="w-4 h-4 text-amber-400" /> کلمه عبور *
            </label>
            <input
              v-model="password"
              type="password"
              required
              autocapitalize="none"
              autocorrect="off"
              placeholder="حداقل ۶ کاراکتر"
              class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-base font-bold outline-none focus:ring-2 focus:ring-purple-500 transition dir-ltr text-right"
            />
          </div>

          <div v-if="errorMessage" class="text-xs p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-bold flex items-center gap-2">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{{ errorMessage }}</span>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3.5 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-black rounded-xl shadow-lg transition duration-200 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
          >
            <ShieldCheck class="w-4 h-4" />
            <span v-if="!isLoading">ارسال کد تأیید</span>
            <span v-else>در حال ارسال...</span>
          </button>
        </form>

        <form v-else @submit.prevent="handleVerifyAndRegister" class="space-y-4">
          <div class="text-center bg-white/5 p-4 rounded-2xl border border-white/10 mb-4">
            <p class="text-xs text-gray-300">کد تأیید به {{ regMethod === 'sms' ? 'شماره' : 'ایمیل' }} زیر ارسال شد:</p>
            <p class="text-sm font-black text-purple-400 dir-ltr mt-1">{{ targetValue }}</p>
            <button
              type="button"
              @click="currentStep = 1; errorMessage = ''; successMessage = ''"
              class="text-[11px] text-gray-400 hover:text-white underline mt-2 inline-flex items-center gap-1"
            >
              <ArrowRight class="w-3 h-3" /> تغییر {{ regMethod === 'sms' ? 'شماره' : 'ایمیل' }}
            </button>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <KeyRound class="w-4 h-4 text-emerald-400" /> کد تأیید ۶ رقمی *
            </label>
            <input
              v-model="otpCode"
              type="text"
              required
              maxlength="6"
              autofocus
              placeholder="123456"
              class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-xl font-black tracking-widest text-center outline-none focus:ring-2 focus:ring-purple-500 transition dir-ltr"
            />
          </div>

          <div v-if="successMessage" class="text-xs p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold flex items-center gap-2">
            <CheckCircle2 class="w-4 h-4 shrink-0" />
            <span>{{ successMessage }}</span>
          </div>

          <div v-if="errorMessage" class="text-xs p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-bold flex items-center gap-2">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{{ errorMessage }}</span>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-black rounded-xl shadow-lg transition duration-200 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
          >
            <CheckCircle2 class="w-4 h-4" />
            <span v-if="!isLoading">تأیید و تکمیل ثبت‌نام</span>
            <span v-else>در حال بررسی...</span>
          </button>

          <div class="text-center pt-2">
            <button
              type="button"
              @click="handleSendCode"
              :disabled="countdown > 0 || isLoading"
              class="text-xs font-bold text-purple-400 hover:text-purple-300 disabled:text-gray-500 transition inline-flex items-center gap-1.5"
            >
              <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
              <span v-if="countdown > 0">ارسال مجدد کد تا {{ countdown }} ثانیه دیگر</span>
              <span v-else>ارسال مجدد کد تأیید</span>
            </button>
          </div>
        </form>

        <p class="text-center text-xs text-gray-400 mt-5 pt-4 border-t border-white/5">
          قبلاً ثبت‌نام کرده‌ای؟
          <router-link to="/login" class="text-purple-400 hover:text-purple-300 font-bold transition">وارد شو</router-link>
        </p>

      </div>

    </div>
  </div>
</template>
