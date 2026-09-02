<script setup>
import { ref, computed, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import { useRouter } from 'vue-router'
import {
  ListTodo, CheckCircle, Flame, TrendingUp, Zap, AlertTriangle,
  Wallet, Lightbulb, Target, Calendar, Plus, RefreshCw, ArrowRight, Clock, Star,
  BarChart2, PieChart, Film, BookOpen, MapPin, Scale, X, Edit3, ShieldAlert, Award
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

// 📱 تب فعال موبایل (فقط در صفحه‌های کوچک نمایش داده میشه)
const mobileTab = ref('today') // 'today' | 'overdue' | 'goals' | 'ideas'

// 📊 روز انتخاب‌شده برای نمایش popup تفکیک تسک‌ها
const selectedDay = ref(null)
function openDayDetail(day) {
  // toggle: اگه همین روز بازه، ببند؛ وگرنه باز کن
  selectedDay.value = (selectedDay.value && selectedDay.value.date === day.date) ? null : day
}

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
    const [dashRes, skillsRes] = await Promise.all([
      api.get('/dashboard/overview'),
      api.get('/skills/_stats/summary').catch(() => ({ data: null }))
    ])
    dashboardData.value = dashRes.data
    skillsStats.value = skillsRes.data
  } catch (error) {
    console.error('خطا در دریافت اطلاعات برج دیده‌بانی:', error)
  } finally {
    isLoading.value = false
  }
}

const skillsStats = ref(null)

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

// محاسبات تحلیلی هفته (KPI + نمودار)
// API به ترتیب [شنبه, یکشنبه, ..., جمعه] برمی‌گردونه (هفته جاری شمسی)
// در RTL: راست = اندیس ۰ = شنبه ✓ (نیازی به reverse نیست)
const orderedWeeklyActivity = computed(() => {
  return dashboardData.value?.weekly_activity || []
})

// تشخیص اندیس امروز بر اساس تاریخ واقعی
// day_index: 0=شنبه، 1=یکشنبه، ...، 6=جمعه
const todayIndexInOrdered = computed(() => {
  const data = orderedWeeklyActivity.value
  if (data.length === 0) return -1

  // تاریخ امروز به فرمت YYYY-MM-DD
  const today = new Date()
  const todayStr = today.toISOString().split('T')[0]

  // اول: مقایسه مستقیم با فیلد date
  const idx = data.findIndex(d => d.date === todayStr)
  if (idx !== -1) return idx

  // دوم: fallback - آخرین روز (اگه API امروز رو برگردونده)
  return data.length - 1
})

// شمارنده عقب‌افتاده
const overdueCount = computed(() => dashboardData.value?.overdue_count || 0)

const weeklyStats = computed(() => {
  const data = orderedWeeklyActivity.value
  if (data.length === 0) {
    return { total: 0, avg: 0, bestDay: '-', bestCount: 0, trend: 0, maxValue: 1, avgLinePos: 0, todayIndex: -1 }
  }

  // مجموع و میانگین
  const total = data.reduce((s, d) => s + (d.completed || 0), 0)
  const avg = data.length > 0 ? Math.round((total / data.length) * 10) / 10 : 0

  // بهترین روز
  let bestDay = '-'
  let bestCount = 0
  for (const d of data) {
    if ((d.completed || 0) > bestCount) {
      bestCount = d.completed
      bestDay = d.day_name || '-'
    }
  }

  // روند: مقایسه میانگین ۳ روز اول هفته (شنبه، یکشنبه، دوشنبه) با ۴ روز دوم (سه‌شنبه تا جمعه)
  // نیمه اول = ابتدای هفته، نیمه دوم = انتهای هفته
  const mid = 3
  const firstHalf = data.slice(0, mid)
  const secondHalf = data.slice(mid)
  const firstAvg = firstHalf.length > 0 ? firstHalf.reduce((s, d) => s + (d.completed || 0), 0) / firstHalf.length : 0
  const secondAvg = secondHalf.length > 0 ? secondHalf.reduce((s, d) => s + (d.completed || 0), 0) / secondHalf.length : 0
  const trend = firstAvg > 0 ? Math.round(((secondAvg - firstAvg) / firstAvg) * 100) : (secondAvg > 0 ? 100 : 0)

  // بیشترین مقدار برای اسکیل
  const maxComp = Math.max(...data.map(d => d.completed || 0), 0)
  const maxPlanned = Math.max(...data.map(d => d.planned || 0), 0)
  const maxValue = Math.max(maxComp, maxPlanned, 1)

  // موقعیت خط میانگین (درصد)
  const avgLinePos = maxValue > 0 ? Math.min(100, (avg / maxValue) * 100) : 0

  return {
    total,
    avg,
    bestDay,
    bestCount,
    trend,
    maxValue,
    avgLinePos,
    todayIndex: todayIndexInOrdered.value
  }
})

// درصدهای نمودار ۳ بعدی
const fixedPercent = computed(() => {
  const total = (dashboardData.value?.summary?.fixed_tasks_count || 0) + (dashboardData.value?.summary?.recurring_tasks_count || 0)
  return total > 0 ? Math.round((dashboardData.value.summary.fixed_tasks_count / total) * 100) : 0
})
const greenPercent = computed(() => {
  const total = (dashboardData.value?.summary?.fixed_tasks_count || 0) + (dashboardData.value?.summary?.recurring_tasks_count || 0)
  return total > 0 ? Math.round((dashboardData.value.summary.recurring_tasks_count / total) * 100) : 0
})

