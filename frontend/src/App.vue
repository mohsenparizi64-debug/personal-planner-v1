<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import AnalogClock from '@/components/AnalogClock.vue'
import {
  LayoutDashboard, ListTodo, Target, Wallet, Film, MapPin, BookOpen, Download,
  Menu, X, LogOut, Calendar, Clock, Palette, Lock, KeyRound, Lightbulb, Type, Sparkles,
  HeartPulse, Award
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const sidebarOpen = ref(false)
const themeMenuOpen = ref(false)
const fontMenuOpen = ref(false)
const showLogoutConfirm = ref(false)
const currentTime = ref('')
const currentTimeEn = ref('')
const currentDate = ref('')
const currentDateShort = ref('')
const persianDate = ref('')
const persianDateShort = ref('')
const dayOfWeek = ref('')

const isAuthPage = computed(() => {
  return ['/login', '/register', '/forgot-password'].includes(route.path)
})

// ⏱️ افزایش زمان عدم فعالیت به ۶۰ دقیقه (هماهنگ با توکن ۱ ساعته)
const INACTIVITY_LIMIT = 60 * 60 * 1000
let inactivityTimer = null

const staticParticles = [
  { left: '10%', delay: '0s', duration: '4s' },
  { left: '25%', delay: '1.5s', duration: '5s' },
  { left: '40%', delay: '0.8s', duration: '3.5s' },
  { left: '60%', delay: '2s', duration: '4.5s' },
  { left: '75%', delay: '1s', duration: '5.5s' },
  { left: '90%', delay: '2.5s', duration: '4s' },
]

const showExpiredModal = ref(false)
const expiredEmail = ref('')
const expiredPassword = ref('')
const expiredLoginLoading = ref(false)
const expiredLoginError = ref('')

const menuItems = [
  { path: '/', label: 'داشبورد', icon: LayoutDashboard },
  { path: '/mentor', label: 'منتور هوشمند', icon: Sparkles },
  { path: '/bio', label: 'پایش زیست و سلامت', icon: HeartPulse },
  { path: '/skills', label: 'بانک مهارت‌ها', icon: Award },
  { path: '/ideas', label: 'ایده‌ها', icon: Lightbulb },
  { path: '/tasks', label: 'تسک‌ها', icon: ListTodo },
  { path: '/goals', label: 'اهداف', icon: Target },
  { path: '/roadmap', label: 'نقشه راه', icon: MapPin },
  { path: '/calendar', label: 'تقویم', icon: Calendar },
  { path: '/finance', label: 'مالی', icon: Wallet },
  { path: '/movies', label: 'فیلم‌ها', icon: Film },
  { path: '/books', label: 'کتاب‌ها', icon: BookOpen },
  { path: '/places', label: 'مکان‌ها', icon: MapPin },
  { path: '/backup', label: 'بکاپ', icon: Download },
]

function updateDateTime() {
  const now = new Date()
  currentTimeEn.value = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
  currentTime.value = now.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDate.value = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
  currentDateShort.value = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  dayOfWeek.value = now.toLocaleDateString('fa-IR', { weekday: 'long' })
  persianDate.value = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { year: 'numeric', month: 'long', day: 'numeric' }).format(now)
  persianDateShort.value = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { month: 'short', day: 'numeric' }).format(now)
}

const resetInactivityTimer = () => {
  if (!authStore.isAuthenticated || isAuthPage.value) {
    if (inactivityTimer) clearTimeout(inactivityTimer)
    return
  }

  if (inactivityTimer) clearTimeout(inactivityTimer)

  inactivityTimer = setTimeout(() => {
    handleInactivityTimeout()
  }, INACTIVITY_LIMIT)
}

const handleInactivityTimeout = () => {
  if (authStore.isAuthenticated && !isAuthPage.value) {
    if (authStore.user?.email || authStore.user?.phone) {
      expiredEmail.value = authStore.user.email || authStore.user.phone
    }
    authStore.expireSession()
    showExpiredModal.value = true
  }
}

const activityEvents = [
  'mousemove', 'mousedown', 'keydown', 'keyup',
  'input', 'change', 'focusin', 'touchstart', 'scroll'
]

const setupActivityListeners = () => {
  activityEvents.forEach(event => {
    window.addEventListener(event, resetInactivityTimer, { capture: true, passive: true })
  })
}

const removeActivityListeners = () => {
  activityEvents.forEach(event => {
    window.removeEventListener(event, resetInactivityTimer, { capture: true })
  })
  if (inactivityTimer) clearTimeout(inactivityTimer)
}

watch(() => authStore.sessionExpiredMessage, (newMsg) => {
  if (newMsg && !isAuthPage.value) {
    if (authStore.user?.email || authStore.user?.phone) {
      expiredEmail.value = authStore.user.email || authStore.user.phone
    }
    showExpiredModal.value = true
  }
})

