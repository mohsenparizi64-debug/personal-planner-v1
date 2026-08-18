<script setup>
import { ref, computed, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import { useRouter } from 'vue-router'
import { 
  ListTodo, CheckCircle, Flame, TrendingUp, Zap, AlertTriangle, 
  Wallet, Lightbulb, Target, Calendar, Plus, RefreshCw, ArrowRight, Clock, Star,
  BarChart2, PieChart, Film, BookOpen, MapPin, Scale, X, Edit3, ShieldAlert
} from 'lucide-vue-next'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const router = useRouter()

const isLoading = ref(true)
const dashboardData = ref(null)
const quickTaskTitle = ref('')

// حالت هاب تحلیلی برج دیده‌بانی
const isAnalyticsView = ref(false)
const selectedPeriodDays = ref(7) // 7, 30, 90, 180, 365
const analyticsData = ref(null)
const analyticsLoading = ref(false)

// مودال مدیریت امنیتی تسک‌های امروز
const showTaskModal = ref(false)
const selectedTaskForModal = ref(null)

const quotes = [
  "بهترین زمان برای کاشت یک درخت ۲۰ سال پیش بود، دومین زمان خوب همین الان است.",
  "موفقیت مجموعه‌ای از تلاش‌های کوچک است که هر روز تکرار می‌شوند.",
  "تمرکز یعنی گفتن «نه» به ۱۰۰ ایده خوب دیگر.",
  "انضباط شخصی یعنی انجام آنچه باید انجام شود، حتی زمانی که حوصله‌اش را ندارید."
]
const todayQuote = ref(quotes[Math.floor(Math.random() * quotes.length)])

const greetingMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) return 'صبح به خیر! ☀️'
  if (hour >= 12 && hour < 18) return 'عصر به خیر! 🌤️'
  return 'شب به خیر! 🌙'
})

const fetchDashboard = async () => {
  try {
    isLoading.value = true
    const response = await api.get('/dashboard/overview')
    dashboardData.value = response.data
  } catch (error) {
    console.error('خطا در دریافت اطلاعات برج دیده‌بانی:', error)
  } finally {
    isLoading.value = false
  }
}

// دریافت داده‌های هاب تحلیلی با فیلتر بازه زمانی (۷ تا ۳۶۵ روز)
const fetchAnalytics = async (days = 7) => {
  selectedPeriodDays.value = days
  try {
    analyticsLoading.value = true
    const res = await api.get(`/dashboard/analytics?days=${days}`)
    analyticsData.value = res.data
  } catch (e) {
    console.error('خطا در دریافت هاب تحلیلی:', e)
  } finally {
    analyticsLoading.value = false
  }
}

const toggleAnalyticsView = () => {
  isAnalyticsView.value = !isAnalyticsView.value
  if (isAnalyticsView.value) {
    fetchAnalytics(selectedPeriodDays.value)
  }
}

// مدیریت امنیتی کلیک روی تسک‌های امروز
const openTaskModal = (task) => {
  selectedTaskForModal.value = { ...task }
  showTaskModal.value = true
}

const confirmToggleTask = async () => {
  if (!selectedTaskForModal.value) return
  try {
    const today = new Date().toISOString().split('T')[0]
    const updatedStatus = !selectedTaskForModal.value.is_completed
    await api.put(`/tasks/${selectedTaskForModal.value.id}`, {
      ...selectedTaskForModal.value,
      is_completed: updatedStatus,
      last_action_date: updatedStatus ? today : null
    })
    showTaskModal.value = false
    fetchDashboard()
  } catch (e) {
    alert('خطا در بروزرسانی وضعیت تسک')
  }
}

const extendToToday = async (task) => {
  try {
    const today = new Date().toISOString().split('T')[0]
    await api.put(`/tasks/${task.id}`, {
      ...task,
      due_date: today
    })
    fetchDashboard()
  } catch (e) {
    alert('خطا در تمدید مهلت تسک')
  }
}

const addQuickTask = async () => {
  if (!quickTaskTitle.value.trim()) return
  try {
    const today = new Date().toISOString().split('T')[0]
    await api.post('/tasks', {
      title: quickTaskTitle.value,
      register_date: today,
      due_date: today,
      status: 'not_started',
      priority: 0
    })
    quickTaskTitle.value = ''
    fetchDashboard()
  } catch (e) {
    alert('خطا در ثبت تسک سریع')
  }
}

