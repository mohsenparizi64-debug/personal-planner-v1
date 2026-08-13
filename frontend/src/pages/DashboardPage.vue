<script setup>
import { ref, computed, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import { useRouter } from 'vue-router'
import { 
  ListTodo, CheckCircle, Flame, TrendingUp, Zap, AlertTriangle, 
  Wallet, Lightbulb, Target, Calendar, Plus, RefreshCw, ArrowRight, Clock, Star
} from 'lucide-vue-next'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const router = useRouter()

const isLoading = ref(true)
const dashboardData = ref(null)
const quickTaskTitle = ref('')

const quotes = [
  "بهترین زمان برای کاشت یک درخت ۲۰ سال پیش بود، دومین زمان خوب همین الان است.",
  "موفقیت مجموعه‌ای از تلاش‌های کوچک است که هر روز تکرار می‌شوند.",
  "تمرکز یعنی گفتن «نه» به ۱۰۰ ایده خوب دیگر.",
  "انضباط شخصی یعنی انجام آنچه باید انجام شود، حتی زمانی که حوصله‌اش را ندارید."
]
const todayQuote = ref(quotes[Math.floor(Math.random() * quotes.length)])

// سلام هوشمند زمان‌بندی‌شده
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

// تیک زدن فوری تسک از داشبورد
const toggleTask = async (task) => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const updatedStatus = !task.is_completed
    await api.put(`/tasks/${task.id}`, {
      ...task,
      is_completed: updatedStatus,
      last_action_date: updatedStatus ? today : null
    })
    fetchDashboard()
  } catch (e) {
    alert('خطا در بروزرسانی تسک')
  }
}

// تمدید مهلت تسک عقب‌افتاده به امروز
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

// ثبت سریع تسک برای امروز
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