const handleExpiredLogin = async () => {
  try {
    expiredLoginLoading.value = true
    expiredLoginError.value = ''

    if (!expiredEmail.value.trim() || !expiredPassword.value.trim()) {
      expiredLoginError.value = '⚠️ لطفاً ایمیل یا شماره موبایل و رمز عبور را وارد کنید'
      return
    }

    await authStore.login(expiredEmail.value, expiredPassword.value, false)
    showExpiredModal.value = false
    expiredPassword.value = ''
    resetInactivityTimer()
  } catch (error) {
    const status = error.response?.status
    if (status === 401) {
      expiredLoginError.value = '❌ رمز عبور اشتباه است'
    } else {
      expiredLoginError.value = '❌ خطا در برقراری ارتباط با سرور'
    }
  } finally {
    expiredLoginLoading.value = false
  }
}

let timer = null

onMounted(() => {
  updateDateTime()
  timer = setInterval(updateDateTime, 1000)

  if (authStore.isAuthenticated) {
    authStore.fetchUser()
    resetInactivityTimer()
  }

  setupActivityListeners()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  removeActivityListeners()
})

watch(() => authStore.isAuthenticated, (newVal) => {
  if (newVal) {
    resetInactivityTimer()
  } else {
    if (inactivityTimer) clearTimeout(inactivityTimer)
  }
})

const handleLogout = () => {
  showLogoutConfirm.value = true
}

const confirmLogout = () => {
  authStore.logout()
  showLogoutConfirm.value = false
  showExpiredModal.value = false
  sidebarOpen.value = false
  router.push('/login')
}

const cancelLogout = () => {
  showLogoutConfirm.value = false
}
</script>

