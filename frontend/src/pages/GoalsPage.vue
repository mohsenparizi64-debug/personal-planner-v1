<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, X, Target, Calendar, Flag, AlertTriangle, Zap, History, Clock, ArrowRight, Eye, Sparkles, ListTodo, PieChart } from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'
import { useRouter } from 'vue-router'

const themeStore = useThemeStore()
const goals = ref([])
const allTasks = ref([])  // همه کارها (برای progress واقعی)
const recentLogs = ref([])
const showForm = ref(false)
const showLogs = ref(false)
const editingGoal = ref(null)
const selectedGoal = ref(null) // <--- استیت مربوط به حالت تمرکز و فوکوس روی هدف
const isLoading = ref(false)
const validationErrors = ref({})
const router = useRouter()

// 🌌 نمایش سه‌بعدی در حالت تمرکز
const focusSubGoals = ref([])
const focusTasksBySub = ref({}) // map: subGoalId -> tasks[]
const focusLoading = ref(false)
const rotateY = ref(0)              // زاویه چرخش صحنه (درجه)
const rotateX = ref(-12)            // کمی خم به بالا برای حس سه‌بعدی
const isDragging = ref(false)
const autoRotate = ref(true)        // چرخش خودکار فعال
let dragStartX = 0
let dragStartY = 0
let rotateStartY = 0
let rotateStartX = 0
let autoRotateRAF = null

const fetchFocusRoadmap = async (goalId) => {
  focusLoading.value = true
  try {
    const res = await api.get(`/roadmap/goal/${goalId}/subgoals`)
    focusSubGoals.value = (res.data || []).map(sg => ({
      ...sg,
      tasks: sg.tasks || []
    }))
    // ساخت map برای دسترسی سریع
    const map = {}
    focusSubGoals.value.forEach(sg => { map[sg.id] = sg.tasks })
    focusTasksBySub.value = map
  } catch (e) {
    focusSubGoals.value = []
    focusTasksBySub.value = {}
  } finally {
    focusLoading.value = false
  }
}

const startAutoRotate = () => {
  const tick = () => {
    if (autoRotate.value && !isDragging.value) {
      rotateY.value = (rotateY.value + 0.18) % 360
    }
    autoRotateRAF = requestAnimationFrame(tick)
  }
  autoRotateRAF = requestAnimationFrame(tick)
}

const stopAutoRotate = () => {
  if (autoRotateRAF) cancelAnimationFrame(autoRotateRAF)
  autoRotateRAF = null
}

const onPointerDown = (e) => {
  isDragging.value = true
  autoRotate.value = false
  const t = e.touches ? e.touches[0] : e
  dragStartX = t.clientX
  dragStartY = t.clientY
  rotateStartX = rotateX.value
  rotateStartY = rotateY.value
}
const onPointerMove = (e) => {
  if (!isDragging.value) return
  e.preventDefault?.()
  const t = e.touches ? e.touches[0] : e
  const dx = t.clientX - dragStartX
  const dy = t.clientY - dragStartY
  rotateY.value = (rotateStartY + dx * 0.4) % 360
  // محدود کردن چرخش X برای جلوگیری از واژگونی
  rotateX.value = Math.max(-45, Math.min(45, rotateStartX - dy * 0.3))
}
const onPointerUp = () => {
  if (!isDragging.value) return
  isDragging.value = false
  // بعد از ۴ ثانیه بدون تعامل، چرخش خودکار برگردد
  setTimeout(() => { if (!isDragging.value) autoRotate.value = true }, 4000)
}
const toggleAutoRotate = () => { autoRotate.value = !autoRotate.value }

const goToRoadmap = (goalId) => {
  sessionStorage.setItem('active_goal_id', goalId)
  router.push('/roadmap')
}

// لینک سریع به کارهای یک هدف (با فیلتر خودکار)
const goToTasks = (goalId) => {
  router.push({ path: '/tasks', query: { goal: goalId } })
}

// انتخاب هدف برای حالت تمرکز (Spotlight Focus)
const selectGoalForFocus = async (goal) => {
  selectedGoal.value = goal
  await fetchFocusRoadmap(goal.id)
  rotateY.value = 0
  rotateX.value = -12
  autoRotate.value = true
  startAutoRotate()
}

const closeFocusMode = () => {
  selectedGoal.value = null
  stopAutoRotate()
  focusSubGoals.value = []
  focusTasksBySub.value = {}
}

const form = ref({
  title: '',
  description: '',
  start_date: '',
  target_date: '',
  current_status: '',
  current_obstacle: '',
  next_step: '',
  priority: 0,
  success_criteria: ''
})

const priorityLabels = ['عادی', 'متوسط', 'فوری']
const priorityColors = ['text-gray-400', 'text-orange-400', 'text-red-400']

const fetchGoals = async () => {
  try {
    const response = await api.get('/goals')
    goals.value = response.data
    // اگر هدفی در حالت فوکوس بود، اطلاعاتش آپدیت شود
    if (selectedGoal.value) {
      const updated = goals.value.find(g => g.id === selectedGoal.value.id)
      if (updated) selectedGoal.value = updated
    }
  } catch (error) {
    console.error('خطا در گرفتن اهداف', error)
  }
}

const fetchAllTasks = async () => {
  try {
    const response = await api.get('/tasks')
    allTasks.value = response.data
  } catch (error) {
    console.error('خطا در گرفتن کارها', error)
  }
}

// 📊 محاسبه progress واقعی از کارها (نه فیلد progress_percent که دستیه)
const progressByGoal = (goalId) => {
  const goalTasks = allTasks.value.filter(t => t.goal_id === goalId)
  if (goalTasks.length === 0) return 0
  const completed = goalTasks.filter(t => t.is_completed).length
  return Math.round((completed / goalTasks.length) * 100)
}

