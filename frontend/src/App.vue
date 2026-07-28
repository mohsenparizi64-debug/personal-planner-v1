<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import AnalogClock from '@/components/AnalogClock.vue'
import { 
  LayoutDashboard, ListTodo, Target, Wallet, Film, MapPin, BookOpen, Download,
  Menu, X, LogOut, Calendar, Clock, Palette 
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const sidebarOpen = ref(false)
const themeMenuOpen = ref(false)
const showLogoutConfirm = ref(false)
const currentTime = ref('')
const currentDate = ref('')
const persianDate = ref('')
const dayOfWeek = ref('')

const menuItems = [
  { path: '/', label: 'داشبورد', icon: LayoutDashboard },
  { path: '/tasks', label: 'تسک‌ها', icon: ListTodo },
  { path: '/goals', label: 'اهداف', icon: Target },
  { path: '/roadmap', label: 'نقشه راه', icon: MapPin },
  { path: '/finance', label: 'مالی', icon: Wallet },
  { path: '/movies', label: 'فیلم‌ها', icon: Film },
  { path: '/books', label: 'کتاب‌ها', icon: BookOpen },
  { path: '/places', label: 'مکان‌ها', icon: MapPin },
  { path: '/backup', label: 'بکاپ', icon: Download },
]

function updateDateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDate.value = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
  dayOfWeek.value = now.toLocaleDateString('fa-IR', { weekday: 'long' })
  persianDate.value = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { year: 'numeric', month: 'long', day: 'numeric' }).format(now)
}

let timer = null
onMounted(() => {
  updateDateTime()
  timer = setInterval(updateDateTime, 1000)
  if (authStore.isAuthenticated) {
    authStore.fetchUser()
  }
})
onUnmounted(() => clearInterval(timer))

const handleLogout = () => {
  showLogoutConfirm.value = true
}

const confirmLogout = () => {
  authStore.logout()
  showLogoutConfirm.value = false
  router.push('/login')
}

const cancelLogout = () => {
  showLogoutConfirm.value = false
}
</script>

<template>
  <div class="flex h-screen" :class="[themeStore.currentTheme]">
    <!-- Mobile overlay -->
    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/50 z-40 lg:hidden"></div>

    <!-- Sidebar -->
    <aside 
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      class="fixed lg:static inset-y-0 right-0 w-64 z-50 transition-transform duration-300 lg:translate-x-0 flex flex-col"
      :style="{ background: 'var(--bg-card)', borderLeft: '1px solid var(--border)' }"
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
      <nav class="flex-1 p-4 space-y-1">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          @click="sidebarOpen = false"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
          :style="route.path === item.path ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-secondary)' }"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="font-medium">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- Theme Selector -->
      <div class="p-4 border-t" :style="{ borderColor: 'var(--border)' }">
        <button 
          @click="themeMenuOpen = !themeMenuOpen"
          class="flex items-center gap-2 w-full px-4 py-3 rounded-xl transition"
          :style="{ color: 'var(--text-secondary)' }"
        >
          <Palette class="w-5 h-5" />
          <span class="font-medium">تغییر تم</span>
        </button>
        <div v-if="themeMenuOpen" class="mt-2 space-y-1 rounded-xl p-2" :style="{ background: 'var(--bg-hover)' }">
          <button 
            v-for="theme in themeStore.themes" 
            :key="theme.id"
            @click="themeStore.setTheme(theme.id); themeMenuOpen = false"
            class="block w-full text-right px-3 py-2 rounded-lg text-sm transition"
            :style="themeStore.currentTheme === theme.id ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-primary)' }"
          >
            {{ theme.icon }} {{ theme.label }}
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t" :style="{ borderColor: 'var(--border)' }">
        <button @click="handleLogout" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }">
          <LogOut class="w-5 h-5" />
          <span class="font-medium">خروج</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto" style="background: var(--bg-primary)">
      
      <!-- Header Bar -->
      <header class="sticky top-0 z-30 backdrop-blur-lg border-b" :style="{ background: 'var(--header-bg)', borderColor: 'var(--border)' }">
        <div class="flex items-center justify-between px-6 py-3">
          <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden p-2 hover:bg-white/5 rounded-lg transition" :style="{ color: 'var(--text-primary)' }">
            <Menu v-if="!sidebarOpen" class="w-6 h-6" /><X v-else class="w-6 h-6" />
          </button>

          <div class="flex items-center gap-4 md:gap-8">
            <AnalogClock />
            <div class="hidden md:flex items-center gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
              <Calendar class="w-4 h-4" /><span>{{ dayOfWeek }} - {{ persianDate }}</span>
            </div>
            <div class="hidden lg:flex items-center gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
              <Calendar class="w-4 h-4" /><span>{{ currentDate }}</span>
            </div>
            <div class="flex items-center gap-2 font-bold text-lg" :style="{ color: 'var(--accent)' }">
              <Clock class="w-5 h-5" /><span>{{ currentTime }}</span>
            </div>
          </div>

          <router-link to="/profile" class="flex items-center gap-3 hover:opacity-80 transition">
            <div class="text-left hidden md:block">
              <p class="text-sm font-bold" :style="{ color: 'var(--text-primary)' }">{{ authStore.user?.full_name || 'کاربر' }} 👋</p>
              <p class="text-xs" :style="{ color: 'var(--text-secondary)' }">خوش آمدی!</p>
            </div>
            <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg"
                 :style="{ background: authStore.user?.avatar_url ? `url(${authStore.user.avatar_url}) center/cover` : 'linear-gradient(135deg, #8b5cf6, #3b82f6)' }">
              {{ !authStore.user?.avatar_url ? (authStore.user?.full_name?.charAt(0) || 'U') : '' }}
            </div>
          </router-link>
        </div>
      </header>

      <!-- Page Content -->
      <div class="fade-in relative" :style="{ minHeight: 'calc(100vh - 60px)' }">
        <div v-if="themeStore.currentTheme === 'persian-classic'" class="absolute inset-0 persian-pattern opacity-30 pointer-events-none"></div>
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="absolute inset-0 pointer-events-none">
          <div class="scanline absolute inset-0"></div>
        </div>
        <div v-if="themeStore.currentTheme === 'cyber-digital'" class="particles">
          <div v-for="i in 20" :key="i" class="particle" :style="{ left: Math.random() * 100 + '%', animationDelay: Math.random() * 4 + 's', animationDuration: (Math.random() * 3 + 3) + 's' }"></div>
        </div>
        <router-view />
      </div>
    </main>

    <!-- مودال تأیید خروج -->
    <div v-if="showLogoutConfirm" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="w-full max-w-sm rounded-2xl p-6 text-center" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="text-5xl mb-4">🚪</div>
        <h3 class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">خروج از حساب</h3>
        <p class="text-sm mb-6" :style="{ color: 'var(--text-secondary)' }">آیا مطمئن هستید که می‌خواهید خارج شوید؟</p>
        <div class="flex gap-3">
          <button @click="confirmLogout" class="flex-1 py-2.5 rounded-xl text-white font-semibold bg-red-500 hover:bg-red-600 transition">بله، خارج می‌شم</button>
          <button @click="cancelLogout" class="flex-1 py-2.5 rounded-xl font-semibold transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>