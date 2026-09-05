<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, X, Target, BarChart3, ChevronDown, 
  ChevronUp, Calendar, ListTodo, Activity, CheckCircle2, Flag, AlertCircle,
  Eye, ArrowRight, Sparkles, BookOpen, Info, Search, Filter, RefreshCw, TrendingUp, Clock, Layers, BarChart,
  RotateCw, Circle
} from 'lucide-vue-next'
import api from '@/services/api'
import TaskFormModal from '@/components/TaskFormModal.vue'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'
import { useRouter } from 'vue-router'

const themeStore = useThemeStore()
const router = useRouter()

// --- State Management ---
const goals = ref([])
const categories = ref([])
const selectedGoalId = ref(null)
const subGoals = ref([])
const kpis = ref([])
const expandedSubGoals = ref({})
const selectedSubGoal = ref(null)
const isLoading = ref(false)
const message = ref('')
const messageType = ref('success')

// --- Modals & Popups ---
const showTaskModal = ref(false)
const showSubGoalForm = ref(false)
const showKPIForm = ref(false)
const showFullDesc = ref(false)
const currentDescText = ref('')

// --- Forms State ---
const editingSubGoal = ref(null)
const editingKPI = ref(null)
const editingTask = ref(null)
const subGoalForm = ref({ title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 })
const kpiForm = ref({ title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' })
const taskForm = ref({ 
  title: '', description: '', 
  register_date: new Date().toISOString().split('T')[0], 
  duration_days: null, category: '', 
  sub_goal_id: null, goal_id: null, 
  last_action_date: '', status: 'not_started', 
  recurrence_type: 'none', recurrence_interval: 1, 
  recurrence_end_date: '', priority: 0 
})

// --- Basic Functions ---
const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const openFullDesc = (text) => {
  currentDescText.value = text
  showFullDesc.value = true
}

const fetchGoals = async () => {
  try { 
    const res = await api.get('/goals')
    goals.value = res.data 
  } catch (e) {}
}

const fetchSubGoals = async () => {
  if (!selectedGoalId.value) return
  try {
    const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/subgoals`)
    subGoals.value = res.data.map(sg => ({
      ...sg,
      // ساده‌سازی: backend الان tasks رو مستقیم می‌فرسته
      tasks: sg.tasks || []
    }))
    res.data.forEach(sg => { if (expandedSubGoals.value[sg.id] === undefined) expandedSubGoals.value[sg.id] = true })
    
    if (selectedSubGoal.value) {
      const updated = subGoals.value.find(s => s.id === selectedSubGoal.value.id)
      if (updated) selectedSubGoal.value = updated
    }
  } catch (e) {}
}

const fetchKPIs = async () => {
  if (!selectedGoalId.value) return
  try { const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/kpis`); kpis.value = res.data } catch (e) {}
}

const selectGoal = (id) => { selectedGoalId.value = id; selectedSubGoal.value = null; fetchSubGoals(); fetchKPIs() }

const openNewSubGoalForm = () => {
  editingSubGoal.value = null
  subGoalForm.value = { title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 }
  showSubGoalForm.value = true
  showKPIForm.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const openNewKPIForm = () => {
  editingKPI.value = null
  kpiForm.value = { title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' }
  showKPIForm.value = true
  showSubGoalForm.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const openEditKPI = (k) => {
  editingKPI.value = k
  kpiForm.value = { ...k }
  showKPIForm.value = true
  showSubGoalForm.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const saveKPI = async () => {
  if (!kpiForm.value.title.trim()) return
  try {
    if (editingKPI.value) {
      await api.put(`/roadmap/kpis/${editingKPI.value.id}`, kpiForm.value)
    } else {
      await api.post(`/roadmap/goal/${selectedGoalId.value}/kpis`, kpiForm.value)
    }
    showKPIForm.value = false
    await fetchKPIs()
    showToast('✅ شاخص کلیدی با موفقیت ذخیره شد')
  } catch (e) {
    showToast('❌ خطا در ذخیره شاخص', 'error')
  }
}

const deleteKPI = async (id) => {
  if (!confirm('آیا این شاخص کلیدی حذف شود؟')) return
  try {
    await api.delete(`/roadmap/kpis/${id}`)
    await fetchKPIs()
    showToast('🗑️ شاخص حذف شد')
  } catch (e) {}
}

const selectSubGoalForFocus = (sg) => {
  selectedSubGoal.value = sg
}

const closeSubGoalFocus = () => {
  selectedSubGoal.value = null
}

const goToTasks = (subGoalId, goalId) => {
  // لینک با query params تا TasksPage خودکار فیلتر کنه
  router.push({ path: '/tasks', query: { goal: goalId, sub: subGoalId } })
}

const isMainTask = (task) => task.source === 'main_task'

const toggleTask = async (task) => {
  try {
    const newStatus = !task.is_completed
    const today = new Date().toISOString().split('T')[0]
    const payload = { 
      ...task, 
      is_completed: newStatus,
      last_action_date: newStatus ? today : (task.last_action_date || today)
    }
    if (payload.last_action_date && payload.last_action_date.includes('T')) {
      payload.last_action_date = payload.last_action_date.split('T')[0]
    }
    const url = isMainTask(task) ? `/tasks/${task.id}` : `/roadmap/tasks/${task.id}`
    await api.put(url, payload)
    await fetchSubGoals()
  } catch (e) { showToast('❌ خطا در بروزرسانی', 'error') }
}

const openEditTask = (task) => {
  editingTask.value = task
  taskForm.value = { ...task }
  showTaskModal.value = true
}

const saveTask = async () => {
  try {
    isLoading.value = true
    const url = isMainTask(editingTask.value) ? `/tasks/${editingTask.value.id}` : `/roadmap/tasks/${editingTask.value.id}`
    await api.put(url, taskForm.value)
    showTaskModal.value = false
    await fetchSubGoals()
    showToast('✅ تغییرات کار با موفقیت ذخیره شد')
  } catch (e) { showToast('❌ خطا در ذخیره', 'error') } finally { isLoading.value = false }
}

const saveSubGoal = async () => {
  if (!subGoalForm.value.title.trim()) return
  try {
    if (editingSubGoal.value) await api.put(`/roadmap/subgoals/${editingSubGoal.value.id}`, subGoalForm.value)
    else await api.post(`/roadmap/goal/${selectedGoalId.value}/subgoals`, subGoalForm.value)
    showSubGoalForm.value = false; await fetchSubGoals(); showToast('✅ گام ذخیره شد')
  } catch (e) { showToast('❌ خطا در ذخیره گام', 'error') }
}

const deleteSubGoal = async (id) => {
  if (!confirm('آیا این گام عملیاتی حذف شود؟')) return
  try { 
    await api.delete(`/roadmap/subgoals/${id}`)
    if (selectedSubGoal.value && selectedSubGoal.value.id === id) {
      selectedSubGoal.value = null
    }
    await fetchSubGoals()
    showToast('🗑️ گام حذف شد') 
  } catch (e) {}
}

const subGoalProgress = (sg) => {
  if (!sg.tasks || sg.tasks.length === 0) return 0
  return Math.round((sg.tasks.filter(t => t.is_completed).length / sg.tasks.length) * 100)
}

// 🏷️ برچسب فارسی نوع تکرار
const recurrenceLabel = (type) => {
  const map = { daily: 'روزانه', weekly: 'هفتگی', monthly: 'ماهانه', yearly: 'سالانه' }
  return map[type] || 'دوره‌ای'
}

// ============================================================
// 🚀 ارتقاهای سربرگ: state و computed ها
// ============================================================
const searchQuery = ref('')                // جستجوی گام‌ها
const filterStatus = ref('all')            // فیلتر وضعیت: all, completed, in_progress, pending
const sortBy = ref('order')                // مرتب‌سازی: order, date, progress, priority
const lastRefreshed = ref(new Date())      // زمان آخرین بروزرسانی
const isRefreshing = ref(false)            // وضعیت لودینگ بروزرسانی
const goalSwitcherOpen = ref(false)        // باز بودن انتخاب‌گر هدف
const treeExpanded = ref(true)             // باز بودن سکشن درختی در modal
const expandedNodes = ref({})              // map: subGoalId -> expanded (پیش‌فرض باز)
const treeModalOpen = ref(false)           // باز بودن modal ساختار درختی

// 📌 وقتی هدف جدیدی انتخاب می‌شود، همه گره‌های درخت ریست شوند
watch(selectedGoalId, () => { expandedNodes.value = {} })
const toggleSubGoalNode = (id) => {
  expandedNodes.value[id] = !(expandedNodes.value[id] !== false)
}

// 🌳 باز کردن modal ساختار درختی هدف (حتی اگر فعال نباشد)
const openGoalTree = async (goalId = null) => {
  const targetId = goalId || selectedGoalId.value
  if (!targetId) return
  // اگر هدف انتخاب نشده، ابتدا آن را فعال کنیم تا گام‌ها و کارها لود شوند
  if (targetId !== selectedGoalId.value) {
    selectGoal(targetId)
  }
  // کمی صبر برای لود شدن subGoals
  await new Promise(r => setTimeout(r, 100))
  expandedNodes.value = {}
  treeModalOpen.value = true
}

// 📊 آمار کلی از همه اهداف (نه فقط هدف فعال)
const overallStats = computed(() => {
  let totalSubGoals = 0
  let completedSubGoals = 0
  let totalTasks = 0
  let completedTasks = 0
  let activeKpis = 0
  goals.value.forEach(g => {
    // برای هر goal باید subGoals را داشته باشیم؛ فعلاً فقط هدف فعال را داریم
  })
  // آمار هدف فعال فعلی
  if (selectedGoalId.value && subGoals.value.length > 0) {
    totalSubGoals = subGoals.value.length
    completedSubGoals = subGoals.value.filter(sg => subGoalProgress(sg) >= 100).length
    totalTasks = subGoals.value.reduce((sum, sg) => sum + (sg.tasks?.length || 0), 0)
    completedTasks = subGoals.value.reduce((sum, sg) => sum + (sg.tasks?.filter(t => t.is_completed).length || 0), 0)
  }
  activeKpis = kpis.value.length
  const overallProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
  return { totalSubGoals, completedSubGoals, totalTasks, completedTasks, activeKpis, overallProgress }
})

// 🎯 هدف فعال فعلی (شیء کامل)
const activeGoal = computed(() => goals.value.find(g => g.id === selectedGoalId.value) || null)

// 📅 گام‌های نزدیک به سررسید (۷ روز آینده)
const upcomingDeadlines = computed(() => {
  const now = new Date()
  const future = new Date()
  future.setDate(future.getDate() + 7)
  return subGoals.value.filter(sg => {
    if (!sg.target_date || subGoalProgress(sg) >= 100) return false
    const d = new Date(sg.target_date)
    return d >= now && d <= future
  }).length
})

// 🔍 فیلتر و مرتب‌سازی گام‌ها
const filteredSubGoals = computed(() => {
  let list = [...subGoals.value]
  // جستجو
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(sg =>
      sg.title.toLowerCase().includes(q) ||
      (sg.description && sg.description.toLowerCase().includes(q))
    )
  }
  // فیلتر وضعیت
  if (filterStatus.value !== 'all') {
    list = list.filter(sg => {
      const p = subGoalProgress(sg)
      if (filterStatus.value === 'completed') return p >= 100
      if (filterStatus.value === 'in_progress') return p > 0 && p < 100
      if (filterStatus.value === 'pending') return p === 0
      return true
    })
  }
  // مرتب‌سازی
  if (sortBy.value === 'progress') {
    list.sort((a, b) => subGoalProgress(b) - subGoalProgress(a))
  } else if (sortBy.value === 'date') {
    list.sort((a, b) => new Date(a.target_date || 0) - new Date(b.target_date || 0))
  } else if (sortBy.value === 'priority') {
    list.sort((a, b) => (b.priority || 0) - (a.priority || 0))
  }
  return list
})

// 🔄 تابع refresh کلی
const refreshAll = async () => {
  isRefreshing.value = true
  try {
    await fetchGoals()
    if (selectedGoalId.value) {
      await Promise.all([fetchSubGoals(), fetchKPIs()])
    }
    lastRefreshed.value = new Date()
    showToast('✅ بروزرسانی انجام شد')
  } catch (e) {
    showToast('❌ خطا در بروزرسانی', 'error')
  } finally {
    setTimeout(() => { isRefreshing.value = false }, 600)
  }
}

// ⏱️ فرمت زمان نسبی برای "آخرین بروزرسانی"
const relativeTime = computed(() => {
  const diff = Math.floor((Date.now() - lastRefreshed.value.getTime()) / 1000)
  if (diff < 60) return `${diff} ثانیه پیش`
  if (diff < 3600) return `${Math.floor(diff / 60)} دقیقه پیش`
  return `${Math.floor(diff / 3600)} ساعت پیش`
})

let refreshInterval = null
const handleEsc = (e) => { if (e.key === 'Escape' && treeModalOpen.value) treeModalOpen.value = false }
onMounted(() => {
  refreshInterval = setInterval(() => {
    // برای reactive شدن relativeTime
    lastRefreshed.value = new Date(lastRefreshed.value.getTime())
  }, 10000)
  window.addEventListener('keydown', handleEsc)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  window.removeEventListener('keydown', handleEsc)
})

onMounted(() => {
  fetchGoals().then(() => {
    const savedGoalId = sessionStorage.getItem('active_goal_id')
    if (savedGoalId) {
      selectGoal(Number(savedGoalId))
      sessionStorage.removeItem('active_goal_id')
    } else if (goals.value.length > 0) {
      // انتخاب اتوماتیک اولین هدف جهت لود آنی گام‌ها
      selectGoal(goals.value[0].id)
    }
  })
  api.get('/tasks/categories').then(res => categories.value = res.data)
})
</script>

<template>
  <div class="p-3 sm:p-4 md:p-8 lg:p-10 max-w-7xl mx-auto relative min-h-screen text-right" dir="rtl">
    
    <!-- Toast -->
    <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <!-- 🚀 سربرگ ارتقایافته نقشه راه -->
    <div class="mb-8 animate-in slide-in-from-top duration-700">

      <!-- ردیف اول: عنوان + دکمه‌های اصلی -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-12 h-12 md:w-14 md:h-14 rounded-2xl bg-gradient-to-br from-purple-500/30 to-blue-500/30 border border-purple-400/40 flex items-center justify-center flex-shrink-0 shadow-[0_0_20px_rgba(168,85,247,0.3)]">
            <MapPin class="w-6 h-6 md:w-7 md:h-7 text-purple-300" />
          </div>
          <div class="min-w-0">
            <h1 class="text-2xl md:text-3xl lg:text-4xl font-black text-white flex items-center gap-2">
              نقشه راه
              <span v-if="upcomingDeadlines > 0" class="text-[10px] md:text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold flex items-center gap-1">
                <Clock class="w-3 h-3" /> {{ upcomingDeadlines }} سررسید
              </span>
            </h1>
            <p class="opacity-70 text-xs md:text-sm flex items-center gap-2" :style="{ color: 'var(--text-secondary)' }">
              <span class="truncate">{{ activeGoal ? `هدف فعال: ${activeGoal.title}` : 'مسیر هوشمند رسیدن به اهداف' }}</span>
              <span class="opacity-40">•</span>
              <span class="flex items-center gap-1 whitespace-nowrap">
                <RefreshCw class="w-3 h-3" :class="{ 'animate-spin': isRefreshing }" />
                {{ relativeTime }}
              </span>
            </p>
          </div>
        </div>

        <!-- دکمه‌های عمل اصلی -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="refreshAll" :disabled="isRefreshing" title="بروزرسانی"
                  class="w-10 h-10 md:w-11 md:h-11 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition flex items-center justify-center text-white/80 hover:text-white disabled:opacity-50">
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" />
          </button>
          <button v-if="selectedGoalId" @click="openNewKPIForm"
                  class="px-3 md:px-4 py-2.5 md:py-3 rounded-xl text-white font-bold text-xs md:text-sm bg-white/10 hover:bg-white/20 transition shadow-lg border border-white/10 flex items-center gap-1.5">
            <Plus class="w-4 h-4 text-blue-400" />
            <span class="hidden sm:inline">افزودن KPI</span>
          </button>
          <button v-if="selectedGoalId" @click="openNewSubGoalForm"
                  class="px-4 md:px-5 py-2.5 md:py-3 rounded-xl text-white font-black text-xs md:text-sm transition shadow-xl hover:scale-105 active:scale-95 shadow-purple-500/20 bg-gradient-to-r from-purple-600 to-indigo-600 flex items-center gap-1.5">
            <Plus class="w-4 h-4 md:w-5 md:h-5" />
            <span>گام جدید</span>
          </button>
        </div>
      </div>

      <!-- ردیف دوم: کارت وضعیت هدف فعال + نوار پیشرفت کلی (فقط وقتی هدفی انتخاب شده) -->
      <div v-if="selectedGoalId && activeGoal" class="glass-card rounded-2xl border border-white/10 p-4 md:p-5 mb-4">
        <div class="flex flex-col md:flex-row md:items-center gap-4">
          <!-- اطلاعات هدف فعال -->
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                 :style="{ background: 'linear-gradient(135deg, var(--accent), rgba(99,102,241,0.6))' }">
              <Target class="w-5 h-5 text-white" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-[10px] opacity-60 font-bold">در حال اجرای</p>
              <p class="text-sm md:text-base font-black text-white truncate">{{ activeGoal.title }}</p>
            </div>
            <button @click="selectedGoalId = null" title="بستن هدف فعال"
                    class="w-8 h-8 rounded-lg hover:bg-white/10 transition flex items-center justify-center text-white/60 hover:text-white flex-shrink-0">
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- نوار پیشرفت کلی هدف فعال -->
          <div class="md:w-80">
            <div class="flex items-center justify-between text-[10px] font-bold mb-1.5">
              <span class="opacity-70 flex items-center gap-1">
                <TrendingUp class="w-3 h-3 text-emerald-400" />
                پیشرفت کلی هدف
              </span>
              <span class="text-emerald-300 font-black">{{ overallStats.overallProgress }}%</span>
            </div>
            <div class="h-2 bg-white/10 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-emerald-500 via-amber-400 to-purple-500 transition-all duration-1000 rounded-full"
                   :style="{ width: overallStats.overallProgress + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ردیف سوم: نوار آمار زنده -->
      <div v-if="selectedGoalId" class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3 mb-4">
        <!-- کارت آمار: گام‌ها -->
        <div class="glass-card rounded-xl border border-white/10 p-3 md:p-4">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-7 h-7 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
              <Layers class="w-3.5 h-3.5 text-purple-300" />
            </div>
            <p class="text-[10px] opacity-60 font-bold">گام‌ها</p>
          </div>
          <p class="text-lg md:text-xl font-black text-white">
            {{ overallStats.completedSubGoals }}<span class="text-xs opacity-50">/{{ overallStats.totalSubGoals }}</span>
          </p>
          <p class="text-[9px] opacity-50 font-bold">تکمیل شده</p>
        </div>

        <!-- کارت آمار: کارها -->
        <div class="glass-card rounded-xl border border-white/10 p-3 md:p-4">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-7 h-7 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
              <CheckCircle2 class="w-3.5 h-3.5 text-emerald-300" />
            </div>
            <p class="text-[10px] opacity-60 font-bold">کارها</p>
          </div>
          <p class="text-lg md:text-xl font-black text-white">
            {{ overallStats.completedTasks }}<span class="text-xs opacity-50">/{{ overallStats.totalTasks }}</span>
          </p>
          <p class="text-[9px] opacity-50 font-bold">انجام شده</p>
        </div>

        <!-- کارت آمار: KPIها -->
        <div class="glass-card rounded-xl border border-white/10 p-3 md:p-4">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-7 h-7 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
              <Activity class="w-3.5 h-3.5 text-blue-300" />
            </div>
            <p class="text-[10px] opacity-60 font-bold">KPIها</p>
          </div>
          <p class="text-lg md:text-xl font-black text-white">{{ overallStats.activeKpis }}</p>
          <p class="text-[9px] opacity-50 font-bold">فعال</p>
        </div>

        <!-- کارت آمار: سررسیدها -->
        <div class="glass-card rounded-xl border border-white/10 p-3 md:p-4">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-7 h-7 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
              <Clock class="w-3.5 h-3.5 text-amber-300" />
            </div>
            <p class="text-[10px] opacity-60 font-bold">سررسید ۷ روز</p>
          </div>
          <p class="text-lg md:text-xl font-black"
             :class="upcomingDeadlines > 0 ? 'text-amber-300' : 'text-white'">
            {{ upcomingDeadlines }}
          </p>
          <p class="text-[9px] opacity-50 font-bold">گام نزدیک</p>
        </div>
      </div>

      <!-- ردیف چهارم: جستجو، فیلتر، مرتب‌سازی (فقط وقتی گام‌ها لود شده) -->
      <div v-if="selectedGoalId && subGoals.length > 0" class="glass-card rounded-2xl border border-white/10 p-3 md:p-4">
        <div class="flex flex-col md:flex-row gap-2 md:gap-3">
          <!-- جستجو -->
          <div class="relative flex-1">
            <Search class="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-white/40 pointer-events-none" />
            <input v-model="searchQuery" type="text" placeholder="جستجو در گام‌ها..."
                   class="w-full pr-9 pl-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs md:text-sm text-white placeholder-white/40 focus:border-purple-500/50 focus:outline-none transition" />
          </div>
          <!-- فیلتر -->
          <div class="flex items-center gap-1 bg-white/5 rounded-xl p-1 border border-white/10">
            <button v-for="f in [{v:'all',l:'همه'},{v:'in_progress',l:'در جریان'},{v:'pending',l:'شروع‌نشده'},{v:'completed',l:'تکمیل'}]"
                    :key="f.v" @click="filterStatus = f.v"
                    class="px-2 md:px-3 py-1.5 rounded-lg text-[10px] md:text-xs font-bold transition"
                    :class="filterStatus === f.v ? 'bg-purple-600 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'">
              {{ f.l }}
            </button>
          </div>
          <!-- مرتب‌سازی -->
          <select v-model="sortBy"
                  class="px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs md:text-sm text-white focus:border-purple-500/50 focus:outline-none transition cursor-pointer">
            <option value="order">ترتیب تعریف</option>
            <option value="progress">پیشرفت</option>
            <option value="date">سررسید</option>
            <option value="priority">اولویت</option>
          </select>
        </div>
        <!-- نشانگر تعداد فیلترشده -->
        <div v-if="searchQuery || filterStatus !== 'all'" class="text-[10px] opacity-60 font-bold mt-2 px-1">
          نمایش {{ filteredSubGoals.length }} از {{ subGoals.length }} گام
          <button @click="searchQuery = ''; filterStatus = 'all'" class="text-purple-300 hover:underline mr-2">پاک کردن فیلتر</button>
        </div>
      </div>

    </div>

    <!-- 🌟 فرم تعریف/ویرایش گام جدید -->
    <div v-if="showSubGoalForm" class="mb-10 p-8 rounded-3xl border-2 border-purple-500/40 bg-slate-900/90 shadow-[0_0_50px_rgba(168,85,247,0.2)] animate-in slide-in-from-top duration-300">
      <div class="flex items-center justify-between pb-4 mb-6 border-b border-white/10">
        <h3 class="text-2xl font-black text-white flex items-center gap-2">
          <Sparkles class="w-6 h-6 text-amber-400" />
          {{ editingSubGoal ? 'ویرایش گام عملیاتی' : 'تعریف گام عملیاتی جدید' }}
        </h3>
        <button @click="showSubGoalForm = false" class="p-2 text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-gray-300 mb-1">عنوان گام عملیاتی *</label>
          <input v-model="subGoalForm.title" placeholder="مثلاً: طراحی فاز اولیه نرم‌افزار" class="w-full p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none transition" />
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-300 mb-1">توضیحات گام</label>
          <textarea v-model="subGoalForm.description" rows="3" placeholder="توضیحات مختصر گام..." class="w-full p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none transition"></textarea>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
           <div><label class="text-xs font-bold text-gray-300 mb-1 block">تاریخ شروع</label><DateInputPersian v-model="subGoalForm.start_date" /></div>
           <div><label class="text-xs font-bold text-gray-300 mb-1 block">تاریخ هدف / پایان</label><DateInputPersian v-model="subGoalForm.target_date" /></div>
        </div>
      </div>

      <div class="flex gap-4 mt-6 pt-4 border-t border-white/10">
        <button @click="saveSubGoal" class="flex-1 py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black rounded-2xl shadow-lg transition">
          {{ editingSubGoal ? 'بروزرسانی گام' : 'ذخیره گام عملیاتی' }}
        </button>
        <button @click="showSubGoalForm = false" class="px-8 py-3.5 bg-white/10 hover:bg-white/20 text-white font-bold rounded-2xl transition">
          لغو
        </button>
      </div>
    </div>

    <!-- 🌟 فرم تعریف/ویرایش شاخص کلیدی (KPI) -->
    <div v-if="showKPIForm" class="mb-10 p-8 rounded-3xl border-2 border-blue-500/40 bg-slate-900/90 shadow-[0_0_50px_rgba(59,130,246,0.2)] animate-in slide-in-from-top duration-300">
      <div class="flex items-center justify-between pb-4 mb-6 border-b border-white/10">
        <h3 class="text-2xl font-black text-white flex items-center gap-2">
          <Activity class="w-6 h-6 text-blue-400" />
          {{ editingKPI ? 'ویرایش شاخص عملکرد (KPI)' : 'تعریف شاخص عملکرد جدید (KPI)' }}
        </h3>
        <button @click="showKPIForm = false" class="p-2 text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-gray-300 mb-1">عنوان شاخص (مثلاً: تعداد برنامه‌های مطالعه‌شده)</label>
          <input v-model="kpiForm.title" placeholder="عنوان شاخص..." class="w-full p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none transition" />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">واحد اندازه‌گیری (مثلاً: صفحه، ساعت، کیلوگرم)</label>
            <input v-model="kpiForm.unit" placeholder="واحد..." class="w-full p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-sm outline-none" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">مقدار هدف نهایی</label>
            <input v-model.number="kpiForm.target_value" type="number" class="w-full p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-sm outline-none" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">مقدار فعلی محقق‌شده</label>
            <input v-model.number="kpiForm.current_value" type="number" class="w-full p-4 rounded-2xl bg-white/5 border border-white/10 text-white text-sm outline-none" />
          </div>
        </div>
      </div>

      <div class="flex gap-4 mt-6 pt-4 border-t border-white/10">
        <button @click="saveKPI" class="flex-1 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-black rounded-2xl shadow-lg transition">
          ذخیره شاخص کلیدی
        </button>
        <button @click="showKPIForm = false" class="px-8 py-3.5 bg-white/10 hover:bg-white/20 text-white font-bold rounded-2xl transition">
          لغو
        </button>
      </div>
    </div>

    <!-- Goal Selection Grid -->
    <div class="mb-12">
      <label class="text-xs font-bold mb-4 block opacity-50 uppercase tracking-widest text-white">انتخاب هدف فعال شما</label>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <div v-for="goal in goals" :key="goal.id"
             class="rounded-2xl border-2 transition-all relative overflow-hidden"
             :style="selectedGoalId === goal.id ? { background: 'var(--accent)', borderColor: 'var(--accent)', color: '#fff', boxShadow: '0 12px 30px -5px var(--accent)' } : { background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
          <!-- دکمه اصلی انتخاب هدف (کل کارت به جز دکمه‌های کناری) -->
          <button @click="selectGoal(goal.id)"
                  class="w-full p-5 pb-2 text-center font-black text-sm">
            {{ goal.title }}
          </button>
          <!-- دکمه‌های کناری: نقشه راه + ساختار درختی -->
          <div class="flex items-center justify-center gap-2 px-3 pb-3 pt-1">
            <button @click.stop="openGoalTree(goal.id)" title="ساختار درختی گام‌ها و کارها"
                    class="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] font-bold transition"
                    :style="selectedGoalId === goal.id ? { background: 'rgba(255,255,255,0.18)', color: '#fff' } : { background: 'rgba(16,185,129,0.12)', color: '#10b981' }">
              <Layers class="w-3 h-3" />
              <span>ساختار</span>
            </button>
            <button @click.stop="selectGoal(goal.id)" title="نقشه راه هدف"
                    class="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] font-bold transition"
                    :style="selectedGoalId === goal.id ? { background: 'rgba(255,255,255,0.18)', color: '#fff' } : { background: 'rgba(168,85,247,0.12)', color: '#a78bfa' }">
              <MapPin class="w-3 h-3" />
              <span>نقشه راه</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedGoalId" class="space-y-12 animate-in fade-in duration-700">
      
      <!-- KPI Display Section -->
      <section class="rounded-3xl p-8 border-2 shadow-sm" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-black flex items-center gap-3"><Activity class="w-8 h-8 text-blue-500" /> شاخص‌های کلیدی (KPI)</h2>
          <button @click="openNewKPIForm" class="text-xs text-blue-400 hover:underline font-bold">+ افزودن شاخص جدید</button>
        </div>
        <div v-if="kpis.length === 0" class="text-center py-6 opacity-40 text-sm">شاخصی برای این هدف تعریف نشده است.</div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="kpi in kpis" :key="kpi.id" class="p-5 rounded-2xl border-2 relative group" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }">
            <div class="flex justify-between items-start mb-3">
              <p class="text-sm font-bold opacity-70">{{ kpi.title }}</p>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                <button @click="openEditKPI(kpi)" class="p-1 hover:bg-white/10 text-gray-300 rounded"><Edit3 class="w-3.5 h-3.5" /></button>
                <button @click="deleteKPI(kpi.id)" class="p-1 hover:bg-red-500/20 text-red-400 rounded"><Trash2 class="w-3.5 h-3.5" /></button>
              </div>
            </div>
            <div class="flex items-baseline gap-2 mb-3">
              <span class="text-3xl font-black">{{ kpi.current_value }}</span>
              <span class="text-xs opacity-50">از {{ kpi.target_value }} {{ kpi.unit }}</span>
            </div>
            <div class="w-full h-2 rounded-full bg-black/10 overflow-hidden">
              <div class="h-full bg-blue-500 transition-all duration-1000 shadow-[0_0_10px_rgba(59,130,246,0.5)]" :style="{ width: Math.min((kpi.current_value/(kpi.target_value||1)*100), 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 🌟 نقشه‌ی اجرایی گام‌ها در چیدمان دو ستونه -->
      <section class="space-y-6">
        <h2 class="text-2xl font-black px-2 flex items-center gap-3"><ListTodo class="w-8 h-8 text-purple-400" /> نقشه‌ی اجرایی گام‌ها</h2>
        
        <div v-if="subGoals.length === 0" class="text-center py-16 rounded-3xl border-2 border-dashed border-white/10 opacity-60">
          <ListTodo class="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p class="font-bold text-base">هیچ گام عملیاتی تعریف نشده است.</p>
          <button @click="openNewSubGoalForm" class="mt-4 px-6 py-2.5 bg-purple-600 text-white font-bold rounded-xl text-xs">تعریف اولین گام</button>
        </div>

        <div v-else-if="filteredSubGoals.length === 0" class="text-center py-12 rounded-3xl border-2 border-dashed border-white/10 opacity-60">
          <Search class="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p class="font-bold text-sm">گامی با این فیلتر پیدا نشد.</p>
          <button @click="searchQuery = ''; filterStatus = 'all'" class="mt-3 px-5 py-2 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition">پاک کردن فیلترها</button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="sg in filteredSubGoals" :key="sg.id"
               @click="selectSubGoalForFocus(sg)"
               class="rounded-3xl border-2 p-6 shadow-md transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer flex flex-col justify-between group relative overflow-hidden"
               :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">

            <div>
              <div class="flex items-start justify-between gap-4 mb-3">
                <div>
                  <h3 class="text-xl font-black group-hover:text-purple-400 transition" :style="{ color: 'var(--text-primary)' }">{{ sg.title }}</h3>
                  <p class="text-xs opacity-60 mt-1 line-clamp-2" :style="{ color: 'var(--text-secondary)' }">{{ sg.description || 'بدون توضیح' }}</p>
                </div>

                <div class="flex items-center gap-1" @click.stop>
                  <button @click="editingSubGoal = sg; subGoalForm = {...sg}; showSubGoalForm = true; window.scrollTo({ top: 0, behavior: 'smooth' })" title="ویرایش" class="p-2 hover:bg-white/10 rounded-xl transition text-gray-400 hover:text-white">
                    <Edit3 class="w-4 h-4" />
                  </button>
                  <button @click="deleteSubGoal(sg.id)" title="حذف" class="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div class="space-y-2 border-t pt-3 mb-4" :style="{ borderColor: 'var(--border)' }">
                <div class="flex items-center justify-between text-xs font-bold">
                  <span class="opacity-70">پیشرفت گام:</span>
                  <span :style="{ color: 'var(--accent)' }">{{ subGoalProgress(sg) }}%</span>
                </div>
                <div class="w-full h-2 rounded-full bg-black/10 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-700" :style="{ width: subGoalProgress(sg) + '%', background: 'var(--accent)' }"></div>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between gap-2 pt-3 border-t" :style="{ borderColor: 'var(--border)' }" @click.stop>
              <button @click="selectSubGoalForFocus(sg)" class="px-3 py-1.5 rounded-xl font-bold text-xs bg-white/5 hover:bg-white/10 text-white transition flex items-center gap-1.5">
                <Eye class="w-3.5 h-3.5 text-amber-400" />
                <span>تمرکز و کارها</span>
              </button>

              <button @click="goToTasks(sg.id, selectedGoalId)" class="px-3.5 py-1.5 rounded-xl font-bold text-xs text-white transition flex items-center gap-1.5 shadow-md hover:scale-105 active:scale-95 bg-gradient-to-r from-purple-600 to-indigo-600">
                <span>اتاق عملیات</span>
                <span>➔</span>
              </button>
            </div>

          </div>
        </div>
      </section>
    </div>

    <!-- 🌟 حالت تمرکز سه‌بعدی گام عملیاتی -->
    <div v-if="selectedSubGoal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-300" @click.self="closeSubGoalFocus">
      
      <div class="w-full max-w-4xl rounded-3xl p-8 max-h-[90vh] overflow-y-auto border-2 border-purple-500/50 shadow-[0_0_60px_rgba(168,85,247,0.3)] bg-slate-900 text-white relative animate-in zoom-in-95 duration-300">
        
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
          <button @click="closeSubGoalFocus" class="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-black rounded-2xl shadow-xl transition flex items-center gap-2 hover:scale-105">
            <ArrowRight class="w-5 h-5" />
            <span>بازگشت به لیست گام‌ها</span>
          </button>

          <div class="flex items-center gap-2">
            <button @click="editingSubGoal = selectedSubGoal; subGoalForm = {...selectedSubGoal}; showSubGoalForm = true; closeSubGoalFocus(); window.scrollTo({ top: 0, behavior: 'smooth' })" class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <Edit3 class="w-4 h-4 text-purple-400" /> ویرایش گام
            </button>
            <button @click="deleteSubGoal(selectedSubGoal.id)" class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <Trash2 class="w-4 h-4" /> حذف گام
            </button>
          </div>
        </div>

        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-300 font-extrabold text-xs mb-3">
          <Sparkles class="w-4 h-4 animate-spin text-amber-400" /> حالت تمرکز سه‌بعدی گام عملیاتی
        </div>

        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-white/10">
          <div>
            <h2 class="text-2xl md:text-3xl font-black text-white mb-2">{{ selectedSubGoal.title }}</h2>
            <p class="text-sm text-gray-300">{{ selectedSubGoal.description || 'بدون توضیح' }}</p>
          </div>

          <div class="flex items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/10">
            <div>
              <p class="text-[10px] text-gray-400 font-bold">پیشرفت این گام</p>
              <p class="text-2xl font-black text-purple-400">{{ subGoalProgress(selectedSubGoal) }}%</p>
            </div>
            <div class="w-20 h-2 bg-black/20 rounded-full overflow-hidden">
              <div class="h-full bg-purple-500 transition-all duration-500" :style="{ width: subGoalProgress(selectedSubGoal) + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="space-y-4 mb-8">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-lg font-black text-white flex items-center gap-2">
              <ListTodo class="w-5 h-5 text-purple-400" /> کارهای مربوط به این گام
            </h4>
            <button @click="goToTasks(selectedSubGoal.id, selectedGoalId)" class="text-xs text-purple-400 hover:underline font-bold">
              مدیریت پیشرفته در اتاق عملیات ➔
            </button>
          </div>

          <div v-if="!selectedSubGoal.tasks || selectedSubGoal.tasks.length === 0" class="text-center py-8 rounded-2xl bg-white/5 border border-white/10 opacity-60">
            هیچ کاری برای این گام ثبت نشده است.
          </div>

          <div v-else class="space-y-3">
            <div v-for="task in selectedSubGoal.tasks" :key="task.id" class="p-4 rounded-2xl border bg-white/5 border-white/10 flex items-start justify-between gap-4">
              <div class="flex items-start gap-3 flex-1">
                <button @click="toggleTask(task)" class="w-8 h-8 rounded-lg border flex items-center justify-center transition-all mt-0.5" :class="task.is_completed ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/20 text-transparent'">
                  <Check class="w-5 h-5" />
                </button>
                <div>
                  <p class="font-bold text-sm text-white" :class="task.is_completed ? 'line-through opacity-40' : ''">{{ task.title }}</p>
                  <p v-if="task.description" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ task.description }}</p>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <button @click="openEditTask(task)" class="p-1.5 text-gray-400 hover:text-white"><Edit3 class="w-4 h-4" /></button>
                <button @click="api.delete(isMainTask(task) ? `/tasks/${task.id}` : `/roadmap/tasks/${task.id}`).then(fetchSubGoals)" class="p-1.5 text-gray-400 hover:text-red-400"><Trash2 class="w-4 h-4" /></button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between gap-4 pt-4 border-t border-white/10">
          <button @click="goToTasks(selectedSubGoal.id, selectedGoalId)" class="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black rounded-xl text-xs transition flex items-center gap-2">
            <span>انتقال کارها به اتاق عملیات</span>
            <span>➔</span>
          </button>

          <button @click="closeSubGoalFocus" class="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition">
            بستن حالت تمرکز
          </button>
        </div>

      </div>
    </div>

    <!-- Modals Section -->
    <div v-if="showFullDesc" class="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-black/85 backdrop-blur-md" @click="showFullDesc = false">
      <div class="w-full max-w-2xl rounded-3xl p-8 bg-gray-900 border-2 border-white/10 shadow-2xl" @click.stop>
        <div class="flex justify-between items-center mb-6 text-white"><h3 class="text-2xl font-black">توضیحات کامل</h3><button @click="showFullDesc = false" class="p-2"><X class="w-8 h-8" /></button></div>
        <div class="text-lg text-gray-200 leading-relaxed max-h-[50vh] overflow-y-auto text-justify pl-4 custom-scrollbar">{{ currentDescText }}</div>
        <button @click="showFullDesc = false" class="w-full mt-6 py-3.5 rounded-2xl bg-blue-600 text-white font-black text-base hover:bg-blue-500 transition shadow-lg">بستن</button>
      </div>
    </div>

    <!-- Task Modal Connector -->
    <TaskFormModal v-model="showTaskModal" :form="taskForm" :categories="categories" :goals="goals" :sub-goals="subGoals" :editing-task="editingTask" :is-loading="isLoading" @save="saveTask" />

    <!-- 🌳 Modal ساختار درختی هدف فعال -->
    <Teleport to="body">
      <div v-if="treeModalOpen" class="fixed inset-0 z-[200] flex items-center justify-center p-3 md:p-6 bg-black/80 backdrop-blur-md" @click.self="treeModalOpen = false">
        <div class="w-full max-w-3xl max-h-[88vh] rounded-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col"
             style="background: linear-gradient(180deg, #0f172a 0%, #020617 100%);">

          <!-- هدر modal -->
          <div class="px-5 md:px-6 py-4 border-b border-white/10 flex items-center justify-between flex-shrink-0">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                <Layers class="w-5 h-5 text-emerald-300" />
              </div>
              <div class="min-w-0">
                <h3 class="text-base md:text-lg font-black text-white flex items-center gap-2">
                  ساختار درختی هدف
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/10 font-bold opacity-70">
                    {{ subGoals.length }} گام • {{ overallStats.totalTasks }} کار
                  </span>
                </h3>
                <p class="text-[10px] opacity-60 font-bold truncate">{{ activeGoal?.title }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <button @click="expandedNodes = {}" title="بستن همه شاخه‌ها"
                      class="px-2.5 py-1.5 rounded-lg text-[10px] font-bold bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition">
                بستن همه
              </button>
              <button @click="treeModalOpen = false" title="بستن"
                      class="w-9 h-9 rounded-lg hover:bg-white/10 transition flex items-center justify-center text-white/60 hover:text-white">
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- بدنه modal: ساختار درختی -->
          <div class="flex-1 overflow-y-auto custom-scrollbar p-4 md:p-6">

            <!-- حالت خالی: بدون گام -->
            <div v-if="subGoals.length === 0" class="text-center py-16 opacity-60">
              <ListTodo class="w-14 h-14 mx-auto mb-3 opacity-40 text-white/40" />
              <p class="font-bold text-sm text-white/70">هنوز گامی برای این هدف تعریف نشده است.</p>
              <button @click="treeModalOpen = false; openNewSubGoalForm()"
                      class="mt-4 px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-xl text-xs transition">
                تعریف اولین گام
              </button>
            </div>

            <!-- ساختار درختی -->
            <div v-else class="space-y-1">
              <!-- ریشه: خود هدف -->
              <div class="flex items-center gap-2.5 py-2.5 px-3 rounded-xl bg-gradient-to-l from-purple-500/15 to-transparent border border-purple-500/20">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                     :style="{ background: 'var(--accent)' }">
                  <Target class="w-4 h-4 text-white" />
                </div>
                <span class="text-sm font-black text-white truncate flex-1">{{ activeGoal?.title }}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold">
                  {{ overallStats.overallProgress }}%
                </span>
              </div>

              <!-- اتصال ریشه به شاخه‌ها -->
              <div class="mr-4 border-r-2 border-purple-500/30 pr-4 space-y-1.5 mt-1">
                <div v-for="(sg, sgIdx) in subGoals" :key="'tree-' + sg.id">
                  <!-- گره گام -->
                  <div class="flex items-center gap-2 py-2 px-2.5 rounded-lg hover:bg-white/5 transition group">
                    <!-- دکمه باز/بستن -->
                    <button @click="toggleSubGoalNode(sg.id)"
                            class="w-5 h-5 flex items-center justify-center flex-shrink-0 rounded hover:bg-white/10 transition"
                            :class="(expandedNodes[sg.id] !== false) ? 'rotate-90' : ''">
                      <ChevronRight class="w-3.5 h-3.5 text-white/60" />
                    </button>
                    <!-- آیکون گام -->
                    <div class="w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0"
                         :style="{ background: subGoalProgress(sg) >= 100 ? 'rgba(34,197,94,0.3)' : subGoalProgress(sg) > 0 ? 'rgba(168,85,247,0.3)' : 'rgba(99,102,241,0.3)' }">
                      <ListTodo class="w-4 h-4"
                                :class="subGoalProgress(sg) >= 100 ? 'text-emerald-300' : subGoalProgress(sg) > 0 ? 'text-purple-300' : 'text-blue-300'" />
                    </div>
                    <!-- شماره + عنوان -->
                    <span class="text-xs font-bold text-white flex-1 truncate" :title="sg.title">
                      <span class="opacity-50 ml-1">{{ sgIdx + 1 }}.</span>{{ sg.title }}
                    </span>
                    <!-- نشانگر تعداد -->
                    <span class="text-[10px] px-2 py-0.5 rounded font-bold flex items-center gap-1"
                          :style="{ background: 'rgba(255,255,255,0.05)' }">
                      <span class="text-emerald-300">{{ (sg.tasks || []).filter(t => t.is_completed).length }}</span>
                      <span class="opacity-40">/</span>
                      <span class="text-white/70">{{ (sg.tasks || []).length }}</span>
                    </span>
                    <!-- نوار پیشرفت کوچک -->
                    <div class="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden hidden sm:block">
                      <div class="h-full transition-all"
                           :class="subGoalProgress(sg) >= 100 ? 'bg-emerald-400' : 'bg-purple-400'"
                           :style="{ width: subGoalProgress(sg) + '%' }"></div>
                    </div>
                    <!-- درصد -->
                    <span class="text-[11px] font-black w-10 text-left"
                          :class="subGoalProgress(sg) >= 100 ? 'text-emerald-300' : 'text-white/70'">
                      {{ subGoalProgress(sg) }}%
                    </span>
                  </div>

                  <!-- کارهای زیرمجموعه -->
                  <div v-if="expandedNodes[sg.id] !== false && sg.tasks && sg.tasks.length > 0"
                       class="mr-8 border-r-2 border-emerald-500/20 pr-4 mt-1 mb-2 space-y-0.5">
                    <div v-for="t in sg.tasks" :key="'task-' + t.id"
                         class="flex items-center gap-2 py-1.5 px-2.5 rounded-lg hover:bg-white/5 transition">
                      <!-- چک‌باکس -->
                      <div class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 transition"
                           :class="t.is_completed ? 'bg-emerald-500 border-emerald-500' : 'border-white/30'">
                        <Check v-if="t.is_completed" class="w-2.5 h-2.5 text-white" :stroke-width="3" />
                      </div>
                      <!-- عنوان -->
                      <span class="text-[11px] flex-1 truncate"
                            :class="t.is_completed ? 'line-through text-white/40' : 'text-white/85'">
                        {{ t.title }}
                      </span>
                      <!-- نوع کار: ساده یا دوره‌ای -->
                      <span v-if="t.recurrence_type && t.recurrence_type !== 'none'"
                            :title="`کار دوره‌ای (${recurrenceLabel(t.recurrence_type)})`"
                            class="text-[9px] px-1.5 py-0.5 rounded font-bold flex items-center gap-1 cursor-help flex-shrink-0"
                            style="background: rgba(168,85,247,0.15); color: #c4b5fd;">
                        <RotateCw class="w-2.5 h-2.5" />
                        <span>{{ recurrenceLabel(t.recurrence_type) }}</span>
                      </span>
                      <span v-else title="کار ساده"
                            class="w-4 h-4 rounded flex items-center justify-center flex-shrink-0 cursor-help"
                            style="background: rgba(99,102,241,0.12);">
                        <Circle class="w-2 h-2" style="color: #a5b4fc;" />
                      </span>
                      <!-- اولویت -->
                      <span v-if="t.priority > 0" class="text-[9px] px-1.5 py-0.5 rounded font-bold"
                            :style="{ background: t.priority >= 2 ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)', color: t.priority >= 2 ? '#fca5a5' : '#fcd34d' }">
                        {{ t.priority >= 2 ? 'فوری' : 'متوسط' }}
                      </span>
                      <!-- تاریخ سررسید (شمسی) -->
                      <span v-if="t.due_date" :title="`سررسید: ${formatDate(t.due_date)}`"
                            class="text-[9px] opacity-70 font-mono hidden md:inline-flex items-center gap-1 cursor-help"
                            :style="{ color: 'var(--text-secondary)' }">
                        <Calendar class="w-3 h-3 opacity-60" />
                        <span>سررسید: {{ formatDate(t.due_date) }}</span>
                      </span>
                    </div>
                  </div>
                  <!-- پیام خالی بودن کار -->
                  <div v-else-if="expandedNodes[sg.id] !== false"
                       class="mr-8 pr-4 py-1.5 text-[10px] opacity-50 italic">
                    بدون کار
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- فوتر modal: راهنما -->
          <div class="px-5 md:px-6 py-3 border-t border-white/10 flex items-center justify-between text-[10px] opacity-60 flex-shrink-0">
            <span class="font-bold">برای بستن: ESC یا کلیک بیرون</span>
            <span class="font-bold hidden sm:inline">{{ subGoals.length }} گام • {{ overallStats.totalTasks }} کار</span>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<style scoped>
.animate-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
</style>