<template>
  <div v-if="isAuthPage" class="min-h-[100dvh] w-full text-right" :class="[themeStore.currentTheme]" dir="rtl">
    <router-view />
  </div>

  <div v-else class="flex h-[100dvh] w-full overflow-hidden relative text-right" dir="rtl" :class="[themeStore.currentTheme]">

    <div
      v-if="sidebarOpen"
      @click="sidebarOpen = false"
      class="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
    ></div>

    <aside
      class="fixed lg:static inset-y-0 right-0 w-64 z-50 transition-transform duration-300 ease-in-out flex flex-col border-l shadow-2xl lg:shadow-none"
      :class="sidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'"
    >
      <div class="p-4 border-b border-white/10 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
            <span class="text-white font-black text-base">P</span>
          </div>
          <div>
            <h1 class="text-sm font-black" :style="{ color: 'var(--text-primary)' }">پلنر شخصی</h1>
            <p class="text-[11px] sm:text-[10px] font-bold" :style="{ color: 'var(--text-secondary)' }">مدیریت هوشمند اهداف</p>
          </div>
        </div>

        <button @click="sidebarOpen = false" class="lg:hidden p-1.5 rounded-lg bg-white/5">
          <X class="w-4 h-4" :style="{ color: 'var(--text-secondary)' }" />
        </button>
      </div>

      <nav class="flex-1 p-2.5 space-y-1 overflow-y-auto custom-scrollbar">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          @click="sidebarOpen = false"
          class="flex items-center gap-2.5 px-3.5 py-2 rounded-xl transition-all duration-200 text-xs font-bold"
          :style="route.path === item.path ? { background: 'var(--accent)', color: '#fff', boxShadow: '0 0 15px var(--glow)' } : { color: 'var(--text-secondary)' }"
        >
          <component :is="item.icon" class="w-4 h-4 shrink-0" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="p-2.5 border-t border-white/10 space-y-1.5">
        <button
          @click="themeMenuOpen = !themeMenuOpen; fontMenuOpen = false"
          class="flex items-center gap-2 w-full px-3 py-2 rounded-lg transition text-xs font-bold bg-white/5 hover:bg-white/10"
          :style="{ color: 'var(--text-primary)' }"
        >
          <Palette class="w-4 h-4 text-purple-400" />
          <span>تغییر تم</span>
        </button>

        <div v-if="themeMenuOpen" class="space-y-1 rounded-xl p-1.5 border border-white/10" :style="{ background: 'var(--bg-secondary)' }">
          <button
            v-for="theme in themeStore.themes"
            :key="theme.id"
            @click="themeStore.setTheme(theme.id); themeMenuOpen = false"
            class="block w-full text-right px-2 py-1.5 rounded-md text-[11px] sm:text-[10px] font-bold transition"
            :style="themeStore.currentTheme === theme.id ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-primary)' }"
          >
            {{ theme.icon }} {{ theme.label }}
          </button>
        </div>

        <button
          @click="fontMenuOpen = !fontMenuOpen; themeMenuOpen = false"
          class="flex items-center gap-2 w-full px-3 py-2 rounded-lg transition text-xs font-bold bg-white/5 hover:bg-white/10"
          :style="{ color: 'var(--text-primary)' }"
        >
          <Type class="w-4 h-4 text-blue-400" />
          <span>اندازه قلم</span>
        </button>

        <div v-if="fontMenuOpen" class="space-y-1 rounded-xl p-1.5 border border-white/10" :style="{ background: 'var(--bg-secondary)' }">
          <button
            v-for="opt in themeStore.fontScaleOptions"
            :key="opt.id"
            @click="themeStore.setFontScale(opt.id); fontMenuOpen = false"
            class="block w-full text-right px-2 py-1.5 rounded-md text-[11px] sm:text-[10px] font-bold transition"
            :style="themeStore.fontScale === opt.id ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-primary)' }"
          >
            🔤 {{ opt.label }}
          </button>
        </div>
      </div>

      <div class="p-2.5 border-t border-white/10">
        <button @click="handleLogout" class="flex items-center gap-2 w-full px-3 py-2 rounded-lg transition bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold">
          <LogOut class="w-4 h-4" />
          <span>خروج از حساب</span>
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col min-w-0 h-[100dvh] overflow-hidden relative z-10">

      <header class="sticky top-0 z-30 backdrop-blur-2xl border-b border-white/10 shadow-xl shrink-0" :style="{ background: 'var(--header-bg)' }">
        <div class="flex items-center justify-between px-3 sm:px-4 md:px-6 py-2 sm:py-2 gap-1.5">

          <div class="flex items-center gap-1.5 shrink-0">
            <button
              type="button"
              @click.stop="sidebarOpen = !sidebarOpen"
              class="lg:hidden w-9 h-9 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition active:scale-95 text-purple-400 flex items-center justify-center"
              title="باز کردن منو"
            >
              <Menu class="w-4 h-4" />
            </button>

            <div class="flex items-center gap-1 px-2 py-1 rounded-lg sm:rounded-xl border border-white/10 bg-white/5 shadow-inner">
              <Calendar class="w-3.5 h-3.5 text-purple-400 shrink-0 hidden sm:block" />
              <div class="flex flex-col sm:flex-row sm:items-center sm:gap-1 text-right">
                <span class="text-[11px] sm:text-xs font-black text-purple-300 leading-tight" :style="{ color: themeStore.currentTheme === 'light-2026' ? '#6d28d9' : '' }">{{ dayOfWeek }}</span>
                <span class="text-[11px] sm:text-xs font-bold leading-tight sm:hidden" :style="{ color: 'var(--text-primary)' }">{{ persianDateShort }}</span>
                <span class="text-xs font-bold hidden sm:inline" :style="{ color: 'var(--text-primary)' }">، {{ persianDate }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-center shrink-0">
            <div class="seven-segment-chassis px-2.5 sm:px-3.5 py-1 rounded-lg sm:rounded-xl flex items-center justify-center border border-emerald-500/40">
              <span dir="ltr" class="seven-segment-glow text-sm sm:text-base md:text-xl font-black tracking-wider sm:tracking-widest select-none">
                {{ currentTimeEn }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-1.5 sm:gap-1.5 shrink-0">
            <div class="flex items-center px-2 py-1 sm:px-2.5 sm:py-1 rounded-lg sm:rounded-xl border border-white/10 bg-white/5 text-[11px] sm:text-xs font-bold shadow-inner" :style="{ color: 'var(--text-secondary)' }">
              <span dir="ltr" class="hidden sm:inline">{{ currentDate }}</span>
              <span dir="ltr" class="sm:hidden">{{ currentDateShort }}</span>
            </div>

            <router-link to="/profile" class="flex items-center gap-1.5 p-1 sm:pr-2 rounded-lg sm:rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition group">
              <div class="text-left hidden md:block">
                <p class="text-xs font-black group-hover:text-blue-400 transition" :style="{ color: 'var(--text-primary)' }">{{ authStore.user?.full_name || 'کاربر' }}</p>
                <p class="text-[10px] flex items-center gap-1 justify-end" :style="{ color: 'var(--text-secondary)' }">
                  <span class="w-1.5 h-1.5 rounded-full bg-green-500 inline-block animate-ping"></span> آنلاین
                </p>
              </div>

              <div class="relative">
                <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-md sm:rounded-lg flex items-center justify-center text-white font-black text-[11px] sm:text-xs shadow-md overflow-hidden border border-white/20"
                     :style="{ background: authStore.user?.avatar_url ? `url(${authStore.user.avatar_url}) center/cover` : 'linear-gradient(135deg, #8b5cf6, #3b82f6)' }">
                  {{ !authStore.user?.avatar_url ? (authStore.user?.full_name?.charAt(0) || 'U') : '' }}
                </div>
                <span class="w-1.5 h-1.5 rounded-full bg-green-500 border border-gray-900 absolute -bottom-0.5 -right-0.5"></span>
              </div>
            </router-link>
          </div>

        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 relative custom-scrollbar">
        <div v-if="themeStore.currentTheme === 'persian-classic'" class="absolute inset-0 persian-pattern opacity-30 pointer-events-none"></div>
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="absolute inset-0 pointer-events-none">
          <div class="scanline absolute inset-0"></div>
        </div>
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="particles pointer-events-none">
          <div v-for="(p, idx) in staticParticles" :key="idx" class="particle" :style="{ left: p.left, animationDelay: p.delay, animationDuration: p.duration }"></div>
        </div>
        <router-view />
      </div>
    </main>

    <Teleport to="body">
      <div v-if="showExpiredModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="w-full max-w-md rounded-3xl p-6 md:p-8 text-center shadow-2xl border border-yellow-500/30 glass-card">
          <div class="w-12 h-12 bg-yellow-500/20 text-yellow-400 rounded-2xl flex items-center justify-center mx-auto mb-3 border border-yellow-500/30">
            <Lock class="w-6 h-6 animate-bounce" />
          </div>
          <h3 class="text-lg font-black mb-2" :style="{ color: 'var(--text-primary)' }">انقضای جلسه کاری</h3>
          <div class="bg-yellow-500/10 border border-yellow-500/20 p-2.5 rounded-xl text-yellow-300 text-xs font-bold mb-4">
            ⚠️ پس از ۶۰ دقیقه عدم فعالیت، جهت حفظ امنیت مجدداً وارد شوید.
          </div>
          <form @submit.prevent="handleExpiredLogin" class="space-y-3 text-right">
            <div>
              <label class="block text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">ایمیل یا شماره موبایل</label>
              <input v-model="expiredEmail" type="text" required class="w-full px-3.5 py-2.5 border border-white/10 rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500 dir-ltr" :style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }" placeholder="you@example.com یا 0912..." />
            </div>
            <div>
              <label class="block text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">رمز عبور</label>
              <input v-model="expiredPassword" type="password" required class="w-full px-3.5 py-2.5 border border-white/10 rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500 dir-ltr" :style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }" placeholder="********" />
            </div>
            <div v-if="expiredLoginError" class="text-xs p-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-bold">
              {{ expiredLoginError }}
            </div>
            <button type="submit" :disabled="expiredLoginLoading" class="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 text-white font-black rounded-xl shadow-lg transition disabled:opacity-50 flex items-center justify-center gap-2">
              <KeyRound class="w-4 h-4" />
              <span v-if="!expiredLoginLoading">ورود مجدد</span>
              <span v-else>در حال بررسی...</span>
            </button>
          </form>
          <div class="mt-3 pt-3 border-t border-white/10 text-center">
            <button @click="confirmLogout" class="text-xs hover:text-white transition" :style="{ color: 'var(--text-secondary)' }">انصراف و خروج کامل</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showLogoutConfirm" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="w-full max-w-sm rounded-3xl p-5 text-center shadow-2xl border border-white/10 glass-card">
          <div class="text-3xl mb-2">🚪</div>
          <h3 class="text-base font-black mb-1.5" :style="{ color: 'var(--text-primary)' }">خروج از حساب</h3>
          <p class="text-xs mb-4" :style="{ color: 'var(--text-secondary)' }">آیا مطمئن هستید که می‌خواهید خارج شوید؟</p>
          <div class="flex gap-2.5">
            <button @click="confirmLogout" class="flex-1 py-2 rounded-xl text-white text-xs font-black bg-red-500 hover:bg-red-600 transition shadow-lg">بله، خارج می‌شم</button>
            <button @click="cancelLogout" class="flex-1 py-2 rounded-xl text-xs font-bold transition bg-white/10 hover:bg-white/20" :style="{ color: 'var(--text-secondary)' }">انصراف</button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<style scoped>
.seven-segment-chassis {
  background: radial-gradient(circle at 50% 50%, #032014 0%, #020617 100%);
  border: 1.5px solid rgba(34, 197, 94, 0.45);
  box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.95), 0 0 10px rgba(34, 197, 94, 0.2);
}

.seven-segment-glow {
  color: #4ade80;
  font-family: 'Consolas', 'Courier New', Courier, monospace;
  text-shadow: 0 0 2px rgba(74, 222, 128, 1), 0 0 6px rgba(34, 197, 94, 0.8), 0 0 12px rgba(34, 197, 94, 0.5), 0 0 20px rgba(16, 185, 129, 0.3);
}
</style>