// ارتفاع stack bar (بر اساس completion rate)
const fixedCompletionHeight = computed(() => {
  return dashboardData.value?.summary?.fixed_completion_rate || 0
})
const recurringCompletionHeight = computed(() => {
  return dashboardData.value?.summary?.recurring_completion_rate || 0
})

// تعداد کل تکمیل‌شده و باقی‌مانده
const totalCompletedCount = computed(() => {
  return (dashboardData.value?.summary?.fixed_completed_count || 0) + (dashboardData.value?.summary?.recurring_completed_count || 0)
})
const totalRemainingCount = computed(() => {
  return (dashboardData.value?.summary?.total_tasks_count || 0) - totalCompletedCount.value
})

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="p-3 sm:p-4 md:p-8 lg:p-10 max-w-7xl mx-auto space-y-4 sm:space-y-6 md:space-y-8 text-right" dir="rtl">

    <!-- هدر برج دیده‌بانی (فشرده در موبایل) -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 shadow-2xl">
      <div>
        <div class="flex items-center gap-2.5 sm:gap-3 mb-1.5 sm:mb-2">
          <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl flex items-center justify-center bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg shadow-purple-500/30">
            <Zap class="w-5 h-5 sm:w-6 sm:h-6 text-white" />
          </div>
          <div>
            <h1 class="text-lg sm:text-2xl md:text-3xl font-black" :style="{ color: 'var(--text-primary)' }">{{ greetingMessage }}</h1>
            <p class="text-[11px] sm:text-xs md:text-sm mt-0.5 sm:mt-1" :style="{ color: 'var(--text-secondary)' }">برج دیده‌بانی و اتاق فرمان برنامه‌ریزی شخصی شما</p>
          </div>
        </div>
      </div>

      <!-- کادر انگیزشی -->
      <div class="max-w-md bg-white/5 border border-white/10 p-3 sm:p-4 rounded-xl sm:rounded-2xl backdrop-blur-md">
        <p class="text-[10px] sm:text-xs text-amber-400 font-bold mb-1 flex items-center gap-1">
          <Star class="w-3 h-3 sm:w-3.5 sm:h-3.5 fill-amber-400" /> الهام‌بخش روز:
        </p>
        <p class="text-[11px] sm:text-xs leading-relaxed italic" :style="{ color: 'var(--text-primary)' }">« {{ todayQuote }} »</p>
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

      <!-- کارت‌های آمار زنده (فشرده در موبایل) -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-3 md:gap-4 lg:gap-6">
        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex items-center justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs font-bold mb-0.5 sm:mb-1 truncate" :style="{ color: 'var(--text-secondary)' }">کارهای امروز</p>
            <p class="text-lg sm:text-2xl md:text-3xl font-black" :style="{ color: 'var(--text-primary)' }">
              {{ dashboardData.summary.today_completed }} / {{ dashboardData.summary.today_total }}
            </p>
          </div>
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 shrink-0 bg-blue-500/20 text-blue-400 rounded-xl md:rounded-2xl flex items-center justify-center border border-blue-500/30">
            <ListTodo class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />
          </div>
        </div>

        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-red-500/30 bg-red-500/5 flex items-center justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs text-red-400 font-bold mb-0.5 sm:mb-1 truncate">عقب‌افتاده‌ها 🚨</p>
            <p class="text-lg sm:text-2xl md:text-3xl font-black text-red-400">{{ dashboardData.summary.overdue_count }}</p>
          </div>
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 shrink-0 bg-red-500/20 text-red-400 rounded-xl md:rounded-2xl flex items-center justify-center border border-red-500/30">
            <AlertTriangle class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 animate-pulse" />
          </div>
        </div>

        <!-- درصد واقعی تحقق کارهای دوره‌ای -->
        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex items-center justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs font-bold mb-0.5 sm:mb-1 truncate" :style="{ color: 'var(--text-secondary)' }">تحقق دوره‌ای</p>
            <p class="text-lg sm:text-2xl md:text-3xl font-black text-emerald-400">{{ dashboardData.summary.recurring_completion_rate }}%</p>
          </div>
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 shrink-0 bg-emerald-500/20 text-emerald-400 rounded-xl md:rounded-2xl flex items-center justify-center border border-emerald-500/30">
            <TrendingUp class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />
          </div>
        </div>

        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex items-center justify-between gap-2">
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs font-bold mb-0.5 sm:mb-1 truncate" :style="{ color: 'var(--text-secondary)' }">کل دارایی</p>
            <p class="text-sm sm:text-base md:text-lg lg:text-xl font-black text-purple-400 truncate">{{ dashboardData.summary.total_balance.toLocaleString('fa-IR') }}</p>
          </div>
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 shrink-0 bg-purple-500/20 text-purple-400 rounded-xl md:rounded-2xl flex items-center justify-center border border-purple-500/30">
            <Wallet class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />
          </div>
        </div>
      </div>

      <!-- نمودارهای گرافیکی (تقویم فارسی از شنبه + اسکیل ۰٪ + دکمه برج دیده‌بانی تحلیلی) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">

        <!-- نمودار ۱: داشبورد تحلیلی هفته (KPI + Bar Chart + Trend Line) -->
        <div class="lg:col-span-2 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 space-y-4 sm:space-y-5">

          <!-- هدر + خلاصه KPI در یک ردیف -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h3 class="text-base sm:text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <TrendingUp class="w-5 h-5 text-blue-400" /> فعالیت ۷ روز گذشته
            </h3>
            <span class="text-[11px] sm:text-xs px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 font-bold inline-flex items-center gap-1.5 self-start sm:self-auto">
              <Calendar class="w-3 h-3" /> هفته شمسی
            </span>
          </div>

          <!-- ۴ کارت KPI کوچک -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20">
              <p class="text-[10px] font-bold" :style="{ color: 'var(--text-secondary)' }">مجموع هفته</p>
              <p class="text-lg sm:text-xl font-black text-blue-300 mt-0.5">{{ weeklyStats.total }}</p>
              <p class="text-[9px] text-blue-400/70 font-bold">تسک تکمیل‌شده</p>
            </div>
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/20">
              <p class="text-[10px] font-bold" :style="{ color: 'var(--text-secondary)' }">میانگین روزانه</p>
              <p class="text-lg sm:text-xl font-black text-emerald-300 mt-0.5">{{ weeklyStats.avg }}</p>
              <p class="text-[9px] text-emerald-400/70 font-bold">تسک در روز</p>
            </div>
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
              <p class="text-[10px] font-bold" :style="{ color: 'var(--text-secondary)' }">بهترین روز</p>
              <p class="text-sm sm:text-base font-black text-amber-300 mt-0.5 truncate">{{ weeklyStats.bestDay }}</p>
              <p class="text-[9px] text-amber-400/70 font-bold">{{ weeklyStats.bestCount }} تسک</p>
            </div>
            <div class="p-2.5 sm:p-3 rounded-xl border" :class="weeklyStats.trend > 0 ? 'bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20' : weeklyStats.trend < 0 ? 'bg-gradient-to-br from-rose-500/10 to-red-500/10 border-rose-500/20' : 'bg-gradient-to-br from-slate-500/10 to-gray-500/10 border-slate-500/20'">
              <p class="text-[10px] font-bold" :style="{ color: 'var(--text-secondary)' }">روند هفته</p>
              <p class="text-lg sm:text-xl font-black mt-0.5 flex items-center gap-1" :class="weeklyStats.trend > 0 ? 'text-green-300' : weeklyStats.trend < 0 ? 'text-rose-300' : 'text-slate-300'">
                <span v-if="weeklyStats.trend > 0">↗</span>
                <span v-else-if="weeklyStats.trend < 0">↘</span>
                <span v-else>→</span>
                {{ weeklyStats.trend > 0 ? '+' : '' }}{{ weeklyStats.trend }}٪
              </p>
              <p class="text-[9px] font-bold opacity-70" :class="weeklyStats.trend > 0 ? 'text-green-400' : weeklyStats.trend < 0 ? 'text-rose-400' : 'text-slate-400'">نسبت به نیمه اول</p>
            </div>
          </div>

          <!-- نمودار میله‌ای Stacked با کلیک‌پذیری و popup تفکیک -->
          <div class="relative">
            <!-- خط میانگین -->
            <div class="absolute left-0 right-0 border-t border-dashed border-amber-400/40 z-[5] pointer-events-none" :style="{ bottom: weeklyStats.avgLinePos + '%' }">
              <span class="absolute -top-3 right-0 text-[9px] text-amber-400 bg-slate-900/80 px-1.5 py-0.5 rounded font-bold">میانگین: {{ weeklyStats.avg }}</span>
            </div>

            <!-- نمودار Stacked: هر روز یک ستون با دو میله روی هم -->
            <div class="h-40 sm:h-44 flex items-end justify-between gap-1.5 sm:gap-2 pt-6 px-1 relative">
              <div v-for="(day, idx) in orderedWeeklyActivity" :key="day.date" class="flex-1 h-full flex flex-col items-center justify-end cursor-pointer group" @click="openDayDetail(day)">
                <!-- popup شناور (روی میله) - با موقعیت هوشمند برای جلوگیری از بیرون‌زدگی -->
                <Transition name="popup">
                  <div v-if="selectedDay && selectedDay.date === day.date"
                       class="absolute bottom-full mb-2 z-30 bg-slate-900/98 border border-white/30 backdrop-blur-xl rounded-2xl p-3 shadow-2xl min-w-[160px] text-right"
                       :class="[
                         idx === 0 ? 'right-0' : (idx === orderedWeeklyActivity.length - 1 ? 'left-0' : 'left-1/2 -translate-x-1/2')
                       ]"
                       style="backface-visibility: hidden;">
                    <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-white/10">
                      <span class="text-xs font-black" :style="{ color: 'var(--text-primary)' }">{{ day.day_name }} {{ formatDate(day.date).slice(5) }}</span>
                      <button @click.stop="selectedDay = null" class="text-slate-400 hover:text-white text-xs leading-none">✕</button>
                    </div>
                    <div class="space-y-1.5 text-[11px]">
                      <div class="flex items-center justify-between gap-3">
                        <span class="flex items-center gap-1.5">
                          <span class="w-2.5 h-2.5 rounded-sm bg-purple-500"></span>
                          <span class="font-bold" :style="{ color: 'var(--text-secondary)' }">ثابت</span>
                        </span>
                        <span class="font-black text-purple-300">{{ day.fixed_completed || 0 }}</span>
                      </div>
                      <div class="flex items-center justify-between gap-3">
                        <span class="flex items-center gap-1.5">
                          <span class="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
                          <span class="font-bold" :style="{ color: 'var(--text-secondary)' }">دوره‌ای</span>
                        </span>
                        <span class="font-black text-emerald-300">{{ day.recurring_completed || 0 }}</span>
                      </div>
                      <div class="flex items-center justify-between gap-3 pt-1.5 mt-1.5 border-t border-white/10">
                        <span class="font-black" :style="{ color: 'var(--text-primary)' }">مجموع</span>
                        <span class="font-black text-base" :style="{ color: 'var(--text-primary)' }">{{ day.completed || 0 }}</span>
                      </div>
                    </div>
                    <!-- فلش popup - موقعیت بر اساس لبه -->
                    <div class="absolute top-full w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-transparent border-t-slate-900"
                         :class="[
                           idx === 0 ? 'right-4' : (idx === orderedWeeklyActivity.length - 1 ? 'left-4' : 'left-1/2 -translate-x-1/2')
                         ]"></div>
                  </div>
                </Transition>

                <!-- عدد بالای میله (مجموع) -->
                <span v-if="day.completed > 0" class="absolute -top-1 text-[10px] font-black px-1.5 py-0.5 rounded" :class="idx === weeklyStats.todayIndex ? 'text-amber-200 bg-amber-500/30 ring-1 ring-amber-400/40' : 'text-blue-200 bg-blue-500/20 ring-1 ring-blue-400/30'">{{ day.completed }}</span>

                <!-- فضای میله + نام روز -->
                <div class="w-full max-w-[36px] h-full flex flex-col items-center justify-end relative">
                  <!-- میله Stacked: ثابت (بنفش، پایین) + دوره‌ای (سبز، بالا) -->
                  <div class="w-full flex flex-col-reverse items-stretch overflow-hidden rounded-t-md ring-1 transition-all" :class="idx === weeklyStats.todayIndex ? 'ring-amber-400/60 shadow-lg shadow-amber-500/30' : 'ring-white/10 group-hover:ring-white/30'" :style="{ height: ((day.completed || 0) > 0 ? Math.max(8, ((day.completed / weeklyStats.maxValue) * 100)) : 0) + '%', minHeight: (day.completed > 0 ? '8px' : '0') }">
                    <!-- بخش ثابت (بنفش) - در پایین -->
                    <div v-if="(day.fixed_completed || 0) > 0" class="w-full bg-gradient-to-t from-purple-700 to-purple-500 transition-all duration-500" :style="{ height: weeklyStats.maxValue > 0 ? Math.max(2, ((day.fixed_completed / weeklyStats.maxValue) * 100)) + '%' : '0%' }"></div>
                    <!-- بخش دوره‌ای (سبز) - در بالا -->
                    <div v-if="(day.recurring_completed || 0) > 0" class="w-full bg-gradient-to-t from-emerald-700 to-emerald-400 transition-all duration-500" :style="{ height: weeklyStats.maxValue > 0 ? Math.max(2, ((day.recurring_completed / weeklyStats.maxValue) * 100)) + '%' : '0%' }"></div>
                  </div>
                </div>

                <!-- نام روز -->
                <div class="flex flex-col items-center mt-1.5 shrink-0">
                  <span class="text-[10px] sm:text-xs font-black text-center" :class="idx === weeklyStats.todayIndex ? 'text-amber-300' : ''" :style="{ color: idx === weeklyStats.todayIndex ? '' : 'var(--text-secondary)' }">{{ day.day_name }}</span>
                  <span v-if="idx === weeklyStats.todayIndex" class="text-[8px] sm:text-[9px] text-amber-400 font-black mt-0.5">امروز</span>
                </div>
              </div>
            </div>
          </div>

          <!-- راهنمای پایین -->
          <div class="flex flex-wrap items-center justify-center gap-3 sm:gap-4 pt-2 border-t border-white/5 text-[10px] sm:text-xs">
            <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-3 h-3 rounded-sm bg-gradient-to-t from-purple-700 to-purple-500"></span>ثابت</span>
            <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-3 h-3 rounded-sm bg-gradient-to-t from-emerald-700 to-emerald-400"></span>دوره‌ای</span>
            <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-3 h-3 rounded-full bg-amber-400"></span>امروز</span>
            <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-3 h-3 rounded-sm bg-blue-500/20 ring-1 ring-blue-400/30"></span>روی نمودار کلیک کنید</span>
          </div>
        </div>

        <!-- نمودار ۲: نمودار سه‌بعدی (3D) تفکیک انواع تسک‌ها -->
        <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 flex flex-col">
          <div class="flex items-center justify-between mb-3 sm:mb-4">
            <h3 class="text-base sm:text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <Flame class="w-5 h-5 text-amber-400" /> تفکیک تسک‌ها
            </h3>
            <button
              @click="toggleAnalyticsView"
              class="p-1.5 sm:p-2 rounded-lg sm:rounded-xl bg-purple-600/30 hover:bg-purple-600 text-purple-200 border border-purple-500/40 text-[10px] sm:text-xs font-bold transition flex items-center gap-1 sm:gap-1.5 shadow-md"
              title="هاب تحلیلی"
            >
              <BarChart2 class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-300" />
              <span class="hidden sm:inline">هاب تحلیلی</span>
            </button>
          </div>

          <!-- نمودار دو Stack Bar عمودی (دماسنج) - شفاف و واضح -->
          <div class="relative flex-1 flex flex-col my-2">
            <!-- عنوان بالا: کل تسک‌ها -->
            <div class="text-center mb-3">
              <p class="text-3xl sm:text-4xl font-black" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.summary.total_tasks_count }}</p>
              <p class="text-[10px] sm:text-xs font-bold" :style="{ color: 'var(--text-secondary)' }">کل تسک‌های ثبت‌شده</p>
              <div class="flex items-center justify-center gap-2 mt-1.5 text-[10px] font-black">
                <span class="px-2 py-0.5 rounded-full" :style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }">
                  ✓ {{ totalCompletedCount }} تکمیل‌شده
                </span>
                <span class="px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-300">
                  {{ totalRemainingCount }} باقی
                </span>
              </div>
            </div>

            <!-- دو Stack Bar -->
            <div class="flex-1 flex items-end justify-around gap-3 sm:gap-4 px-2">
              <!-- Bar 1: ثابت (بنفش) -->
              <div class="flex-1 flex flex-col items-center gap-2 max-w-[100px]">
                <!-- Stack bar -->
                <div class="relative w-full h-32 sm:h-36 rounded-xl overflow-hidden ring-1 ring-white/15 shadow-lg">
                  <!-- باقی (کم‌رنگ) -->
                  <div class="absolute inset-x-0 bottom-0 bg-purple-500/20" :style="{ height: '100%' }"></div>
                  <!-- تکمیل‌شده (پررنگ) - از پایین -->
                  <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-purple-700 via-purple-600 to-purple-500 transition-all duration-700" :style="{ height: fixedCompletionHeight + '%' }">
                    <!-- عدد تکمیل‌شده -->
                    <div class="absolute top-1.5 left-1/2 -translate-x-1/2 text-[11px] sm:text-xs font-black text-white drop-shadow-lg">
                      {{ dashboardData.summary.fixed_completed_count || 0 }}
                    </div>
                  </div>
                  <!-- عدد کل در پایین -->
                  <div class="absolute bottom-1.5 left-1/2 -translate-x-1/2 text-[9px] sm:text-[10px] font-bold text-purple-200 bg-slate-900/60 px-1.5 py-0.5 rounded">
                    {{ dashboardData.summary.fixed_tasks_count }} کل
                  </div>
                </div>
                <!-- Label -->
                <div class="text-center">
                  <p class="text-xs sm:text-sm font-black" :style="{ color: 'var(--text-primary)' }">ثابت</p>
                  <p class="text-[9px] sm:text-[10px] font-bold text-purple-400">{{ dashboardData.summary.fixed_completion_rate }}٪ تکمیل</p>
                </div>
              </div>

              <!-- Bar 2: دوره‌ای (سبز) -->
              <div class="flex-1 flex flex-col items-center gap-2 max-w-[100px]">
                <div class="relative w-full h-32 sm:h-36 rounded-xl overflow-hidden ring-1 ring-white/15 shadow-lg">
                  <!-- باقی (کم‌رنگ) -->
                  <div class="absolute inset-x-0 bottom-0 bg-emerald-500/20" :style="{ height: '100%' }"></div>
                  <!-- تکمیل‌شده (پررنگ) -->
                  <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-emerald-700 via-emerald-600 to-emerald-400 transition-all duration-700" :style="{ height: recurringCompletionHeight + '%' }">
                    <div class="absolute top-1.5 left-1/2 -translate-x-1/2 text-[11px] sm:text-xs font-black text-white drop-shadow-lg">
                      {{ dashboardData.summary.recurring_completed_count || 0 }}
                    </div>
                  </div>
                  <div class="absolute bottom-1.5 left-1/2 -translate-x-1/2 text-[9px] sm:text-[10px] font-bold text-emerald-200 bg-slate-900/60 px-1.5 py-0.5 rounded">
                    {{ dashboardData.summary.recurring_tasks_count }} کل
                  </div>
                </div>
                <div class="text-center">
                  <p class="text-xs sm:text-sm font-black" :style="{ color: 'var(--text-primary)' }">دوره‌ای</p>
                  <p class="text-[9px] sm:text-[10px] font-bold text-emerald-400">{{ dashboardData.summary.recurring_completion_rate }}٪ تکمیل</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- 📱 تب‌بندی موبایل: فقط در صفحه کوچک نمایش داده میشه -->
      <div class="lg:hidden glass-card p-1.5 rounded-2xl border border-white/10 flex items-center gap-1 sticky top-2 z-20 backdrop-blur-xl" :style="{ background: 'var(--bg-card)' }">
        <button @click="mobileTab = 'today'" :class="mobileTab === 'today' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' : ''" class="flex-1 py-2 px-1 rounded-xl text-[11px] font-black transition" :style="mobileTab !== 'today' ? { color: 'var(--text-secondary)' } : {}">
          📋 امروز
        </button>
        <button @click="mobileTab = 'overdue'" :class="mobileTab === 'overdue' ? 'bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-lg' : ''" class="flex-1 py-2 px-1 rounded-xl text-[11px] font-black transition relative" :style="mobileTab !== 'overdue' ? { color: 'var(--text-secondary)' } : {}">
          🚨 عقب‌افتاده
          <span v-if="dashboardData.overdue_count > 0" class="absolute -top-1 -left-1 bg-red-500 text-white text-[9px] font-black rounded-full w-4 h-4 flex items-center justify-center ring-2 ring-slate-900">{{ dashboardData.overdue_count }}</span>
        </button>
        <button @click="mobileTab = 'goals'" :class="mobileTab === 'goals' ? 'bg-gradient-to-r from-purple-600 to-fuchsia-600 text-white shadow-lg' : ''" class="flex-1 py-2 px-1 rounded-xl text-[11px] font-black transition" :style="mobileTab !== 'goals' ? { color: 'var(--text-secondary)' } : {}">
          🎯 اهداف
        </button>
        <button @click="mobileTab = 'ideas'" :class="mobileTab === 'ideas' ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg' : ''" class="flex-1 py-2 px-1 rounded-xl text-[11px] font-black transition" :style="mobileTab !== 'ideas' ? { color: 'var(--text-secondary)' } : {}">
          💡 ایده
        </button>
      </div>

      <!-- کارهای عقب‌افتاده + کارهای امروز با کلیک امنیتی -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 md:gap-6">

        <!-- 📱 موبایل: فقط تب فعال نمایش داده میشه / دسکتاپ: همیشه -->
        <div class="hidden lg:block glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-red-500/30 bg-red-500/5">
          <div class="flex items-center justify-between mb-3 sm:mb-4">
            <h3 class="text-base sm:text-lg font-black text-red-400 flex items-center gap-2"><AlertTriangle class="w-4 h-4 sm:w-5 sm:h-5 animate-pulse" /> کارهای عقب‌افتاده نیازمند اقدام</h3>
            <span class="text-[10px] sm:text-xs bg-red-500/20 text-red-300 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full font-bold">{{ dashboardData.overdue_tasks.length }} مورد</span>
          </div>

          <div v-if="dashboardData.overdue_tasks.length === 0" class="text-center py-6 sm:py-8 text-xs" :style="{ color: 'var(--text-secondary)' }">🎉 هیچ کار عقب‌افتاده‌ای نداری.</div>
          <div v-else class="space-y-2 sm:space-y-3 max-h-64 overflow-y-auto pr-1">
            <div v-for="task in dashboardData.overdue_tasks" :key="task.id" class="p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl bg-white/5 border border-red-500/20 flex items-center justify-between gap-2 sm:gap-3">
              <div class="min-w-0"><p class="text-[11px] sm:text-xs font-bold mb-0.5 sm:mb-1 truncate" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</p><p class="text-[10px] text-red-400 font-bold">مهلت: {{ formatDate(task.due_date) }}</p></div>
              <button @click="extendToToday(task)" class="px-2 sm:px-2.5 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-[10px] font-bold shrink-0">تمدید</button>
            </div>
          </div>
        </div>

        <!-- کارهای امروز (با باز کردن مودال مدیریت امنیتی) -->
        <div class="hidden lg:flex glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3 sm:mb-4">
              <h3 class="text-base sm:text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><ListTodo class="w-4 h-4 sm:w-5 sm:h-5 text-blue-400" /> کارهای امروز</h3>
              <router-link to="/tasks" class="text-[11px] sm:text-xs text-blue-400 hover:underline flex items-center gap-1">اتاق عملیات <ArrowRight class="w-3 h-3 sm:w-3.5 sm:h-3.5" /></router-link>
            </div>

            <div v-if="dashboardData.today_tasks.length === 0" class="text-center py-4 sm:py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">هیچ تسکی برای امروز ثبت نشده است.</div>
            <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
              <div v-for="task in dashboardData.today_tasks" :key="task.id" @click="openTaskModal(task)" class="p-2.5 sm:p-3 rounded-xl sm:rounded-2xl bg-white/5 hover:bg-white/10 transition cursor-pointer flex items-center justify-between border border-white/5">
                <div class="flex items-center gap-2 sm:gap-3 min-w-0">
                  <div class="w-4 h-4 sm:w-5 sm:h-5 rounded-md sm:rounded-lg border-2 shrink-0 flex items-center justify-center transition" :class="task.is_completed ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30'"><CheckCircle v-if="task.is_completed" class="w-2.5 h-2.5 sm:w-3.5 sm:h-3.5" /></div>
                  <span class="text-[11px] sm:text-xs font-bold truncate" :class="task.is_completed ? 'line-through opacity-40' : ''" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</span>
                </div>
              </div>
            </div>
          </div>

          <form @submit.prevent="addQuickTask" class="mt-3 sm:mt-4 pt-2.5 sm:pt-3 border-t border-white/10 flex items-center gap-2">
            <input v-model="quickTaskTitle" type="text" placeholder="ثبت سریع..." class="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl text-[11px] sm:text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500" :style="{ color: 'var(--text-primary)' }" />
            <button type="submit" class="p-2 sm:p-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg sm:rounded-xl transition"><Plus class="w-3.5 h-3.5 sm:w-4 sm:h-4" /></button>
          </form>
        </div>

        <!-- 📱 موبایل: نمایش تب فعال -->
        <div v-show="mobileTab === 'today'" class="lg:hidden glass-card p-4 rounded-2xl border border-white/10 flex flex-col">
          <div>
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-base font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><ListTodo class="w-5 h-5 text-blue-400" /> کارهای امروز</h3>
              <span class="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full font-bold">{{ dashboardData.today_tasks.length }} مورد</span>
            </div>
            <div v-if="dashboardData.today_tasks.length === 0" class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">هیچ تسکی برای امروز ثبت نشده است.</div>
            <div v-else class="space-y-2 max-h-72 overflow-y-auto pr-1">
              <div v-for="task in dashboardData.today_tasks" :key="task.id" @click="openTaskModal(task)" class="p-3 rounded-xl bg-white/5 hover:bg-white/10 transition cursor-pointer flex items-center justify-between border border-white/5">
                <div class="flex items-center gap-2.5 min-w-0 flex-1">
                  <div class="w-5 h-5 rounded-lg border-2 shrink-0 flex items-center justify-center transition" :class="task.is_completed ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30'"><CheckCircle v-if="task.is_completed" class="w-3.5 h-3.5" /></div>
                  <span class="text-xs font-bold truncate" :class="task.is_completed ? 'line-through opacity-40' : ''" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</span>
                </div>
              </div>
            </div>
          </div>
          <form @submit.prevent="addQuickTask" class="mt-3 pt-3 border-t border-white/10 flex items-center gap-2">
            <input v-model="quickTaskTitle" type="text" placeholder="ثبت سریع تسک جدید..." class="flex-1 px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500" :style="{ color: 'var(--text-primary)' }" />
            <button type="submit" class="p-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl transition"><Plus class="w-4 h-4" /></button>
          </form>
        </div>

        <div v-show="mobileTab === 'overdue'" class="lg:hidden glass-card p-4 rounded-2xl border border-red-500/30 bg-red-500/5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-black text-red-400 flex items-center gap-2"><AlertTriangle class="w-5 h-5 animate-pulse" /> کارهای عقب‌افتاده</h3>
            <span class="text-[10px] bg-red-500/20 text-red-300 px-2 py-0.5 rounded-full font-bold">{{ dashboardData.overdue_tasks.length }} مورد</span>
          </div>
          <div v-if="dashboardData.overdue_tasks.length === 0" class="text-center py-8 text-xs" :style="{ color: 'var(--text-secondary)' }">🎉 هیچ کار عقب‌افتاده‌ای نداری.</div>
          <div v-else class="space-y-2 max-h-72 overflow-y-auto pr-1">
            <div v-for="task in dashboardData.overdue_tasks" :key="task.id" class="p-3 rounded-xl bg-white/5 border border-red-500/20">
              <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</p>
              <div class="flex items-center justify-between gap-2">
                <p class="text-[10px] text-red-400 font-bold">مهلت: {{ formatDate(task.due_date) }}</p>
                <button @click="extendToToday(task)" class="px-2.5 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-[10px] font-bold">تمدید به امروز</button>
              </div>
            </div>
          </div>
        </div>

        <div v-show="mobileTab === 'goals'" class="lg:hidden glass-card p-4 rounded-2xl border border-white/10">
          <h3 class="text-base font-black mb-3 flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><Target class="w-5 h-5 text-purple-400" /> اهداف کلان</h3>
          <div v-if="dashboardData.goals.length === 0" class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">هیچ هدفی تعریف نشده است.</div>
          <div v-else class="space-y-3 max-h-72 overflow-y-auto pr-1">
            <div v-for="goal in dashboardData.goals" :key="goal.id" class="p-3 rounded-xl bg-white/5 border border-white/10">
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-xs font-bold truncate flex-1" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</span>
                <span class="text-xs font-black text-purple-400 mr-2">{{ goal.calculated_progress }}%</span>
              </div>
              <div class="w-full h-2 rounded-full bg-black/20 overflow-hidden"><div class="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-700" :style="{ width: goal.calculated_progress + '%' }"></div></div>
            </div>
          </div>
        </div>

        <div v-show="mobileTab === 'ideas'" class="lg:hidden glass-card p-4 rounded-2xl border border-amber-500/30 bg-amber-500/5 flex flex-col">
          <div>
            <h3 class="text-base font-black text-amber-400 mb-3 flex items-center gap-2"><Lightbulb class="w-5 h-5" /> ایده برتر روز</h3>
            <div v-if="dashboardData.idea_of_the_day">
              <div class="flex items-center gap-1 mb-2">
                <span class="text-amber-300 font-bold text-[11px]">درجه هیجان:</span>
                <span class="text-amber-400 text-xs">★ {{ dashboardData.idea_of_the_day.excitement_rating || 5 }}</span>
              </div>
              <h4 class="text-sm font-bold mb-2" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.idea_of_the_day.title }}</h4>
              <p class="text-[11px] leading-relaxed line-clamp-5" :style="{ color: 'var(--text-secondary)' }">{{ dashboardData.idea_of_the_day.description || 'بدون توضیحات' }}</p>
            </div>
            <div v-else class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">ایده‌ای ثبت نشده است.</div>
          </div>
          <router-link to="/ideas" class="mt-3 w-full py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-bold transition text-center block">ورود به بانک ایده‌ها</router-link>
        </div>

      </div>

      <!-- اهداف کلان (محاسبه واقعی وزن‌دهی بر اساس SubGoals) + ایده برتر روز -->
      <div class="hidden lg:grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
        <div class="lg:col-span-2 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10">
          <div class="flex items-center justify-between mb-3 sm:mb-4">
            <h3 class="text-base sm:text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><Target class="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" /> پیشرفت واقعی اهداف کلان (بر اساس گام‌های عملیاتی)</h3>
            <router-link to="/goals" class="text-[11px] sm:text-xs text-purple-400 hover:underline">مشاهده همه اهداف</router-link>
          </div>

          <div v-if="dashboardData.goals.length === 0" class="text-center py-4 sm:py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">هیچ هدفی تعریف نشده است.</div>
          <div v-else class="space-y-3 sm:space-y-4">
            <div v-for="goal in dashboardData.goals" :key="goal.id" class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10">
              <div class="flex items-center justify-between mb-1.5 sm:mb-2">
                <span class="text-xs sm:text-sm font-bold" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</span>
                <span class="text-[11px] sm:text-xs font-black text-purple-400">{{ goal.calculated_progress }}%</span>
              </div>
              <div class="w-full h-2 rounded-full bg-black/20 overflow-hidden mb-1.5 sm:mb-2"><div class="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-700" :style="{ width: goal.calculated_progress + '%' }"></div></div>
            </div>
          </div>
        </div>

        <!-- ایده برتر روز (ثابت و با درجه هیجان بالا) -->
        <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-amber-500/30 bg-amber-500/5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3 sm:mb-4">
              <h3 class="text-base sm:text-lg font-black text-amber-400 flex items-center gap-2"><Lightbulb class="w-4 h-4 sm:w-5 sm:h-5" /> ایده برتر روز</h3>
              <router-link to="/ideas" class="text-[11px] sm:text-xs text-amber-400 hover:underline">بانک ایده‌ها</router-link>
            </div>
            <div v-if="dashboardData.idea_of_the_day">
              <div class="flex items-center gap-1 mb-2">
                <span class="text-amber-300 font-bold text-[11px] sm:text-xs">درجه هیجان:</span>
                <span class="text-amber-400 text-xs">★ {{ dashboardData.idea_of_the_day.excitement_rating || 5 }}</span>
              </div>
              <h4 class="text-sm sm:text-base font-bold mb-2" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.idea_of_the_day.title }}</h4>
              <p class="text-[11px] sm:text-xs leading-relaxed line-clamp-4" :style="{ color: 'var(--text-secondary)' }">{{ dashboardData.idea_of_the_day.description || 'بدون توضیحات' }}</p>
            </div>
          </div>
          <router-link to="/ideas" class="mt-3 sm:mt-4 w-full py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/30 rounded-xl text-[11px] sm:text-xs font-bold transition text-center block">ورود به بانک ایده‌ها</router-link>
        </div>

        <!-- کارت مهارت‌ها (جدید) -->
        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-amber-500/20 space-y-2 sm:space-y-3" v-if="skillsStats">
          <div class="flex items-center justify-between">
            <h3 class="text-sm sm:text-base font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <Award class="w-4 h-4 sm:w-5 sm:h-5 text-amber-400" />
              مهارت‌ها
            </h3>
            <router-link to="/skills" class="text-[11px] sm:text-xs text-amber-400 hover:underline">همه ←</router-link>
          </div>

          <div class="grid grid-cols-2 gap-2 sm:gap-3">
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
              <p class="text-[10px] font-bold text-gray-400">کل مهارت‌ها</p>
              <p class="text-lg sm:text-xl font-black text-amber-300 mt-0.5">{{ skillsStats.total_skills }}</p>
              <p class="text-[9px] text-amber-400/70 font-bold mt-0.5">
                {{ skillsStats.mastered }} تسلط · {{ skillsStats.in_progress }} در حال
              </p>
            </div>
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20">
              <p class="text-[10px] font-bold text-gray-400 flex items-center gap-1">
                <Flame class="w-3 h-3" /> Streak
              </p>
              <p class="text-lg sm:text-xl font-black text-orange-300 mt-0.5">{{ skillsStats.current_streak }} روز</p>
              <p class="text-[9px] text-orange-400/70 font-bold mt-0.5">رکورد: {{ skillsStats.longest_streak }} روز</p>
            </div>
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
              <p class="text-[10px] font-bold text-gray-400">میانگین پیشرفت</p>
              <p class="text-lg sm:text-xl font-black text-blue-300 mt-0.5">{{ skillsStats.overall_progress_avg }}٪</p>
            </div>
            <div class="p-2.5 sm:p-3 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
              <p class="text-[10px] font-bold text-gray-400">مستقل (بدون هدف)</p>
              <p class="text-lg sm:text-xl font-black text-purple-300 mt-0.5">{{ skillsStats.independent_skills }}</p>
              <p v-if="skillsStats.independent_skills > 0" class="text-[9px] text-purple-400/70 font-bold mt-0.5">
                شاید وقت اتصال به هدف
              </p>
            </div>
          </div>

          <router-link to="/skills" class="mt-1 sm:mt-2 w-full py-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/30 rounded-xl text-[11px] sm:text-xs font-bold transition text-center block">ورود به بانک مهارت‌ها</router-link>
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

<style scoped>
/* Transition برای popup تفکیک روز */
.popup-enter-active, .popup-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.popup-enter-from, .popup-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}
</style>