const tasksCountByGoal = (goalId) => {
  return allTasks.value.filter(t => t.goal_id === goalId).length
}

const completedTasksByGoal = (goalId) => {
  return allTasks.value.filter(t => t.goal_id === goalId && t.is_completed).length
}

// 📊 تفکیک اهداف بر اساس درصد پیشرفت واقعی
const goalsByProgress = computed(() => {
  const buckets = {
    completed: { label: 'تکمیل‌شده (۱۰۰٪)', goals: [], color: '#10b981' },   // سبز
    active:    { label: 'در جریان (۱-۹۹٪)', goals: [], color: '#f59e0b' },    // طلایی
    planning:  { label: 'فقط برنامه‌ریزی (۰٪)', goals: [], color: '#6366f1' }, // بنفش
  }
  goals.value.forEach(g => {
    const p = progressByGoal(g.id)
    if (p >= 100) buckets.completed.goals.push(g)
    else if (p > 0) buckets.active.goals.push(g)
    else buckets.planning.goals.push(g)
  })
  return buckets
})

// محاسبه درصد برای Donut
const donutSegments = computed(() => {
  const segs = []
  const total = goals.value.length
  if (total === 0) return segs
  let offset = 0
  Object.values(goalsByProgress.value).forEach(b => {
    const pct = (b.goals.length / total) * 100
    if (pct > 0) {
      segs.push({ ...b, percent: pct, offset })
      offset += pct
    }
  })
  return segs
})

// 📅 Timeline: کارهای ۳۰ روز آینده (سررسید نزدیک)
const upcomingTasks = computed(() => {
  const now = new Date()
  const today = now.toISOString().split('T')[0]
  const future = new Date(now)
  future.setDate(future.getDate() + 30)
  const futureISO = future.toISOString().split('T')[0]
  return allTasks.value
    .filter(t => !t.is_completed && t.due_date)
    .map(t => ({ ...t, dueDateStr: String(t.due_date).split('T')[0] }))
    .filter(t => t.dueDateStr >= today && t.dueDateStr <= futureISO)
    .sort((a, b) => a.dueDateStr.localeCompare(b.dueDateStr))
    .slice(0, 10)
})

// 🚀 Quick action: مستقیم به صفحه کار جدید (با goal context)
const quickAddTask = (goalId) => {
  router.push({ path: '/tasks', query: { goal: goalId, add: '1' } })
}

// 💡 Smart suggestion: پیشنهاد از next_step فیلد goal (اگه پر باشه)
const smartSuggestion = computed(() => {
  // اولویت: goals که next_step دارن و پیشرفت < 50٪
  const candidates = goals.value
    .filter(g => g.next_step && g.next_step.trim() && progressByGoal(g.id) < 50)
    .sort((a, b) => progressByGoal(a.id) - progressByGoal(b.id))  // کمترین پیشرفت اول
  if (candidates.length === 0) return null
  return candidates[0]
})

// 🌌 محاسبه موقعیت گره‌های سه‌بعدی برای نمایش در حالت تمرکز
// چیدمان: گام‌ها به‌صورت دایره‌ای روی یک استوانه در فاصله‌های z متفاوت
// لایه‌بندی: هر ۶ گام در یک «ردیف» عمق
const focusSceneLayers = computed(() => {
  const layers = []
  const perLayer = 6
  for (let i = 0; i < focusSubGoals.value.length; i += perLayer) {
    layers.push(focusSubGoals.value.slice(i, i + perLayer))
  }
  return layers
})

const subGoalProgress = (sg) => {
  const tasks = (sg.tasks || [])
  if (tasks.length === 0) return 0
  const done = tasks.filter(t => t.is_completed).length
  return Math.round((done / tasks.length) * 100)
}

// موقعیت هر گره گام در دایره (theta = زاویه روی دایره)
const nodePosition = (indexInLayer, layerIndex, totalInLayer) => {
  const radius = 180                              // شعاع دایره
  const layerSpacing = 130                        // فاصله لایه‌ها
  const angle = (360 / Math.max(totalInLayer, 1)) * indexInLayer
  const rad = (angle * Math.PI) / 180
  const x = Math.cos(rad) * radius
  const z = Math.sin(rad) * radius
  const y = layerIndex * layerSpacing
  return { x, y, z, angle }
}

const fetchLogs = async () => {
  try {
    const response = await api.get('/goals/logs?limit=15')
    recentLogs.value = response.data
  } catch (error) {
    console.error('خطا در گرفتن لاگ‌ها', error)
  }
}

const resetForm = () => {
  form.value = {
    title: '', description: '', start_date: '', target_date: '',
    current_status: '', current_obstacle: '', next_step: '',
    priority: 0, success_criteria: ''
  }
  editingGoal.value = null
  validationErrors.value = {}
}

const openNewForm = () => {
  resetForm()
  showForm.value = true
}

const openEditForm = (goal) => {
  form.value = {
    title: goal.title,
    description: goal.description || '',
    start_date: goal.start_date || '',
    target_date: goal.target_date || '',
    current_status: goal.current_status || '',
    current_obstacle: goal.current_obstacle || '',
    next_step: goal.next_step || '',
    priority: goal.priority,
    success_criteria: goal.success_criteria || ''
  }
  editingGoal.value = goal
  validationErrors.value = {}
  showForm.value = true
}