// محاسبه حداکثر واقعی هفته برای اسکیل دقیق ۱۰۰٪
const maxWeeklyValue = computed(() => {
  if (!dashboardData.value?.weekly_activity) return 1
  const maxComp = Math.max(...dashboardData.value.weekly_activity.map(d => d.completed), 0)
  return maxComp > 0 ? maxComp : 1
})

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
    
    <!-- هدر برج دیده‌بانی -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 rounded-3xl border border-white/10 shadow-2xl">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg shadow-purple-500/30">
            <Zap class="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 class="text-2xl md:text-3xl font-black" :style="{ color: 'var(--text-primary)' }">{{ greetingMessage }}</h1>
            <p class="text-xs md:text-sm mt-1" :style="{ color: 'var(--text-secondary)' }">برج دیده‌بانی و اتاق فرمان برنامه‌ریزی شخصی شما</p>
          </div>
        </div>
      </div>

      <!-- کادر انگیزشی -->
      <div class="max-w-md bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-md">
        <p class="text-xs text-amber-400 font-bold mb-1 flex items-center gap-1">
          <Star class="w-3.5 h-3.5 fill-amber-400" /> الهام‌بخش روز:
        </p>
        <p class="text-xs leading-relaxed italic" :style="{ color: 'var(--text-primary)' }">« {{ todayQuote }} »</p>
      </div>
    </div>

    <!-- 📊 نمای ۱: هاب تحلیلی گرافی برج دیده‌بانی -->
    <div v-if="isAnalyticsView" class="space-y-6 animate-in fade-in duration-300">
      
      <div class="glass-card p-4 rounded-2xl border border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4">
        <div class="flex items-center gap-3">
          <button @click="toggleAnalyticsView" class="p-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition"><ArrowRight class="w-5 h-5" /></button>
          <h2 class="text-lg font-black text-white flex items-center gap-2"><BarChart2 class="w-6 h-6 text-purple-400" /> هاب تحلیلی تمام ماژول‌های سیستم</h2>
        </div>

        <!-- انتخابگر بازه زمانی ۱ هفته تا ۱ سال -->
        <div class="flex items-center gap-1.5 p-1 bg-white/5 rounded-xl border border-white/10">
          <button @click="fetchAnalytics(7)" :class="selectedPeriodDays === 7 ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition">۱ هفته</button>
          <button @click="fetchAnalytics(30)" :class="selectedPeriodDays === 30 ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition">۱ ماه</button>
          <button @click="fetchAnalytics(90)" :class="selectedPeriodDays === 90 ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition">۳ ماه</button>
          <button @click="fetchAnalytics(180)" :class="selectedPeriodDays === 180 ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition">۶ ماه</button>
          <button @click="fetchAnalytics(365)" :class="selectedPeriodDays === 365 ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-white'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition">۱ سال</button>
        </div>
      </div>

      <div v-if="analyticsLoading" class="text-center py-20 text-purple-400 font-bold">
        <RefreshCw class="w-10 h-10 animate-spin mx-auto mb-2" />
        در حال تحلیل و استخراج نمودارهای بازه {{ selectedPeriodDays }} روزه...
      </div>

      <div v-else-if="analyticsData" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        <div class="glass-card p-6 rounded-3xl border border-white/10 space-y-4">
          <h3 class="text-base font-black text-white flex items-center gap-2"><Target class="w-5 h-5 text-purple-400" /> پیشرفت اهداف کلان در {{ selectedPeriodDays }} روز گذشته</h3>
          <div class="space-y-3">
            <div v-for="g in analyticsData.goal_analytics" :key="g.goal_id" class="p-3 bg-white/5 rounded-2xl border border-white/5 space-y-1">
              <div class="flex justify-between text-xs font-bold"><span class="text-white">{{ g.title }}</span><span class="text-purple-400">{{ g.completed_tasks }} تسک</span></div>
              <div class="w-full h-2 bg-black/30 rounded-full overflow-hidden"><div class="h-full bg-purple-500" :style="{ width: Math.min(100, (g.completed_tasks / (g.total_tasks || 1)) * 100) + '%' }"></div></div>
            </div>
          </div>
        </div>

        <div class="glass-card p-6 rounded-3xl border border-white/10 space-y-4">
          <h3 class="text-base font-black text-white flex items-center gap-2"><Wallet class="w-5 h-5 text-emerald-400" /> گردش مالی بازه {{ selectedPeriodDays }} روزه</h3>
          <div class="space-y-3 pt-2">
            <div class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex justify-between items-center"><span class="text-xs text-gray-300 font-bold">مجموع واریزی‌ها:</span><span class="text-sm font-black text-emerald-400 dir-ltr">{{ analyticsData.financial_summary.deposit_total.toLocaleString('fa-IR') }}</span></div>
            <div class="p-3 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex justify-between items-center"><span class="text-xs text-gray-300 font-bold">مجموع برداشت‌ها:</span><span class="text-sm font-black text-rose-400 dir-ltr">{{ analyticsData.financial_summary.withdraw_total.toLocaleString('fa-IR') }}</span></div>
            <div class="p-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl flex justify-between items-center"><span class="text-xs text-gray-300 font-bold">تراز خالص:</span><span class="text-sm font-black text-blue-400 dir-ltr">{{ analyticsData.financial_summary.balance_net.toLocaleString('fa-IR') }}</span></div>
          </div>
        </div>

        <div class="glass-card p-6 rounded-3xl border border-white/10 space-y-4">
          <h3 class="text-base font-black text-white flex items-center gap-2"><Film class="w-5 h-5 text-amber-400" /> آرشیو سبک زندگی</h3>
          <div class="grid grid-cols-3 gap-2 text-center pt-2">
            <div class="p-3 bg-white/5 rounded-2xl border border-white/10"><Film class="w-5 h-5 text-purple-400 mx-auto mb-1" /><span class="text-lg font-black text-white block">{{ analyticsData.lifestyle_summary.movies_watched }}</span><span class="text-[10px] text-gray-400">فیلم دیده‌شده</span></div>
            <div class="p-3 bg-white/5 rounded-2xl border border-white/10"><BookOpen class="w-5 h-5 text-blue-400 mx-auto mb-1" /><span class="text-lg font-black text-white block">{{ analyticsData.lifestyle_summary.books_read }}</span><span class="text-[10px] text-gray-400">کتاب خوانده‌شده</span></div>
            <div class="p-3 bg-white/5 rounded-2xl border border-white/10"><MapPin class="w-5 h-5 text-rose-400 mx-auto mb-1" /><span class="text-lg font-black text-white block">{{ analyticsData.lifestyle_summary.places_visited }}</span><span class="text-[10px] text-gray-400">مکان بازدیدشده</span></div>
          </div>
        </div>

      </div>
    </div>

    <!-- 📊 نمای ۲: نمای اصلی داشبورد -->
    <div v-else-if="isLoading" class="text-center py-20" :style="{ color: 'var(--text-secondary)' }">
      <RefreshCw class="w-10 h-10 animate-spin mx-auto mb-3 text-purple-400" />
      <p class="font-bold text-sm">در حال دریافت و تحلیل داده‌های برج دیده‌بانی...</p>
    </div>

    <div v-else-if="dashboardData" class="space-y-8">

      <!-- کارت‌های آمار زنده -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
        <div class="glass-card p-5 rounded-3xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">کارهای امروز</p>
            <p class="text-2xl md:text-3xl font-black" :style="{ color: 'var(--text-primary)' }">
              {{ dashboardData.summary.today_completed }} / {{ dashboardData.summary.today_total }}
            </p>
          </div>
          <div class="w-12 h-12 bg-blue-500/20 text-blue-400 rounded-2xl flex items-center justify-center border border-blue-500/30">
            <ListTodo class="w-6 h-6" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-3xl border border-red-500/30 bg-red-500/5 flex items-center justify-between">
          <div>
            <p class="text-xs text-red-400 font-bold mb-1">عقب‌افتاده‌ها 🚨</p>
            <p class="text-2xl md:text-3xl font-black text-red-400">{{ dashboardData.summary.overdue_count }}</p>
          </div>
          <div class="w-12 h-12 bg-red-500/20 text-red-400 rounded-2xl flex items-center justify-center border border-red-500/30">
            <AlertTriangle class="w-6 h-6 animate-pulse" />
          </div>
        </div>

        <!-- درصد واقعی تحقق کارهای دوره‌ای -->
        <div class="glass-card p-5 rounded-3xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">تحقق کارهای دوره‌ای</p>
            <p class="text-2xl md:text-3xl font-black text-emerald-400">{{ dashboardData.summary.recurring_completion_rate }}%</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 text-emerald-400 rounded-2xl flex items-center justify-center border border-emerald-500/30">
            <TrendingUp class="w-6 h-6" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-3xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">کل دارایی مالی</p>
            <p class="text-lg md:text-xl font-black text-purple-400">{{ dashboardData.summary.total_balance.toLocaleString('fa-IR') }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-500/20 text-purple-400 rounded-2xl flex items-center justify-center border border-purple-500/30">
            <Wallet class="w-6 h-6" />
          </div>
        </div>
      </div>

      <!-- نمودارهای گرافیکی (تقویم فارسی از شنبه + اسکیل ۰٪ + دکمه برج دیده‌بانی تحلیلی) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- نمودار ۱: چارت میله‌ای فعالیت ۷ روز گذشته (اسکیل واقعی با ۰٪ و روزهای فارسی از شنبه) -->
        <div class="lg:col-span-2 glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <TrendingUp class="w-5 h-5 text-blue-400" /> نمودار فعالیت ۷ روز گذشته (تقویم شمسی از شنبه)
            </h3>
            <span class="text-xs" :style="{ color: 'var(--text-secondary)' }">تسک‌های تکمیل‌شده در هفته</span>
          </div>

          <!-- چارت اسکیل‌یافته: اگر ۰ باشد ارتفاع دقیقاً ۰٪ خواهد بود -->
          <div class="h-48 flex items-end justify-between gap-2 pt-4 px-2 border-b border-white/10">
            <div v-for="day in dashboardData.weekly_activity" :key="day.date" class="flex-1 flex flex-col items-center h-full justify-end group relative">
              <div class="absolute -top-8 opacity-0 group-hover:opacity-100 transition bg-slate-900 border border-white/20 px-2 py-1 rounded text-[10px] text-white whitespace-nowrap z-20">
                {{ day.completed }} تسک تکمیل‌شده
              </div>

              <!-- اسکیل دقیق ۰ تا ۱۰۰٪ -->
              <div 
                class="w-full max-w-[32px] bg-gradient-to-t from-blue-600 to-purple-500 rounded-t-xl transition-all duration-500 group-hover:brightness-125 shadow-lg shadow-blue-500/20" 
                :style="{ height: (day.completed > 0 ? ((day.completed / maxWeeklyValue) * 100) : 0) + '%' }"
              ></div>

              <!-- فونت درشت و نام فارسی روزهای هفته شروع از شنبه -->
              <span class="text-xs md:text-sm font-black mt-2 text-white">{{ day.day_name }}</span>
            </div>
          </div>
        </div>

        <!-- نمودار ۲: دونات تفکیک دقیق انواع تسک‌ها با دکمه ورود به هاب تحلیلی -->
        <div class="glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <Flame class="w-5 h-5 text-amber-400" /> تفکیک انواع تسک‌ها
            </h3>

            <!-- دکمه ورود به برج دیده‌بانی تحلیلی کنار چارت دونات -->
            <button 
              @click="toggleAnalyticsView" 
              class="p-2 rounded-xl bg-purple-600/30 hover:bg-purple-600 text-purple-200 border border-purple-500/40 text-xs font-bold transition flex items-center gap-1.5 shadow-md"
              title="ورود به برج دیده‌بانی تحلیلی گرافی"
            >
              <BarChart2 class="w-4 h-4 text-amber-300" />
              <span>هاب تحلیلی</span>
            </button>
          </div>

          <!-- چارت دونات ۲ بخشی دقیق متناظر با راهنما -->
          <div class="relative flex items-center justify-center my-2">
            <svg class="w-36 h-36 transform -rotate-90" viewBox="0 0 36 36">
              <path class="text-gray-800" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <!-- تسک‌های یک‌باره (بنفش) -->
              <path class="text-purple-500" :stroke-dasharray="`${dashboardData.summary.fixed_completion_rate}, 100`" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <!-- تسک‌های دوره‌ای (سبز) -->
              <path class="text-emerald-400" :stroke-dasharray="`${dashboardData.summary.recurring_completion_rate}, 100`" stroke-dashoffset="-50" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
            <div class="absolute text-center">
              <span class="text-xl font-black" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.summary.total_tasks_count }}</span>
              <p class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">کل تسک‌ها</p>
            </div>
          </div>

          <div class="space-y-2 text-xs pt-2 border-t border-white/5">
            <div class="flex items-center justify-between">
              <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block"></span> تسک‌های یک‌باره:</span>
              <span class="font-bold text-white">{{ dashboardData.summary.fixed_tasks_count }} ({{ dashboardData.summary.fixed_completion_rate }}٪)</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block"></span> تسک‌های دوره‌ای:</span>
              <span class="font-bold text-white">{{ dashboardData.summary.recurring_tasks_count }} ({{ dashboardData.summary.recurring_completion_rate }}٪)</span>
            </div>
          </div>
        </div>

      </div>

      <!-- کارهای عقب‌افتاده + کارهای امروز با کلیک امنیتی -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <div class="glass-card p-6 rounded-3xl border border-red-500/30 bg-red-500/5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-black text-red-400 flex items-center gap-2"><AlertTriangle class="w-5 h-5 animate-pulse" /> کارهای عقب‌افتاده نیازمند اقدام</h3>
            <span class="text-xs bg-red-500/20 text-red-300 px-2.5 py-1 rounded-full font-bold">{{ dashboardData.overdue_tasks.length }} مورد</span>
          </div>

          <div v-if="dashboardData.overdue_tasks.length === 0" class="text-center py-8 text-xs" :style="{ color: 'var(--text-secondary)' }">🎉 هیچ کار عقب‌افتاده‌ای نداری.</div>
          <div v-else class="space-y-3 max-h-64 overflow-y-auto pr-1">
            <div v-for="task in dashboardData.overdue_tasks" :key="task.id" class="p-3.5 rounded-2xl bg-white/5 border border-red-500/20 flex items-center justify-between gap-3">
              <div><p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</p><p class="text-[10px] text-red-400 font-bold">مهلت: {{ formatDate(task.due_date) }}</p></div>
              <div class="flex items-center gap-1.5"><button @click="extendToToday(task)" class="px-2.5 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-[10px] font-bold">تمدید به امروز</button></div>
            </div>
          </div>
        </div>

        <!-- کارهای امروز (با باز کردن مودال مدیریت امنیتی) -->
        <div class="glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><ListTodo class="w-5 h-5 text-blue-400" /> کارهای امروز</h3>
              <router-link to="/tasks" class="text-xs text-blue-400 hover:underline flex items-center gap-1">اتاق عملیات <ArrowRight class="w-3.5 h-3.5" /></router-link>
            </div>

            <div v-if="dashboardData.today_tasks.length === 0" class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">هیچ تسکی برای امروز ثبت نشده است.</div>
            <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
              <div v-for="task in dashboardData.today_tasks" :key="task.id" @click="openTaskModal(task)" class="p-3 rounded-2xl bg-white/5 hover:bg-white/10 transition cursor-pointer flex items-center justify-between border border-white/5">
                <div class="flex items-center gap-3">
                  <div class="w-5 h-5 rounded-lg border-2 flex items-center justify-center transition" :class="task.is_completed ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30'"><CheckCircle v-if="task.is_completed" class="w-3.5 h-3.5" /></div>
                  <span class="text-xs font-bold" :class="task.is_completed ? 'line-through opacity-40' : ''" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</span>
                </div>
              </div>
            </div>
          </div>

          <form @submit.prevent="addQuickTask" class="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <input v-model="quickTaskTitle" type="text" placeholder="ثبت سریع تسک جدید برای امروز..." class="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500" :style="{ color: 'var(--text-primary)' }" />
            <button type="submit" class="p-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl transition"><Plus class="w-4 h-4" /></button>
          </form>
        </div>

      </div>

      <!-- اهداف کلان (محاسبه واقعی وزن‌دهی بر اساس SubGoals) + ایده برتر روز -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 glass-card p-6 rounded-3xl border border-white/10">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><Target class="w-5 h-5 text-purple-400" /> پیشرفت واقعی اهداف کلان (بر اساس گام‌های عملیاتی)</h3>
            <router-link to="/goals" class="text-xs text-purple-400 hover:underline">مشاهده همه اهداف</router-link>
          </div>

          <div v-if="dashboardData.goals.length === 0" class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">هیچ هدفی تعریف نشده است.</div>
          <div v-else class="space-y-4">
            <div v-for="goal in dashboardData.goals" :key="goal.id" class="p-4 rounded-2xl bg-white/5 border border-white/10">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-bold" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</span>
                <span class="text-xs font-black text-purple-400">{{ goal.calculated_progress }}%</span>
              </div>
              <div class="w-full h-2 rounded-full bg-black/20 overflow-hidden mb-2"><div class="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-700" :style="{ width: goal.calculated_progress + '%' }"></div></div>
            </div>
          </div>
        </div>

        <!-- ایده برتر روز (ثابت و با درجه هیجان بالا) -->
        <div class="glass-card p-6 rounded-3xl border border-amber-500/30 bg-amber-500/5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-black text-amber-400 flex items-center gap-2"><Lightbulb class="w-5 h-5" /> ایده برتر روز</h3>
              <router-link to="/ideas" class="text-xs text-amber-400 hover:underline">بانک ایده‌ها</router-link>
            </div>
            <div v-if="dashboardData.idea_of_the_day">
              <div class="flex items-center gap-1 mb-2">
                <span class="text-amber-300 font-bold text-xs">درجه هیجان:</span>
                <span class="text-amber-400">★ {{ dashboardData.idea_of_the_day.excitement_rating || 5 }}</span>
              </div>
              <h4 class="text-base font-bold mb-2" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.idea_of_the_day.title }}</h4>
              <p class="text-xs leading-relaxed line-clamp-4" :style="{ color: 'var(--text-secondary)' }">{{ dashboardData.idea_of_the_day.description || 'بدون توضیحات' }}</p>
            </div>
          </div>
          <router-link to="/ideas" class="mt-4 w-full py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-bold transition text-center block">ورود به بانک ایده‌ها</router-link>
        </div>
      </div>

    </div>

    <!-- مودال مدیریت امنیتی تسک انتخابی از لیست امروز -->
    <Teleport to="body">
      <div v-if="showTaskModal && selectedTaskForModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="w-full max-w-md glass-card p-6 rounded-3xl border border-white/20 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto custom-scrollbar">
          <div class="flex justify-between items-center border-b border-white/10 pb-3">
            <h3 class="text-base font-bold text-white flex items-center gap-2"><ShieldAlert class="w-5 h-5 text-amber-400" /> مدیریت امنیتی تسک</h3>
            <button @click="showTaskModal = false" class="text-gray-400 hover:text-white"><X class="w-5 h-5" /></button>
          </div>

          <div class="space-y-3 text-right">
            <div><label class="block text-[11px] text-gray-400">عنوان تسک:</label><p class="text-sm font-black text-white mt-1">{{ selectedTaskForModal.title }}</p></div>
            <div><label class="block text-[11px] text-gray-400">هدف مرتبط:</label><p class="text-xs font-bold text-purple-300 mt-1">{{ selectedTaskForModal.goal_title }}</p></div>
            <div><label class="block text-[11px] text-gray-400">دسته‌بندی:</label><span class="inline-block px-2.5 py-1 rounded bg-white/10 text-xs font-bold text-gray-200 mt-1">{{ selectedTaskForModal.category || 'عمومی' }}</span></div>
          </div>

          <div class="flex gap-3 pt-4 border-t border-white/10">
            <button @click="confirmToggleTask" class="flex-1 py-3 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-xl shadow-lg flex items-center justify-center gap-1.5">
              <CheckCircle class="w-4 h-4" />
              <span>{{ selectedTaskForModal.is_completed ? 'علامت‌گذاری به عنوان انجام‌نشده' : 'تایید و تکمیل تسک' }}</span>
            </button>
            <button @click="showTaskModal = false" class="py-3 px-4 bg-white/10 hover:bg-white/20 text-gray-300 font-bold text-xs rounded-xl">انصراف</button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>