<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
<<<<<<< HEAD
import AnalogClock from '@/components/AnalogClock.vue'
=======
>>>>>>> main
import { 
  LayoutDashboard, ListTodo, Target, Wallet, Film, MapPin, BookOpen, Download,
  Menu, X, LogOut, Calendar, Clock, Palette, Lock, KeyRound, Lightbulb, Type, Sparkles,
  HeartPulse, Award
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
<<<<<<< HEAD
=======

>>>>>>> main
const sidebarOpen = ref(false)
const themeMenuOpen = ref(false)
const fontMenuOpen = ref(false)
const showLogoutConfirm = ref(false)
const currentTime = ref('')
<<<<<<< HEAD
const currentDate = ref('')
const persianDate = ref('')
const dayOfWeek = ref('')

// متغیرها و استیت‌های مربوط به انقضای ۵ دقیقه عدم فعالیت
=======
const currentTimeEn = ref('')
const currentDate = ref('')
const currentDateShort = ref('')
const persianDate = ref('')
const persianDateShort = ref('')
const dayOfWeek = ref('')

const isAuthPage = computed(() => {
  return ['/login', '/register', '/forgot-password'].includes(route.path)
})

// متغیرهای انقضای ۳۰ دقیقه عدم فعالیت
>>>>>>> main
const showExpiredModal = ref(false)
const expiredEmail = ref('')
const expiredPassword = ref('')
const expiredLoginLoading = ref(false)
const expiredLoginError = ref('')

<<<<<<< HEAD
// زمان عدم فعالیت: ۵ دقیقه (۳۰۰,۰۰۰ میلی‌ثانیه)
const INACTIVITY_LIMIT = 5 * 60 * 1000 
let inactivityTimer = null

=======
// ⏱️ افزایش زمان عدم فعالیت به ۳۰ دقیقه کامل (۱,۸۰۰,۰۰۰ میلی‌ثانیه)
const INACTIVITY_LIMIT = 30 * 60 * 1000 
let inactivityTimer = null

const staticParticles = [
  { left: '10%', delay: '0s', duration: '4s' },
  { left: '25%', delay: '1.5s', duration: '5s' },
  { left: '40%', delay: '0.8s', duration: '3.5s' },
  { left: '60%', delay: '2s', duration: '4.5s' },
  { left: '75%', delay: '1s', duration: '5.5s' },
  { left: '90%', delay: '2.5s', duration: '4s' },
]

>>>>>>> main
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
<<<<<<< HEAD
  currentTime.value = now.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDate.value = now.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })
  dayOfWeek.value = now.toLocaleDateString('fa-IR', { weekday: 'long' })
  persianDate.value = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { year: 'numeric', month: 'long', day: 'numeric' }).format(now)
}

// -------------------------------------------------------------
// موتور قدرتمند پایش فعالیت کاربر (با پشتیبانی کامل از تایپ فرم‌ها)
// -------------------------------------------------------------
const resetInactivityTimer = () => {
  if (!authStore.isAuthenticated) {
=======
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
>>>>>>> main
    if (inactivityTimer) clearTimeout(inactivityTimer)
    return
  }

  if (inactivityTimer) clearTimeout(inactivityTimer)

  inactivityTimer = setTimeout(() => {
    handleInactivityTimeout()
  }, INACTIVITY_LIMIT)
}