const saveGoal = async () => {
  validationErrors.value = {}
  let hasError = false
  
  if (!form.value.title || !form.value.title.trim()) {
    validationErrors.value.title = 'عنوان هدف اجباری است'
    hasError = true
  }
  
  // مقایسه دقیق و استاندارد تاریخ شمسی/میلادی
  if (form.value.start_date && form.value.target_date) {
    const startStr = String(form.value.start_date).replace(/\//g, '-')
    const targetStr = String(form.value.target_date).replace(/\//g, '-')
    
    if (targetStr < startStr) {
      validationErrors.value.target_date = 'تاریخ تحقق نمی‌تواند قبل از تاریخ تعریف باشد'
      hasError = true
    }
  }
  
  if (hasError) {
    showToast('⚠️ لطفاً خطاهای فرم را برطرف کنید', 'error')
    return
  }
  
  isLoading.value = true
  try {
    if (editingGoal.value) {
      await api.put(`/goals/${editingGoal.value.id}`, form.value)
      showToast('✅ هدف با موفقیت بروزرسانی شد')
    } else {
      await api.post('/goals', form.value)
      showToast('✅ هدف جدید با موفقیت ایجاد شد')
    }
    showForm.value = false
    resetForm()
    await fetchGoals()
    await fetchLogs()
  } catch (error) {
    const detail = error.response?.data?.detail
    if (error.response?.status === 422) {
      showToast('⚠️ لطفاً اطلاعات را کامل و صحیح وارد کنید', 'error')
    } else if (detail) {
      showToast('❌ ' + detail, 'error')
    } else {
      showToast('❌ خطا در ذخیره هدف', 'error')
    }
  } finally {
    isLoading.value = false
  }
}

const deleteGoal = async (goalId) => {
  if (!confirm('مطمئنی می‌خوای این هدف رو حذف کنی؟')) return
  try {
    await api.delete(`/goals/${goalId}`)
    if (selectedGoal.value && selectedGoal.value.id === goalId) {
      selectedGoal.value = null
    }
    await fetchGoals()
    await fetchLogs()
    showToast('🗑️ هدف حذف شد')
  } catch (error) {
    console.error('خطا در حذف هدف', error)
  }
}

const resetAllGoals = async () => {
  if (!confirm('همه اهداف حذف بشن؟ این کار قابل بازگشت نیست!')) return
  try {
    await api.delete('/goals/all/reset')
    selectedGoal.value = null
    await fetchGoals()
    await fetchLogs()
    showToast('🗑️ همه اهداف حذف شدند')
  } catch (error) {
    console.error('خطا در حذف همه اهداف', error)
  }
}

const showToast = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

const message = ref('')
const messageType = ref('success')

onMounted(() => {
  fetchGoals()
  fetchAllTasks()  // برای progress واقعی
  fetchLogs()
})

onUnmounted(() => {
  stopAutoRotate()
})
</script>

<template>
  <div 
    class="p-3 sm:p-4 md:p-8 lg:p-10 max-w-7xl mx-auto relative z-10 min-h-screen text-right" dir="rtl"
    :class="themeStore.currentTheme === 'persian-classic' ? 'page-bg-tasks' : themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''"
  >
    <!-- الگوی اسلیمی -->
    <div v-if="themeStore.currentTheme === 'persian-classic'" class="absolute inset-0 persian-pattern opacity-20 pointer-events-none"></div>
    
    <!-- ذرات رباتیک -->
    <div v-if="themeStore.currentTheme === 'cyber-digital'" class="particles">
      <div v-for="i in 15" :key="i" class="particle" :style="{ left: Math.random() * 100 + '%', animationDelay: Math.random() * 4 + 's' }"></div>
    </div>

    <!-- 📊 نمودار Donut: تفکیک اهداف بر اساس پیشرفت -->
    <div v-if="goals.length > 0" class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 mb-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 items-center">
        <!-- Donut SVG -->
        <div class="flex flex-col items-center">
          <h3 class="text-sm sm:text-base font-black mb-3 flex items-center gap-2">
            <PieChart class="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" />
            تفکیک پیشرفت اهداف ({{ goals.length }} هدف)
          </h3>
          <div class="relative w-36 h-36 sm:w-44 sm:h-44">
            <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
              <circle cx="18" cy="18" r="15.9155" fill="transparent" stroke="rgba(255,255,255,0.05)" stroke-width="3" />
              <circle v-for="(seg, i) in donutSegments" :key="i"
                      cx="18" cy="18" r="15.9155" fill="transparent"
                      :stroke="seg.color"
                      stroke-width="3"
                      :stroke-dasharray="`${seg.percent} ${100 - seg.percent}`"
                      :stroke-dashoffset="-seg.offset"
                      class="transition-all duration-500" />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <p class="text-[10px] opacity-60">تعداد کل</p>
              <p class="text-2xl font-black">{{ goals.length }}</p>
            </div>
          </div>
        </div>

        <!-- لژند + آمار -->
        <div class="space-y-3">
          <div v-for="(seg, i) in donutSegments" :key="i"
               class="flex items-center gap-2 sm:gap-3 p-2.5 sm:p-3 rounded-xl bg-white/5 border border-white/5">
            <div class="w-3 h-3 sm:w-4 sm:h-4 rounded-sm flex-shrink-0" :style="{ background: seg.color }"></div>
            <div class="flex-1 min-w-0">
              <p class="text-xs sm:text-sm font-bold truncate">{{ seg.label }}</p>
              <p class="text-[10px] sm:text-xs opacity-60">{{ seg.goals.length }} هدف</p>
            </div>
            <p class="font-black text-sm sm:text-base" :style="{ color: seg.color }">{{ Math.round(seg.percent) }}٪</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 📅 Timeline: کارهای پیش‌رو (۳۰ روز آینده) -->
    <div v-if="upcomingTasks.length > 0" class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 mb-5">
      <h3 class="text-sm sm:text-base font-black mb-3 flex items-center gap-2">
        <Calendar class="w-4 h-4 sm:w-5 sm:h-5 text-amber-400" />
        سررسیدهای پیش‌رو ({{ upcomingTasks.length }} کار)
      </h3>
      <div class="space-y-2">
        <div v-for="t in upcomingTasks" :key="t.id"
             class="flex items-center gap-2 sm:gap-3 p-2.5 sm:p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition">
          <!-- دایره رنگی بر اساس فوریت -->
          <div class="w-2 h-2 rounded-full flex-shrink-0"
               :class="{
                 'bg-red-500': new Date(t.dueDateStr) - new Date() < 3*24*60*60*1000,
                 'bg-amber-500': new Date(t.dueDateStr) - new Date() < 7*24*60*60*1000,
                 'bg-blue-500': true
               }"></div>
          <!-- عنوان کار -->
          <div class="flex-1 min-w-0">
            <p class="text-xs sm:text-sm font-bold truncate">{{ t.title }}</p>
            <p class="text-[10px] sm:text-xs opacity-60 truncate">
              {{ goals.find(g => g.id === t.goal_id)?.title || 'بدون هدف' }}
            </p>
          </div>
          <!-- تاریخ سررسید -->
          <div class="text-left flex-shrink-0">
            <p class="text-[10px] sm:text-xs font-bold text-amber-300" dir="ltr">{{ t.dueDateStr }}</p>
            <p class="text-[9px] sm:text-[10px] opacity-50">سررسید</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 💡 Smart Suggestion -->
    <div v-if="smartSuggestion" class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-amber-500/30 bg-amber-500/5 mb-5">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
          <Sparkles class="w-5 h-5 sm:w-6 sm:h-6" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-[10px] sm:text-xs font-black opacity-60 mb-1">💡 پیشنهاد هوشمند بعدی</p>
          <p class="text-sm sm:text-base font-bold mb-1 truncate">{{ smartSuggestion.title }}</p>
          <p class="text-xs sm:text-sm leading-relaxed text-amber-200/90 line-clamp-2">{{ smartSuggestion.next_step }}</p>
          <div class="flex items-center gap-2 mt-2">
            <button @click="quickAddTask(smartSuggestion.id)" class="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-900 font-black text-[10px] sm:text-xs flex items-center gap-1">
              <Plus class="w-3 h-3" /> افزودن کار
            </button>
            <span class="text-[10px] opacity-50">پیشرفت فعلی: {{ progressByGoal(smartSuggestion.id) }}٪</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Message -->
    <div v-if="message" 
         class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between mb-6 relative">
      <div>
        <h1 class="text-3xl font-extrabold flex items-center gap-2" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">
          <Target class="w-8 h-8 text-purple-400" /> اهداف کلان
        </h1>
        <p :style="{ color: 'var(--text-secondary)' }">مسیر موفقیتت رو در نمای دو ستونه و حالت تمرکز مدیریت کن</p>
      </div>
      <div class="flex gap-3">
        <button @click="resetAllGoals"
                class="px-4 py-2 rounded-xl transition text-sm hover:bg-red-500/10"
                :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <Trash2 class="w-4 h-4 inline ml-1" /> حذف همه
        </button>
        <button @click="openNewForm"
                class="px-5 py-2 text-white font-semibold rounded-xl transition flex items-center gap-2 shadow-lg hover:scale-105"
                :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> هدف جدید
        </button>
      </div>
    </div>

    <!-- Recent Activity Timeline -->
    <div class="mb-10 relative">
      <button @click="showLogs = !showLogs"
              class="flex items-center gap-2 text-sm mb-4 transition font-bold"
              :style="{ color: 'var(--accent)' }">
        <History class="w-5 h-5" />
        <span>آخرین تغییرات و لاگ‌ها</span>
        <span :class="showLogs ? 'rotate-90' : ''" class="transition-transform inline-block">▶</span>
        <span class="text-xs px-2 py-0.5 rounded-full" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">{{ recentLogs.length }}</span>
      </button>

      <div v-if="showLogs" class="space-y-3">
        <div v-if="recentLogs.length === 0" class="text-center py-4 rounded-xl opacity-60" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          هنوز تغییری ثبت نشده.
        </div>
        
        <div v-for="log in recentLogs" :key="log.id"
             class="flex items-start gap-3 p-3.5 rounded-2xl transition border"
             :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
          
          <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm"
               :style="{ 
                 background: log.action === 'created' ? 'rgba(34,197,94,0.2)' : 
                             log.action === 'deleted' ? 'rgba(239,68,68,0.2)' : 
                             'rgba(139,92,246,0.2)' 
               }">
            <Plus v-if="log.action === 'created'" class="w-4 h-4 text-green-500" />
            <Edit3 v-else-if="log.action === 'updated'" class="w-4 h-4 text-purple-400" />
            <Trash2 v-else class="w-4 h-4 text-red-400" />
          </div>

          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold" :style="{ color: 'var(--text-primary)' }">{{ log.description }}</p>
            <div class="flex items-center gap-3 mt-1.5">
              <span class="text-[10px] px-2 py-0.5 rounded-md font-bold"
                    :style="{ 
                      background: log.action === 'created' ? 'rgba(34,197,94,0.15)' : 
                                  log.action === 'deleted' ? 'rgba(239,68,68,0.15)' : 
                                  'rgba(139,92,246,0.15)',
                      color: log.action === 'created' ? '#22c55e' : 
                             log.action === 'deleted' ? '#ef4444' : '#8b5cf6'
                    }">
                {{ log.action === 'created' ? 'ایجاد' : log.action === 'deleted' ? 'حذف' : 'بروزرسانی' }}
              </span>
              <span class="text-xs opacity-60 flex items-center gap-1" :style="{ color: 'var(--text-secondary)' }">
                <Clock class="w-3 h-3" /> {{ formatDate(log.created_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Modal -->
    <div v-if="showForm" class="fixed inset-0 z-[180] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div class="w-full max-w-2xl rounded-3xl p-8 max-h-[90vh] overflow-y-auto shadow-2xl border"
           :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingGoal ? 'ویرایش هدف کلان' : 'تعریف هدف جدید' }}</h2>
          <button @click="showForm = false" :style="{ color: 'var(--text-secondary)' }">
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="space-y-4">
          <!-- عنوان -->
          <div>
            <label class="block text-sm mb-1" :style="{ color: validationErrors.title ? '#ef4444' : 'var(--text-secondary)' }">
              عنوان هدف کلان * {{ validationErrors.title ? '⚠️' : '' }}
            </label>
            <input v-model="form.title" type="text" placeholder="مثلاً: راه‌اندازی کسب‌وکار آنلاین"
                   class="w-full px-4 py-3 rounded-xl transition text-right outline-none border"
                   :style="{ 
                     background: 'var(--bg-primary)', 
                     borderColor: validationErrors.title ? '#ef4444' : 'var(--border)', 
                     color: 'var(--text-primary)' 
                   }" />
            <p v-if="validationErrors.title" class="text-red-400 text-xs mt-1 mr-1">{{ validationErrors.title }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">تاریخ تعریف هدف</label>
              <DateInputPersian v-model="form.start_date" placeholder="تاریخ تعریف هدف" />
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70" :style="{ color: validationErrors.target_date ? '#ef4444' : 'var(--text-secondary)' }">
                تاریخ تحقق هدف {{ validationErrors.target_date ? '⚠️' : '' }}
              </label>
              <DateInputPersian v-model="form.target_date" placeholder="تاریخ تحقق هدف" />
              <p v-if="validationErrors.target_date" class="text-red-400 text-xs mt-1 mr-1">{{ validationErrors.target_date }}</p>
            </div>
          </div>

          <div>
            <label class="block text-sm mb-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">آخرین وضعیت</label>
            <textarea v-model="form.current_status" rows="2" placeholder="الان کجای کاری؟"
                      class="w-full px-4 py-3 rounded-xl transition text-right outline-none border"
                      :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>

          <div>
            <label class="block text-sm mb-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">مانع فعلی تحقق</label>
            <textarea v-model="form.current_obstacle" rows="2" placeholder="چه چیزی جلوت رو گرفته؟"
                      class="w-full px-4 py-3 rounded-xl transition text-right outline-none border"
                      :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>

          <div>
            <label class="block text-sm mb-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">گام بعدی</label>
            <input v-model="form.next_step" type="text" placeholder="قدم بعدی چیه؟"
                   class="w-full px-4 py-3 rounded-xl transition text-right outline-none border"
                   :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">اولویت</label>
              <select v-model="form.priority"
                      class="w-full px-4 py-3 rounded-xl transition text-right outline-none border"
                      :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
                <option :value="0">عادی</option>
                <option :value="1">متوسط</option>
                <option :value="2">فوری</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">معیار موفقیت</label>
              <input v-model="form.success_criteria" type="text" placeholder="از کجا بفهمی موفق شدی؟"
                     class="w-full px-4 py-3 rounded-xl transition text-right outline-none border"
                     :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
            </div>
          </div>
        </div>

        <div class="flex gap-3 mt-8">
          <button @click="saveGoal" :disabled="isLoading"
                  class="flex-1 py-3.5 text-white font-bold rounded-2xl transition disabled:opacity-50 shadow-lg"
                  :style="{ background: 'var(--accent)' }">
            {{ editingGoal ? 'بروزرسانی هدف' : 'ایجاد هدف' }}
          </button>
          <button @click="showForm = false"
                  class="px-6 py-3.5 rounded-2xl font-semibold transition"
                  :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
            انصراف
          </button>
        </div>
      </div>
    </div>

    <!-- Goals List (Empty State) -->
    <div v-if="goals.length === 0" class="text-center py-20 relative">
      <Target class="w-16 h-16 mx-auto mb-4 opacity-40" :style="{ color: 'var(--accent)' }" />
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">هنوز هیچ هدفی تعریف نکردی!</p>
      <p :style="{ color: 'var(--text-secondary)' }">اولین هدف رو بساز و مسیر موفقیتت رو شروع کن.</p>
      <button @click="openNewForm"
              class="mt-6 px-8 py-3 text-white font-semibold rounded-2xl transition inline-flex items-center gap-2 shadow-lg hover:scale-105"
              :style="{ background: 'var(--accent)' }">
        <Plus class="w-5 h-5" /> ساخت اولین هدف
      </button>
    </div>

    <!-- 🌟 چیدمان اصلی اهداف (ریسپانسیو حرفه‌ای: موبایل تک ستونه استاندارد، تبلت ۲ ستونه، دسکتاپ ۳ ستونه با کارت‌های کامپکت و متناسب) -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 relative">
      <div v-for="goal in goals" :key="goal.id"
           @click="selectGoalForFocus(goal)"
           class="rounded-3xl p-5 sm:p-6 transition-all duration-300 border shadow-md hover:shadow-2xl hover:-translate-y-1 cursor-pointer flex flex-col justify-between group relative overflow-hidden"
           :class="themeStore.currentTheme === 'persian-classic' ? 'card-ornament' : themeStore.currentTheme === 'cyber-digital' ? 'neon-border' : ''"
           :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        
        <div>
          <!-- Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0 pr-2">
              <div class="flex items-center gap-2 mb-1.5">
                <Target class="w-5 h-5 flex-shrink-0 group-hover:rotate-12 transition-transform" :style="{ color: 'var(--accent)' }" />
                <h3 class="text-base sm:text-lg font-black truncate group-hover:text-purple-400 transition" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</h3>
              </div>
              <span :class="[priorityColors[goal.priority], 'text-[10px] sm:text-[11px] font-extrabold flex items-center gap-1 bg-white/5 px-2 py-0.5 rounded-lg w-fit']">
                <Flag class="w-3 h-3" /> {{ priorityLabels[goal.priority] }}
              </span>
            </div>

            <div class="flex gap-1 flex-shrink-0" @click.stop>
              <button @click="openEditForm(goal)" title="ویرایش" class="p-1.5 rounded-xl transition hover:bg-white/10 text-gray-400 hover:text-white">
                <Edit3 class="w-4 h-4" />
              </button>
              <button @click="deleteGoal(goal.id)" title="حذف" class="p-1.5 rounded-xl transition hover:bg-red-500/10 text-gray-400 hover:text-red-400">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <p v-if="goal.description" :style="{ color: 'var(--text-secondary)' }" class="text-xs opacity-80 mb-3 line-clamp-2 leading-relaxed">{{ goal.description }}</p>

          <!-- خلاصه فیلدها در کارت -->
          <div class="space-y-1.5 border-t pt-2.5 text-xs" :style="{ borderColor: 'var(--border)' }">
            <div v-if="goal.next_step" class="flex items-center gap-2 font-medium" :style="{ color: 'var(--accent)' }">
              <Check class="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
              <span class="truncate">گام بعدی: {{ goal.next_step }}</span>
            </div>
            <div v-if="goal.target_date" class="flex items-center gap-2 opacity-70" :style="{ color: 'var(--text-secondary)' }">
              <Calendar class="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
              <span>تحقق: {{ formatDate(goal.target_date) }}</span>
            </div>
          </div>
        </div>

        <!-- دکمه‌های پایینی کارت -->
        <div class="flex items-center justify-between gap-1.5 mt-4 pt-3 border-t flex-wrap sm:flex-nowrap" :style="{ borderColor: 'var(--border)' }" @click.stop>
          <button @click="selectGoalForFocus(goal)" class="px-2.5 py-1.5 rounded-xl font-bold text-[11px] bg-white/5 hover:bg-white/10 text-white transition flex items-center gap-1">
            <Eye class="w-3.5 h-3.5 text-amber-400" />
            <span>تمرکز</span>
          </button>

          <button @click="goToRoadmap(goal.id)"
                  class="px-3 py-1.5 rounded-xl font-bold text-[11px] text-white transition flex items-center gap-1 shadow-md hover:scale-105 active:scale-95 bg-gradient-to-r from-purple-600 to-indigo-600">
            <span>نقشه راه</span>
            <span>➔</span>
          </button>

          <!-- دکمه کارها -->
          <button @click.stop="goToTasks(goal.id)"
                  class="px-2.5 py-1.5 rounded-xl font-bold text-[11px] bg-white/5 hover:bg-white/10 text-white transition flex items-center gap-1">
            <ListTodo class="w-3.5 h-3.5 text-emerald-400" />
            <span>{{ completedTasksByGoal(goal.id) }}/{{ tasksCountByGoal(goal.id) }}</span>
          </button>

          <!-- 🚀 Quick add کار جدید -->
          <button @click.stop="quickAddTask(goal.id)"
                  class="px-2 py-1.5 rounded-xl font-bold text-[11px] bg-emerald-600/80 hover:bg-emerald-500 text-white transition flex items-center gap-1"
                  title="افزودن سریع کار">
            <Plus class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Progress واقعی از کارها -->
        <div class="mt-3 pt-3 border-t border-white/5">
          <div class="flex items-center justify-between text-[10px] mb-1.5">
            <span class="opacity-70 font-bold">پیشرفت واقعی (محاسبه از کارها)</span>
            <span class="font-black text-amber-300">{{ progressByGoal(goal.id) }}%</span>
          </div>
          <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-amber-500 to-emerald-400 transition-all"
                 :style="{ width: progressByGoal(goal.id) + '%' }"></div>
          </div>
        </div>      </div>
    </div>

    <!-- 🌟 حالت تمرکز هوشمند و سه‌بعدی روی هدف انتخابی (Spotlight Focus Mode) -->
    <div v-if="selectedGoal" class="fixed inset-0 z-[150] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-300" @click.self="closeFocusMode">
      
      <div class="w-full max-w-3xl rounded-3xl p-8 max-h-[90vh] overflow-y-auto border-2 border-purple-500/50 shadow-[0_0_60px_rgba(168,85,247,0.3)] bg-slate-900 text-white relative animate-in zoom-in-95 duration-300">
        
        <!-- دکمه‌های بالای کارت تمرکز -->
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
          
          <!-- دکمه اصلی بازگشت به لیست اهداف -->
          <button @click="closeFocusMode" class="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-black rounded-2xl shadow-xl transition flex items-center gap-2 hover:scale-105">
            <ArrowRight class="w-5 h-5" />
            <span>بازگشت به لیست اهداف</span>
          </button>

          <div class="flex items-center gap-2">
            <button @click="openEditForm(selectedGoal)" class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <Edit3 class="w-4 h-4 text-purple-400" /> ویرایش
            </button>
            <button @click="deleteGoal(selectedGoal.id)" class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <Trash2 class="w-4 h-4" /> حذف
            </button>
          </div>
        </div>

        <!-- نشان ویژه تمرکز -->
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-extrabold text-xs mb-3">
          <Sparkles class="w-4 h-4 animate-spin" /> حالت تمرکز سه‌بعدی روی هدف
        </div>

        <!-- عنوان هدف -->
        <div class="flex items-start justify-between gap-4 mb-6">
          <div>
            <h2 class="text-2xl md:text-3xl font-black text-white mb-2 flex items-center gap-3">
              <Target class="w-8 h-8 text-purple-400" /> {{ selectedGoal.title }}
            </h2>
            <p v-if="selectedGoal.description" class="text-sm text-gray-300 leading-relaxed">{{ selectedGoal.description }}</p>
          </div>
          <span :class="[priorityColors[selectedGoal.priority], 'text-xs font-black bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 flex items-center gap-1.5 whitespace-nowrap']">
            <Flag class="w-4 h-4" /> {{ priorityLabels[selectedGoal.priority] }}
          </span>
        </div>

        <!-- گرید کامل و بزرگ ۸ فیلد شناسنامه هدف -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          
          <div v-if="selectedGoal.start_date" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3">
            <div class="p-2.5 bg-blue-500/20 text-blue-400 rounded-xl"><Calendar class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] text-gray-400 font-bold">تاریخ تعریف هدف</p>
              <p class="text-sm font-bold text-white">{{ formatDate(selectedGoal.start_date) }}</p>
            </div>
          </div>

          <div v-if="selectedGoal.target_date" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3">
            <div class="p-2.5 bg-purple-500/20 text-purple-400 rounded-xl"><Calendar class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] text-gray-400 font-bold">تاریخ تحقق هدف</p>
              <p class="text-sm font-bold text-white">{{ formatDate(selectedGoal.target_date) }}</p>
            </div>
          </div>

          <div v-if="selectedGoal.current_status" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-start gap-3">
            <div class="p-2.5 bg-amber-500/20 text-amber-400 rounded-xl"><Zap class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] text-gray-400 font-bold">آخرین وضعیت</p>
              <p class="text-sm font-bold text-amber-300">{{ selectedGoal.current_status }}</p>
            </div>
          </div>

          <div v-if="selectedGoal.current_obstacle" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-start gap-3">
            <div class="p-2.5 bg-red-500/20 text-red-400 rounded-xl"><AlertTriangle class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] text-gray-400 font-bold">مانع فعلی تحقق</p>
              <p class="text-sm font-bold text-red-300">{{ selectedGoal.current_obstacle }}</p>
            </div>
          </div>

          <div v-if="selectedGoal.next_step" class="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3 md:col-span-2">
            <div class="p-2.5 bg-emerald-500/20 text-emerald-400 rounded-xl"><Check class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] text-emerald-400 font-bold">گام بعدی اجرایی</p>
              <p class="text-base font-black text-emerald-300">{{ selectedGoal.next_step }}</p>
            </div>
          </div>

          <div v-if="selectedGoal.success_criteria" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-start gap-3 md:col-span-2">
            <div class="p-2.5 bg-green-500/20 text-green-400 rounded-xl"><Target class="w-5 h-5" /></div>
            <div>
              <p class="text-[10px] text-gray-400 font-bold">معیار موفقیت (چطور بفهمم موفق شدم؟)</p>
              <p class="text-sm font-bold text-green-300">{{ selectedGoal.success_criteria }}</p>
            </div>
          </div>

        </div>

        <!-- 🌌 نمایش سه‌بعدی چرخشی: گام‌ها + کارهای هدف انتخابی -->
        <div class="mt-6 mb-4">
          <div class="flex items-center justify-between mb-3 px-1">
            <h3 class="text-sm font-black flex items-center gap-2 text-white">
              <Sparkles class="w-4 h-4 text-amber-400" />
              نقشه سه‌بعدی گام‌ها
              <span v-if="focusSubGoals.length" class="text-[10px] opacity-60 font-bold">({{ focusSubGoals.length }} گام)</span>
            </h3>
            <div class="flex items-center gap-1.5">
              <button @click="toggleAutoRotate" :title="autoRotate ? 'توقف چرخش خودکار' : 'شروع چرخش خودکار'"
                      class="px-2.5 py-1 rounded-lg text-[10px] font-bold transition"
                      :style="autoRotate ? { background: 'rgba(34,197,94,0.15)', color: '#22c55e' } : { background: 'rgba(255,255,255,0.05)', color: '#9ca3af' }">
                {{ autoRotate ? '⏸ توقف' : '▶ چرخش' }}
              </button>
            </div>
          </div>

          <!-- حالت بارگذاری -->
          <div v-if="focusLoading" class="h-72 flex items-center justify-center text-white/50 text-sm rounded-3xl border border-white/10 bg-black/20">
            <div class="flex flex-col items-center gap-2">
              <div class="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
              <p>در حال بارگذاری نقشه سه‌بعدی...</p>
            </div>
          </div>

          <!-- حالت خالی -->
          <div v-else-if="focusSubGoals.length === 0" class="h-44 flex items-center justify-center text-white/50 text-xs rounded-3xl border border-dashed border-white/10 bg-black/20">
            هنوز گامی برای این هدف تعریف نشده است. در صفحه نقشه راه گام جدید اضافه کنید.
          </div>

          <!-- صحنه سه‌بعدی چرخشی -->
          <div v-else
               class="relative w-full h-[420px] rounded-3xl overflow-hidden border border-white/10 touch-none select-none"
               style="background: radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, rgba(15,23,42,0.95) 60%, rgba(0,0,0,0.98) 100%);"
               @mousedown="onPointerDown"
               @mousemove="onPointerMove"
               @mouseup="onPointerUp"
               @mouseleave="onPointerUp"
               @touchstart.passive="onPointerDown"
               @touchmove.passive="onPointerMove"
               @touchend="onPointerUp">

            <!-- راهنما -->
            <div class="absolute top-3 right-3 z-20 text-[10px] text-white/50 font-bold flex items-center gap-1 pointer-events-none">
              <span>👆 برای چرخش بکشید</span>
            </div>

            <!-- نشانگر محور چرخش -->
            <div class="absolute bottom-3 left-3 z-20 text-[9px] text-white/40 font-mono pointer-events-none">
              چرخش: {{ Math.round(rotateY) }}°
            </div>

            <!-- صحنه اصلی با perspective -->
            <div class="absolute inset-0 flex items-center justify-center" style="perspective: 1400px;">
              <div class="relative"
                   :style="{
                     transformStyle: 'preserve-3d',
                     transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
                     transition: isDragging ? 'none' : 'transform 0.05s linear',
                     width: '100%', height: '100%'
                   }">

                <!-- حلقه نورانی مرکزی (محور استوانه) -->
                <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-amber-400/80 shadow-[0_0_20px_rgba(251,191,36,0.8)]"
                     style="transform: translate3d(-50%, -50%, 0) rotateX(0deg);"></div>

                <!-- هر لایه عمق -->
                <div v-for="(layer, layerIdx) in focusSceneLayers" :key="'layer-' + layerIdx"
                     class="absolute top-1/2 left-1/2"
                     :style="{
                       transformStyle: 'preserve-3d',
                       transform: `translate3d(-50%, -50%, ${-layerIdx * 130}px)`
                     }">

                  <!-- حلقه نمایشی (دایره‌ای که هر گام روی آن قرار دارد) -->
                  <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[360px] h-[360px] rounded-full border border-purple-500/20"
                       style="transform: translate(-50%, -50%) rotateX(90deg);"></div>

                  <!-- گره‌های گام‌ها -->
                  <div v-for="(sg, idxInLayer) in layer" :key="sg.id"
                       class="absolute top-1/2 left-1/2"
                       :style="{
                         transform: `translate3d(calc(-50% + ${nodePosition(idxInLayer, layerIdx, layer.length).x}px), calc(-50% + ${nodePosition(idxInLayer, layerIdx, layer.length).y}px), ${nodePosition(idxInLayer, layerIdx, layer.length).z}px)`,
                         width: '140px'
                       }">

                    <div class="rounded-2xl p-2.5 backdrop-blur-xl border border-white/20 shadow-2xl"
                         :style="{
                           background: subGoalProgress(sg) >= 100 ? 'linear-gradient(135deg, rgba(34,197,94,0.4), rgba(16,185,129,0.3))' :
                                       subGoalProgress(sg) > 0 ? 'linear-gradient(135deg, rgba(168,85,247,0.4), rgba(99,102,241,0.3))' :
                                       'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(67,56,202,0.3))',
                           boxShadow: '0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(168,85,247,0.2)'
                         }">
                      <!-- عنوان گام -->
                      <div class="flex items-start gap-1.5 mb-1.5">
                        <ListTodo class="w-3.5 h-3.5 text-amber-300 flex-shrink-0 mt-0.5" />
                        <p class="text-[11px] font-black text-white leading-tight line-clamp-2">{{ sg.title }}</p>
                      </div>
                      <!-- درصد پیشرفت -->
                      <div class="flex items-center gap-1.5">
                        <div class="flex-1 h-1 bg-white/20 rounded-full overflow-hidden">
                          <div class="h-full bg-gradient-to-r from-amber-400 to-emerald-400"
                               :style="{ width: subGoalProgress(sg) + '%' }"></div>
                        </div>
                        <span class="text-[9px] font-black text-amber-300">{{ subGoalProgress(sg) }}%</span>
                      </div>
                      <!-- تعداد کار -->
                      <p class="text-[9px] text-white/60 mt-1 font-bold">{{ (sg.tasks || []).length }} کار</p>

                      <!-- کارها به‌صورت نودهای کوچک اطراف گره اصلی -->
                      <div v-if="(sg.tasks || []).length > 0" class="mt-1.5 pt-1.5 border-t border-white/10 space-y-0.5">
                        <div v-for="(t, tIdx) in sg.tasks.slice(0, 3)" :key="t.id"
                             class="flex items-center gap-1 text-[9px] leading-tight">
                          <div class="w-1 h-1 rounded-full flex-shrink-0"
                               :class="t.is_completed ? 'bg-emerald-400' : 'bg-white/40'"></div>
                          <span class="truncate flex-1"
                                :class="t.is_completed ? 'text-emerald-200/80 line-through' : 'text-white/80'">
                            {{ t.title }}
                          </span>
                        </div>
                        <p v-if="(sg.tasks || []).length > 3" class="text-[8px] text-white/40 text-center">
                          +{{ sg.tasks.length - 3 }} کار دیگر
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- اکشن اصلی انتهای کارت تمرکز -->
        <div class="flex flex-col md:flex-row items-center justify-between gap-4 pt-4 border-t border-white/10">
          <button @click="goToRoadmap(selectedGoal.id)" class="w-full md:w-auto px-8 py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black rounded-2xl shadow-xl transition flex items-center justify-center gap-2">
            <span>ورود به اتاق عملیات و نقشه راه این هدف</span>
            <span>➔</span>
          </button>

          <button @click="closeFocusMode" class="w-full md:w-auto px-6 py-3.5 bg-white/10 hover:bg-white/20 text-white font-bold rounded-2xl transition">
            بستن حالت تمرکز
          </button>
        </div>

      </div>
    </div>

  </div>
</template>