const maxWeeklyValue = computed(() => {
  if (!dashboardData.value?.weekly_activity) return 10
  const maxComp = Math.max(...dashboardData.value.weekly_activity.map(d => d.completed), 1)
  return Math.max(maxComp, 5)
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

      <!-- کادر جمله انگیزشی روز -->
      <div class="max-w-md bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-md">
        <p class="text-xs text-amber-400 font-bold mb-1 flex items-center gap-1">
          <Star class="w-3.5 h-3.5 fill-amber-400" /> الهام‌بخش روز:
        </p>
        <p class="text-xs leading-relaxed italic" :style="{ color: 'var(--text-primary)' }">« {{ todayQuote }} »</p>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-20" :style="{ color: 'var(--text-secondary)' }">
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
            <p class="text-2xl md:text-3xl font-black text-red-400">
              {{ dashboardData.summary.overdue_count }}
            </p>
          </div>
          <div class="w-12 h-12 bg-red-500/20 text-red-400 rounded-2xl flex items-center justify-center border border-red-500/30">
            <AlertTriangle class="w-6 h-6 animate-pulse" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-3xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">تحقق کارهای دوره‌ای</p>
            <p class="text-2xl md:text-3xl font-black text-emerald-400">
              {{ dashboardData.summary.recurring_completion_rate }}%
            </p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 text-emerald-400 rounded-2xl flex items-center justify-center border border-emerald-500/30">
            <TrendingUp class="w-6 h-6" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-3xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">کل دارایی مالی</p>
            <p class="text-lg md:text-xl font-black text-purple-400">
              {{ dashboardData.summary.total_balance.toLocaleString('fa-IR') }}
            </p>
          </div>
          <div class="w-12 h-12 bg-purple-500/20 text-purple-400 rounded-2xl flex items-center justify-center border border-purple-500/30">
            <Wallet class="w-6 h-6" />
          </div>
        </div>

      </div>

      <!-- 📊 بخش نمودارهای گرافیکی متحرک -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- نمودار ۱: روند فعالیت ۷ روز گذشته (Bar Chart) -->
        <div class="lg:col-span-2 glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <TrendingUp class="w-5 h-5 text-blue-400" /> نمودار فعالیت ۷ روز گذشته
            </h3>
            <span class="text-xs" :style="{ color: 'var(--text-secondary)' }">تسک‌های تکمیل‌شده در هفته</span>
          </div>

          <!-- رسم چارت میله‌ای با SVG -->
          <div class="h-48 flex items-end justify-between gap-2 pt-4 px-2 border-b border-white/10">
            <div 
              v-for="day in dashboardData.weekly_activity" 
              :key="day.date" 
              class="flex-1 flex flex-col items-center h-full justify-end group relative"
            >
              <div class="absolute -top-8 opacity-0 group-hover:opacity-100 transition bg-slate-900 border border-white/20 px-2 py-1 rounded text-[10px] text-white whitespace-nowrap z-20">
                {{ day.completed }} تسک تکمیل‌شده
              </div>

              <div 
                class="w-full max-w-[32px] bg-gradient-to-t from-blue-600 to-purple-500 rounded-t-xl transition-all duration-500 group-hover:brightness-125 shadow-lg shadow-blue-500/20"
                :style="{ height: Math.max((day.completed / maxWeeklyValue * 100), 8) + '%' }"
              ></div>

              <span class="text-[10px] font-bold mt-2" :style="{ color: 'var(--text-secondary)' }">{{ day.day_name }}</span>
            </div>
          </div>
        </div>

        <!-- نمودار ۲: دونات تفکیک تسک‌ها (Donut Chart) -->
        <div class="glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between">
          <h3 class="text-lg font-black flex items-center gap-2 mb-4" :style="{ color: 'var(--text-primary)' }">
            <Flame class="w-5 h-5 text-amber-400" /> تفکیک انواع تسک‌ها
          </h3>

          <div class="relative flex items-center justify-center my-2">
            <svg class="w-36 h-36 transform -rotate-90" viewBox="0 0 36 36">
              <path class="text-gray-300 dark:text-gray-800" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path class="text-purple-500" stroke-dasharray="60, 100" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path class="text-amber-400" stroke-dasharray="25, 100" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
            <div class="absolute text-center">
              <span class="text-xl font-black" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.summary.total_tasks_count }}</span>
              <p class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">کل تسک‌ها</p>
            </div>
          </div>

          <div class="space-y-2 text-xs pt-2 border-t border-white/5">
            <div class="flex items-center justify-between">
              <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block"></span> تسک‌های یک‌باره:</span>
              <span class="font-bold" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.summary.fixed_tasks_count }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="flex items-center gap-1.5" :style="{ color: 'var(--text-secondary)' }"><span class="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block"></span> تسک‌های دوره‌ای:</span>
              <span class="font-bold" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.summary.recurring_tasks_count }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- 🚨 کارهای عقب‌افتاده + کارهای امروز -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- کارهای عقب‌افتاده -->
        <div class="glass-card p-6 rounded-3xl border border-red-500/30 bg-red-500/5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-black text-red-400 flex items-center gap-2">
              <AlertTriangle class="w-5 h-5 animate-pulse" /> کارهای عقب‌افتاده نیاز به اقدام
            </h3>
            <span class="text-xs bg-red-500/20 text-red-300 px-2.5 py-1 rounded-full font-bold">
              {{ dashboardData.overdue_tasks.length }} مورد
            </span>
          </div>

          <div v-if="dashboardData.overdue_tasks.length === 0" class="text-center py-8 text-xs" :style="{ color: 'var(--text-secondary)' }">
            🎉 عالیه! هیچ کار عقب‌افتاده‌ای نداری.
          </div>

          <div v-else class="space-y-3 max-h-64 overflow-y-auto pr-1">
            <div 
              v-for="task in dashboardData.overdue_tasks" 
              :key="task.id"
              class="p-3.5 rounded-2xl bg-white/5 border border-red-500/20 flex items-center justify-between gap-3 hover:bg-white/10 transition"
            >
              <div>
                <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</p>
                <p class="text-[10px] text-red-400 font-bold">مهلت: {{ formatDate(task.due_date) }}</p>
              </div>

              <div class="flex items-center gap-1.5">
                <button @click="extendToToday(task)" class="px-2.5 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-[10px] font-bold hover:bg-amber-500/30 transition">
                  تمدید به امروز
                </button>
                <button @click="toggleTask(task)" class="px-2.5 py-1 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg text-[10px] font-bold hover:bg-green-500/30 transition">
                  تکمیل
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- کارهای امروز + ثبت سریع -->
        <div class="glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                <ListTodo class="w-5 h-5 text-blue-400" /> کارهای امروز
              </h3>
              <router-link to="/tasks" class="text-xs text-blue-400 hover:underline flex items-center gap-1">
                اتاق عملیات <ArrowRight class="w-3.5 h-3.5" />
              </router-link>
            </div>

            <div v-if="dashboardData.today_tasks.length === 0" class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">
              هیچ تسکی برای امروز ثبت نشده است.
            </div>

            <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
              <div 
                v-for="task in dashboardData.today_tasks" 
                :key="task.id"
                @click="toggleTask(task)"
                class="p-3 rounded-2xl bg-white/5 hover:bg-white/10 transition cursor-pointer flex items-center justify-between border border-white/5"
              >
                <div class="flex items-center gap-3">
                  <div class="w-5 h-5 rounded-lg border-2 flex items-center justify-center transition" :class="task.is_completed ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30'">
                    <CheckCircle v-if="task.is_completed" class="w-3.5 h-3.5" />
                  </div>
                  <span class="text-xs font-bold" :class="task.is_completed ? 'line-through opacity-40' : ''" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ثبت سریع تسک امروز -->
          <form @submit.prevent="addQuickTask" class="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <input 
              v-model="quickTaskTitle" 
              type="text" 
              placeholder="ثبت سریع تسک جدید برای امروز..." 
              class="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500"
              :style="{ color: 'var(--text-primary)' }"
            />
            <button type="submit" class="p-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl transition">
              <Plus class="w-4 h-4" />
            </button>
          </form>
        </div>

      </div>

      <!-- 🎯 پیشرفت واقعی اهداف + ایده پیشنهادی روز -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div class="lg:col-span-2 glass-card p-6 rounded-3xl border border-white/10">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
              <Target class="w-5 h-5 text-purple-400" /> پیشرفت واقعی اهداف کلان
            </h3>
            <router-link to="/goals" class="text-xs text-purple-400 hover:underline">مشاهده همه اهداف</router-link>
          </div>

          <div v-if="dashboardData.goals.length === 0" class="text-center py-6 text-xs" :style="{ color: 'var(--text-secondary)' }">
            هیچ هدفی تعریف نشده است.
          </div>

          <div v-else class="space-y-4">
            <div v-for="goal in dashboardData.goals" :key="goal.id" class="p-4 rounded-2xl bg-white/5 border border-white/10">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-bold" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</span>
                <span class="text-xs font-black text-purple-400">{{ goal.calculated_progress }}%</span>
              </div>
              <div class="w-full h-2 rounded-full bg-black/20 overflow-hidden mb-2">
                <div class="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-700" :style="{ width: goal.calculated_progress + '%' }"></div>
              </div>
              <div v-if="goal.next_step" class="text-[10px]" :style="{ color: 'var(--text-secondary)' }">
                📌 گام بعدی: <span class="font-bold" :style="{ color: 'var(--text-primary)' }">{{ goal.next_step }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ایده برتر روز -->
        <div class="glass-card p-6 rounded-3xl border border-amber-500/30 bg-amber-500/5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-black text-amber-400 flex items-center gap-2">
                <Lightbulb class="w-5 h-5" /> ایده برتر روز
              </h3>
              <router-link to="/ideas" class="text-xs text-amber-400 hover:underline">بانک ایده‌ها</router-link>
            </div>

            <div v-if="dashboardData.idea_of_the_day">
              <h4 class="text-base font-bold mb-2" :style="{ color: 'var(--text-primary)' }">{{ dashboardData.idea_of_the_day.title }}</h4>
              <p class="text-xs leading-relaxed line-clamp-4" :style="{ color: 'var(--text-secondary)' }">{{ dashboardData.idea_of_the_day.description || 'بدون توضیحات' }}</p>
            </div>
            <div v-else class="text-center py-8 text-xs" :style="{ color: 'var(--text-secondary)' }">
              هیچ ایده‌ای ثبت نشده است.
            </div>
          </div>

          <router-link to="/ideas" class="mt-4 w-full py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-bold transition text-center block">
            ورود به بانک ایده‌ها و پرورش ایده
          </router-link>
        </div>

      </div>

    </div>
  </div>
</template>