const handleInactivityTimeout = () => {
<<<<<<< HEAD
  if (authStore.isAuthenticated) {
    if (authStore.user?.email) {
      expiredEmail.value = authStore.user.email
=======
  if (authStore.isAuthenticated && !isAuthPage.value) {
    if (authStore.user?.email || authStore.user?.phone) {
      expiredEmail.value = authStore.user.email || authStore.user.phone
>>>>>>> main
    }
    authStore.expireSession()
    showExpiredModal.value = true
  }
}

<<<<<<< HEAD
// لیست کامل رویدادهای تایپ، فوکوس، کلیک، لمس و اسکرول
=======
>>>>>>> main
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
<<<<<<< HEAD
  if (newMsg) {
    if (authStore.user?.email) {
      expiredEmail.value = authStore.user.email
=======
  if (newMsg && !isAuthPage.value) {
    if (authStore.user?.email || authStore.user?.phone) {
      expiredEmail.value = authStore.user.email || authStore.user.phone
>>>>>>> main
    }
    showExpiredModal.value = true
  }
})

const handleExpiredLogin = async () => {
  try {
    expiredLoginLoading.value = true
    expiredLoginError.value = ''
    
    if (!expiredEmail.value.trim() || !expiredPassword.value.trim()) {
<<<<<<< HEAD
      expiredLoginError.value = '⚠️ لطفاً ایمیل و رمز عبور را وارد کنید'
=======
      expiredLoginError.value = '⚠️ لطفاً ایمیل یا شماره موبایل و رمز عبور را وارد کنید'
>>>>>>> main
      return
    }

    await authStore.login(expiredEmail.value, expiredPassword.value)
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
<<<<<<< HEAD
=======
  sidebarOpen.value = false
>>>>>>> main
  router.push('/login')
}

const cancelLogout = () => {
  showLogoutConfirm.value = false
}
</script>

<template>
<<<<<<< HEAD
  <div class="flex h-screen relative" :class="[themeStore.currentTheme]">
    <!-- Mobile overlay -->
    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/50 z-40 lg:hidden"></div>

    <!-- Sidebar -->
    <aside 
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      class="fixed lg:static inset-y-0 right-0 w-64 z-50 transition-transform duration-300 lg:translate-x-0 flex flex-col glass-card"
      :style="{ borderLeft: '1px solid var(--border)', borderRadius: '0px' }"
    >
      <!-- Logo -->
      <div class="p-6 border-b" :style="{ borderColor: 'var(--border)' }">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
            <span class="text-white font-bold text-lg">P</span>
          </div>
          <div>
            <h1 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">پلنر شخصی</h1>
            <p class="text-xs" :style="{ color: 'var(--text-secondary)' }">مدیریت هوشمند</p>
          </div>
        </div>
      </div>

      <!-- Menu -->
      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
=======
  <div v-if="isAuthPage" class="min-h-[100dvh] w-full bg-slate-950 text-right" dir="rtl">
    <router-view />
  </div>

  <div v-else class="flex h-[100dvh] w-full overflow-hidden relative text-right bg-slate-950" dir="rtl" :class="[themeStore.currentTheme]">
    
    <div 
      v-if="sidebarOpen" 
      @click="sidebarOpen = false" 
      class="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
    ></div>

    <aside 
      class="fixed lg:static inset-y-0 right-0 w-64 z-50 transition-transform duration-300 ease-in-out flex flex-col bg-slate-900 border-l border-white/10 shadow-2xl lg:shadow-none"
      :class="sidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'"
    >
      <div class="p-4 border-b border-white/10 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
            <span class="text-white font-black text-base">P</span>
          </div>
          <div>
            <h1 class="text-sm font-black text-white">پلنر شخصی</h1>
            <p class="text-[10px] font-bold text-gray-400">مدیریت هوشمند اهداف</p>
          </div>
        </div>

        <button @click="sidebarOpen = false" class="lg:hidden p-1.5 text-gray-400 hover:text-white rounded-lg bg-white/5">
          <X class="w-4 h-4" />
        </button>
      </div>

      <nav class="flex-1 p-2.5 space-y-1 overflow-y-auto custom-scrollbar">
>>>>>>> main
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          @click="sidebarOpen = false"
<<<<<<< HEAD
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
          :style="route.path === item.path ? { background: 'var(--accent)', color: '#fff', boxShadow: '0 0 15px var(--glow)' } : { color: 'var(--text-secondary)' }"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="font-medium">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- Theme & Font Size Selector -->
      <div class="p-4 border-t space-y-2" :style="{ borderColor: 'var(--border)' }">
        
        <!-- انتخاب تم -->
        <button 
          @click="themeMenuOpen = !themeMenuOpen; fontMenuOpen = false"
          class="flex items-center gap-2 w-full px-4 py-2.5 rounded-xl transition"
          :style="{ color: 'var(--text-secondary)' }"
        >
          <Palette class="w-5 h-5" />
          <span class="font-medium">تغییر تم</span>
        </button>

        <div v-if="themeMenuOpen" class="space-y-1 rounded-xl p-2 border" :style="{ background: 'var(--bg-hover)', borderColor: 'var(--border)' }">
=======
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
          class="flex items-center gap-2 w-full px-3 py-1.5 rounded-lg transition text-[11px] font-bold bg-white/5 text-gray-300 hover:bg-white/10"
        >
          <Palette class="w-3.5 h-3.5 text-purple-400" />
          <span>تغییر تم</span>
        </button>

        <div v-if="themeMenuOpen" class="space-y-1 rounded-xl p-1.5 bg-slate-950 border border-white/10">
>>>>>>> main
          <button 
            v-for="theme in themeStore.themes" 
            :key="theme.id"
            @click="themeStore.setTheme(theme.id); themeMenuOpen = false"
<<<<<<< HEAD
            class="block w-full text-right px-3 py-2 rounded-lg text-xs font-bold transition"
=======
            class="block w-full text-right px-2 py-1 rounded-md text-[10px] font-bold transition"
>>>>>>> main
            :style="themeStore.currentTheme === theme.id ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-primary)' }"
          >
            {{ theme.icon }} {{ theme.label }}
          </button>
        </div>

<<<<<<< HEAD
        <!-- 🔤 انتخاب سایز فونت کل برنامه -->
        <button 
          @click="fontMenuOpen = !fontMenuOpen; themeMenuOpen = false"
          class="flex items-center gap-2 w-full px-4 py-2.5 rounded-xl transition"
          :style="{ color: 'var(--text-secondary)' }"
        >
          <Type class="w-5 h-5" />
          <span class="font-medium">اندازه فونت برنامه</span>
        </button>

        <div v-if="fontMenuOpen" class="space-y-1 rounded-xl p-2 border" :style="{ background: 'var(--bg-hover)', borderColor: 'var(--border)' }">
=======
        <button 
          @click="fontMenuOpen = !fontMenuOpen; themeMenuOpen = false"
          class="flex items-center gap-2 w-full px-3 py-1.5 rounded-lg transition text-[11px] font-bold bg-white/5 text-gray-300 hover:bg-white/10"
        >
          <Type class="w-3.5 h-3.5 text-blue-400" />
          <span>اندازه قلم</span>
        </button>

        <div v-if="fontMenuOpen" class="space-y-1 rounded-xl p-1.5 bg-slate-950 border border-white/10">
>>>>>>> main
          <button 
            v-for="opt in themeStore.fontScaleOptions" 
            :key="opt.id"
            @click="themeStore.setFontScale(opt.id); fontMenuOpen = false"
<<<<<<< HEAD
            class="block w-full text-right px-3 py-2 rounded-lg text-xs font-bold transition"
=======
            class="block w-full text-right px-2 py-1 rounded-md text-[10px] font-bold transition"
>>>>>>> main
            :style="themeStore.fontScale === opt.id ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-primary)' }"
          >
            🔤 {{ opt.label }}
          </button>
        </div>
<<<<<<< HEAD

      </div>

      <!-- Footer -->
      <div class="p-4 border-t" :style="{ borderColor: 'var(--border)' }">
        <button @click="handleLogout" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }">
          <LogOut class="w-5 h-5" />
          <span class="font-medium">خروج</span>
=======
      </div>

      <div class="p-2.5 border-t border-white/10">
        <button @click="handleLogout" class="flex items-center gap-2 w-full px-3 py-1.5 rounded-lg transition bg-red-500/10 hover:bg-red-500/20 text-red-400 text-[11px] font-bold">
          <LogOut class="w-3.5 h-3.5" />
          <span>خروج از حساب</span>
>>>>>>> main
        </button>
      </div>
    </aside>

<<<<<<< HEAD
    <!-- Main Content -->
    <main class="flex-1 overflow-auto relative z-10" style="background: transparent;">
      
      <!-- هدر جدید، شکیل و کپسولی -->
       <header class="sticky top-0 z-30 backdrop-blur-xl border-b shadow-lg transition-all" 
              :style="{ background: 'var(--header-bg)', borderColor: 'var(--border)' }">
        <div class="flex items-center justify-between px-6 py-3.5">
          
          <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden p-2 hover:bg-white/5 rounded-xl transition" :style="{ color: 'var(--text-primary)' }">
            <Menu v-if="!sidebarOpen" class="w-7 h-7" /><X v-else class="w-7 h-7" />
          </button>

          <div class="flex items-center gap-4 md:gap-6">
            <AnalogClock />

            <div class="hidden md:flex items-center gap-2.5 px-4 py-2 rounded-2xl border bg-white/5 backdrop-blur-md text-sm md:text-base font-black shadow-inner"
                 :style="{ borderColor: 'var(--border)', color: 'var(--text-primary)' }">
              <Calendar class="w-5 h-5 text-purple-400" />
              <span>{{ dayOfWeek }} {{ persianDate }}</span>
            </div>

            <div class="hidden lg:flex items-center gap-2.5 px-4 py-2 rounded-2xl border bg-white/5 backdrop-blur-md text-xs md:text-sm font-bold opacity-80"
                 :style="{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }">
              <span>{{ currentDate }}</span>
            </div>

            <div class="flex items-center gap-2.5 px-5 py-2 rounded-2xl border bg-blue-500/10 backdrop-blur-md text-xl md:text-2xl font-black shadow-xl"
                 :style="{ borderColor: 'rgba(59, 130, 246, 0.4)', color: 'var(--accent)' }">
              <Clock class="w-6 h-6 text-blue-400 animate-pulse" />
              <span dir="ltr" class="font-mono tracking-widest">{{ currentTime }}</span>
            </div>
          </div>

          <router-link to="/profile" class="flex items-center gap-3.5 p-2 pr-4 rounded-2xl border bg-white/5 hover:bg-white/10 transition backdrop-blur-md group"
                       :style="{ borderColor: 'var(--border)' }">
            <div class="text-left hidden md:block">
              <p class="text-sm md:text-base font-black group-hover:text-blue-400 transition" :style="{ color: 'var(--text-primary)' }">{{ authStore.user?.full_name || 'کاربر گرامی' }}</p>
              <p class="text-xs opacity-70 flex items-center gap-1.5 justify-end" :style="{ color: 'var(--text-secondary)' }">
                <span class="w-2 h-2 rounded-full bg-green-500 inline-block animate-ping"></span> آنلاین
              </p>
            </div>
            
            <div class="relative">
              <div class="w-11 h-11 rounded-2xl flex items-center justify-center text-white font-black text-lg shadow-md overflow-hidden border-2 border-white/20"
                   :style="{ background: authStore.user?.avatar_url ? `url(${authStore.user.avatar_url}) center/cover` : 'linear-gradient(135deg, #8b5cf6, #3b82f6)' }">
                {{ !authStore.user?.avatar_url ? (authStore.user?.full_name?.charAt(0) || 'U') : '' }}
              </div>
              <span class="w-3 h-3 rounded-full bg-green-500 border-2 border-gray-900 absolute -bottom-0.5 -right-0.5"></span>
            </div>
          </router-link>
=======
    <main class="flex-1 flex flex-col min-w-0 h-[100dvh] overflow-hidden relative z-10 bg-slate-950">
      
      <!-- هدر ریسپانسیو و متقارن -->
      <header class="sticky top-0 z-30 bg-slate-900/95 backdrop-blur-2xl border-b border-white/10 shadow-xl shrink-0">
        <div class="flex items-center justify-between px-2 sm:px-4 md:px-6 py-1.5 sm:py-2 gap-1">
          
          <!-- ۱. راست: دکمه منو + روز و تاریخ شمسی -->
          <div class="flex items-center gap-1.5 shrink-0">
            <button 
              type="button"
              @click.stop="sidebarOpen = !sidebarOpen" 
              class="lg:hidden w-8 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition active:scale-95 text-purple-400 flex items-center justify-center" 
              title="باز کردن منو"
            >
              <Menu class="w-4 h-4" />
            </button>

            <div class="flex items-center gap-1 px-2 py-1 rounded-lg sm:rounded-xl border border-white/10 bg-white/5 shadow-inner">
              <Calendar class="w-3 h-3 text-purple-400 shrink-0 hidden sm:block" />
              <div class="flex flex-col sm:flex-row sm:items-center sm:gap-1 text-right">
                <span class="text-[9px] sm:text-xs font-black text-purple-300 leading-tight">{{ dayOfWeek }}</span>
                <span class="text-[9px] sm:text-xs font-bold text-white leading-tight sm:hidden">{{ persianDateShort }}</span>
                <span class="text-xs font-bold text-white hidden sm:inline">، {{ persianDate }}</span>
              </div>
            </div>
          </div>

          <!-- ۲. مرکز: ساعت دیجیتال سون‌سگمنت نئونی سبز -->
          <div class="flex items-center justify-center shrink-0">
            <div class="seven-segment-chassis px-2 sm:px-3.5 py-1 rounded-lg sm:rounded-xl flex items-center justify-center border border-emerald-500/40">
              <span dir="ltr" class="seven-segment-glow text-xs sm:text-base md:text-xl font-black tracking-wider sm:tracking-widest select-none">
                {{ currentTimeEn }}
              </span>
            </div>
          </div>

          <!-- ۳. چپ: تاریخ میلادی (فعال در موبایل) + پروفایل -->
          <div class="flex items-center gap-1 sm:gap-1.5 shrink-0">
            <div class="flex items-center px-1.5 py-1 sm:px-2.5 sm:py-1 rounded-lg sm:rounded-xl border border-white/10 bg-white/5 text-[9px] sm:text-xs font-bold text-gray-300 shadow-inner">
              <span dir="ltr" class="hidden sm:inline">{{ currentDate }}</span>
              <span dir="ltr" class="sm:hidden">{{ currentDateShort }}</span>
            </div>

            <router-link to="/profile" class="flex items-center gap-1.5 p-1 sm:pr-2 rounded-lg sm:rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition group">
              <div class="text-left hidden md:block">
                <p class="text-xs font-black text-white group-hover:text-blue-400 transition">{{ authStore.user?.full_name || 'کاربر' }}</p>
                <p class="text-[9px] text-gray-400 flex items-center gap-1 justify-end">
                  <span class="w-1.5 h-1.5 rounded-full bg-green-500 inline-block animate-ping"></span> آنلاین
                </p>
              </div>
              
              <div class="relative">
                <div class="w-6 h-6 sm:w-8 sm:h-8 rounded-md sm:rounded-lg flex items-center justify-center text-white font-black text-[10px] sm:text-xs shadow-md overflow-hidden border border-white/20"
                     :style="{ background: authStore.user?.avatar_url ? `url(${authStore.user.avatar_url}) center/cover` : 'linear-gradient(135deg, #8b5cf6, #3b82f6)' }">
                  {{ !authStore.user?.avatar_url ? (authStore.user?.full_name?.charAt(0) || 'U') : '' }}
                </div>
                <span class="w-1.5 h-1.5 rounded-full bg-green-500 border border-gray-900 absolute -bottom-0.5 -right-0.5"></span>
              </div>
            </router-link>
          </div>
>>>>>>> main

        </div>
      </header>

<<<<<<< HEAD
      <!-- Page Content -->
      <div class="fade-in relative p-6" :style="{ minHeight: 'calc(100vh - 60px)' }">
=======
      <div class="flex-1 overflow-y-auto p-2.5 sm:p-4 md:p-6 relative custom-scrollbar">
>>>>>>> main
        <div v-if="themeStore.currentTheme === 'persian-classic'" class="absolute inset-0 persian-pattern opacity-30 pointer-events-none"></div>
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="absolute inset-0 pointer-events-none">
          <div class="scanline absolute inset-0"></div>
        </div>
<<<<<<< HEAD
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="particles">
          <div v-for="i in 20" :key="i" class="particle" :style="{ left: Math.random() * 100 + '%', animationDelay: Math.random() * 4 + 's', animationDuration: (Math.random() * 3 + 3) + 's' }"></div>
=======
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="particles pointer-events-none">
          <div v-for="(p, idx) in staticParticles" :key="idx" class="particle" :style="{ left: p.left, animationDelay: p.delay, animationDuration: p.duration }"></div>
>>>>>>> main
        </div>
        <router-view />
      </div>
    </main>

<<<<<<< HEAD
    <!-- کادر اتوماتیک ورود به سایت پس از ۵ دقیقه انقضا -->
    <div v-if="showExpiredModal" class="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div class="w-full max-w-md rounded-3xl p-8 text-center shadow-2xl border bg-slate-900 border-yellow-500/30 animate-in fade-in zoom-in duration-300">
        <div class="w-16 h-16 bg-yellow-500/20 text-yellow-400 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-yellow-500/30">
          <Lock class="w-8 h-8 animate-bounce" />
        </div>
        
        <h3 class="text-2xl font-black text-white mb-2">انقضای کلمه عبور</h3>
        
        <div class="bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-2xl text-yellow-300 text-sm font-bold mb-6">
          ⚠️ با توجه به منقضی شدن کلمه عبور مجددا وارد شوید.
        </div>

        <form @submit.prevent="handleExpiredLogin" class="space-y-4 text-right">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">ایمیل</label>
            <input 
              v-model="expiredEmail"
              type="email" 
              required
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none transition"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">رمز عبور</label>
            <input 
              v-model="expiredPassword"
              type="password" 
              required
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none transition"
              placeholder="********"
            />
          </div>

          <div v-if="expiredLoginError" class="text-xs p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-bold">
            {{ expiredLoginError }}
          </div>

          <button 
            type="submit" 
            :disabled="expiredLoginLoading"
            class="w-full py-3.5 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-black rounded-xl shadow-lg transition duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <KeyRound class="w-5 h-5" />
            <span v-if="!expiredLoginLoading">ورود مجدد</span>
            <span v-else>در حال بررسی...</span>
          </button>
        </form>

        <div class="mt-4 pt-4 border-t border-white/10 text-center">
          <button @click="confirmLogout" class="text-xs text-gray-400 hover:text-white transition">
            انصراف و خروج کامل از حساب
          </button>
        </div>
      </div>
    </div>

    <!-- مودال تأیید خروج دستی -->
    <div v-if="showLogoutConfirm" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="w-full max-w-sm rounded-3xl p-6 text-center shadow-2xl border" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        <div class="text-5xl mb-4">🚪</div>
        <h3 class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">خروج از حساب</h3>
        <p class="text-sm mb-6" :style="{ color: 'var(--text-secondary)' }">آیا مطمئن هستید که می‌خواهید خارج شوید؟</p>
        <div class="flex gap-3">
          <button @click="confirmLogout" class="flex-1 py-2.5 rounded-2xl text-white font-bold bg-red-500 hover:bg-red-600 transition shadow-lg shadow-red-500/20">بله، خارج می‌شم</button>
          <button @click="cancelLogout" class="flex-1 py-2.5 rounded-2xl font-semibold transition bg-white/10 hover:bg-white/20" :style="{ color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>
=======
    <!-- مودال انقضای نشست ۳۰ دقیقه‌ای -->
    <Teleport to="body">
      <div v-if="showExpiredModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="w-full max-w-md rounded-3xl p-6 md:p-8 text-center shadow-2xl border bg-slate-900 border-yellow-500/30 animate-in fade-in zoom-in duration-300">
          <div class="w-12 h-12 bg-yellow-500/20 text-yellow-400 rounded-2xl flex items-center justify-center mx-auto mb-3 border border-yellow-500/30">
            <Lock class="w-6 h-6 animate-bounce" />
          </div>
          <h3 class="text-lg font-black text-white mb-2">انقضای جلسه کاری</h3>
          <div class="bg-yellow-500/10 border border-yellow-500/20 p-2.5 rounded-xl text-yellow-300 text-xs font-bold mb-4">
            ⚠️ پس از ۳۰ دقیقه عدم فعالیت، جهت حفظ امنیت مجدداً وارد شوید.
          </div>
          <form @submit.prevent="handleExpiredLogin" class="space-y-3 text-right">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">ایمیل یا شماره موبایل</label>
              <input v-model="expiredEmail" type="text" required class="w-full px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500 dir-ltr" placeholder="you@example.com یا 0912..." />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">رمز عبور</label>
              <input v-model="expiredPassword" type="password" required class="w-full px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500 dir-ltr" placeholder="********" />
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
            <button @click="confirmLogout" class="text-xs text-gray-400 hover:text-white transition">انصراف و خروج کامل</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- مودال خروج -->
    <Teleport to="body">
      <div v-if="showLogoutConfirm" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="w-full max-w-sm rounded-3xl p-5 text-center shadow-2xl border bg-slate-900 border-white/10">
          <div class="text-3xl mb-2">🚪</div>
          <h3 class="text-base font-black text-white mb-1.5">خروج از حساب</h3>
          <p class="text-xs text-gray-400 mb-4">آیا مطمئن هستید که می‌خواهید خارج شوید؟</p>
          <div class="flex gap-2.5">
            <button @click="confirmLogout" class="flex-1 py-2 rounded-xl text-white text-xs font-black bg-red-500 hover:bg-red-600 transition shadow-lg">بله، خارج می‌شم</button>
            <button @click="cancelLogout" class="flex-1 py-2 rounded-xl text-xs font-bold transition bg-white/10 hover:bg-white/20 text-gray-300">انصراف</button>
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
>>>>>>> main
