<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, Filter, Search, List, 
  Calendar, RefreshCw, AlertTriangle, Eye, ArrowRight, Sparkles, Tag, Target, Flag, Clock, Layers, CheckCircle2,
  Type, Sun, Moon, HelpCircle, BookOpen, Info, CheckSquare, X
} from 'lucide-vue-next'
import api from '@/services/api'
import TaskFormModal from '@/components/TaskFormModal.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const tasks = ref([])
const goals = ref([])
const subGoals = ref([])
const categories = ref([])
const showTaskModal = ref(false)
const showHelpModal = ref(false)
const editingTask = ref(null)
const selectedTask = ref(null)
const isLoading = ref(false)
const message = ref('')
const messageType = ref('success')
const validationErrors = ref({})

// 🔤 کنترلر اندازه‌ فونت زنده (small | standard | large)
const fontSizeMode = ref('standard') 

// 🎨 کنترلر طیف رنگ فونت (bright = روشن درخشان | dark = تیره با کنتراست بالا)
const fontColorMode = ref('bright') 

const showAllTasks = ref(true)
const showFilters = ref(true)
const quickTab = ref('all') // all, today, overdue, recurring, simple, completed

const filterSearch = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterPriority = ref(null)
const filterGoalId = ref(null)
const filterRecurrence = ref('')
const filterDueDateFrom = ref('')
const filterDueDateTo = ref('')

const form = ref({
  title: '', description: '', register_date: new Date().toISOString().split('T')[0],
  duration_days: null, category: '', sub_goal_id: null, goal_id: null,
  last_action_date: '', status: 'not_started',
  recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '',
  priority: 0, auto_reschedule: true
})

const statusLabels = { 'not_started': 'شروع نشده', 'in_progress': 'در حال انجام', 'completed': 'تکمیل', 'on_hold': 'متوقف', 'cancelled': 'لغو شده' }
const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'اضطراری' }

const showToast = (msg, type = 'success') => { message.value = msg; messageType.value = type; setTimeout(() => message.value = '', 3000) }

// 🔍 تبدیل تمام اعداد فارسی/عربی به انگلیسی و اسلش به خط تیره جهت مقایسه عددی دقیق
const toEngNums = (str) => {
  if (!str) return ''
  return String(str)
    .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d))
    .replace(/\//g, '-')
}

// بررسی تسک دوره‌ای
const isTaskRecurring = (task) => {
  return task.recurrence_type && task.recurrence_type !== 'none'
}

// 🗓️ محاسبه تاریخ اقدام / مهلت بعدی تسک
const getNextActionDate = (task) => {
  if (!task.due_date && !task.last_action_date) return 'تعیین نشده'
  
  if (isTaskRecurring(task)) {
    const lastDate = task.last_action_date ? new Date(task.last_action_date) : new Date()
    const interval = Number(task.recurrence_interval) || 1
    
    if (task.recurrence_type === 'daily') lastDate.setDate(lastDate.getDate() + interval)
    else if (task.recurrence_type === 'weekly') lastDate.setDate(lastDate.getDate() + (interval * 7))
    else if (task.recurrence_type === 'monthly') lastDate.setMonth(lastDate.getMonth() + interval)
    else if (task.recurrence_type === 'yearly') lastDate.setFullYear(lastDate.getFullYear() + interval)
    
    return formatDate(lastDate.toISOString().split('T')[0])
  }
  
  return formatDate(task.due_date || task.register_date)
}

// 🚨 بررسی هوشمند و قطعی تسک عقب‌افتاده بر اساس «تاریخ اقدام بعدی موثر»
const isTaskOverdue = (task) => {
  if (task.is_completed || task.status === 'completed') return false

  // ۱. دریافت تاریخ امروز به شمسی استاندارد (مثلاً 1405-05-21)
  const now = new Date()
  const todayShamsiStr = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { 
    year: 'numeric', month: '2-digit', day: '2-digit' 
  }).format(now)
  const todayClean = toEngNums(todayShamsiStr)

  // ۲. مبنا قرار دادن «تاریخ اقدام بعدی» موثر (چه ساده چه دوره‌ای)
  let effectiveDueDate = isTaskRecurring(task) ? getNextActionDate(task) : (task.due_date || task.register_date)

  if (!effectiveDueDate) return false

  let taskDueClean = toEngNums(effectiveDueDate)

  // اگر تاریخ میلادی است (با 202x شروع می‌شود)، آن را به شمسی تبدیل کن
  if (taskDueClean.startsWith('202')) {
    const gDate = new Date(taskDueClean)
    const jStr = new Intl.DateTimeFormat('fa-IR-u-ca-persian', { 
      year: 'numeric', month: '2-digit', day: '2-digit' 
    }).format(gDate)
    taskDueClean = toEngNums(jStr)
  }

  // مقایسه: آیا تاریخ اقدام بعدی قبل از امروز است؟
  return taskDueClean < todayClean
}

// 🔤 محاسبه کلاس‌های اندازه فونت پویا
const fontSizeClasses = computed(() => {
  if (fontSizeMode.value === 'small') {
    return {
      title: 'text-base font-bold',
      desc: 'text-xs',
      badge: 'text-[10px] font-bold px-2 py-0.5',
      meta: 'text-[11px] font-bold',
      tab: 'text-xs font-bold px-3 py-1.5'
    }
  } else if (fontSizeMode.value === 'large') {
    return {
      title: 'text-xl md:text-2xl font-black',
      desc: 'text-base font-medium leading-relaxed',
      badge: 'text-xs font-black px-3.5 py-1.5',
      meta: 'text-sm md:text-base font-black',
      tab: 'text-base font-black px-6 py-3'
    }
  } else { // standard
    return {
      title: 'text-lg md:text-xl font-black',
      desc: 'text-sm font-normal leading-relaxed',
      badge: 'text-xs font-black px-3 py-1',
      meta: 'text-xs md:text-sm font-bold',
      tab: 'text-sm font-black px-5 py-2.5'
    }
  }
})

// 🎨 محاسبه کلاس‌های طیف رنگ پویا
const fontColorClasses = computed(() => {
  if (fontColorMode.value === 'dark') {
    return {
      cardBg: 'bg-slate-100 text-slate-900 border-slate-300 shadow-xl',
      title: 'text-slate-950',
      desc: 'text-slate-800 font-semibold',
      meta: 'text-slate-700 font-bold',
      border: 'border-slate-300'
    }
  } else { // bright (default)
    return {
      cardBg: 'glass-card text-white border-white/10',
      title: 'text-white',
      desc: 'text-gray-200',
      meta: 'text-gray-300',
      border: 'border-white/10'
    }
  }
})

const selectTaskForFocus = (task) => { selectedTask.value = task }
const closeTaskFocus = () => { selectedTask.value = null }

const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
    if (selectedTask.value) {
      const updated = tasks.value.find(t => t.id === selectedTask.value.id)
      if (updated) selectedTask.value = updated
    }
  } catch (e) {
    showToast('⚠️ خطا در بارگذاری تسک‌ها', 'error')
  }
}

const fetchGoals = async () => { try { const res = await api.get('/goals'); goals.value = res.data } catch (e) {} }
const fetchSubGoals = async (goalId) => { if (!goalId) { subGoals.value = []; return }; try { const res = await api.get(`/roadmap/goal/${goalId}/subgoals`); subGoals.value = res.data } catch (e) {} }
const fetchCategories = async () => { try { const res = await api.get('/tasks/categories'); categories.value = res.data } catch (e) {} }

const filteredTasks = computed(() => {
  let result = tasks.value
  const today = new Date().toISOString().split('T')[0]

  if (quickTab.value === 'today') {
    result = result.filter(t => String(t.due_date) === today || String(t.register_date) === today)
  } else if (quickTab.value === 'overdue') {
    result = result.filter(t => isTaskOverdue(t))
  } else if (quickTab.value === 'recurring') {
    result = result.filter(t => isTaskRecurring(t))
  } else if (quickTab.value === 'simple') {
    result = result.filter(t => !isTaskRecurring(t))
  } else if (quickTab.value === 'completed') {
    result = result.filter(t => t.is_completed || t.status === 'completed')
  }

  if (filterSearch.value.trim()) {
    const q = filterSearch.value.toLowerCase()
    result = result.filter(t =>
      (t.title && t.title.toLowerCase().includes(q)) ||
      (t.description && t.description.toLowerCase().includes(q))
    )
  }
  if (filterCategory.value) result = result.filter(t => t.category === filterCategory.value)
  if (filterStatus.value) result = result.filter(t => t.status === filterStatus.value)
  if (filterPriority.value !== null && filterPriority.value !== '') result = result.filter(t => t.priority === Number(filterPriority.value))
  if (filterGoalId.value) result = result.filter(t => t.goal_id === filterGoalId.value)
  if (filterDueDateFrom.value) result = result.filter(t => t.due_date && t.due_date >= filterDueDateFrom.value)
  if (filterDueDateTo.value) result = result.filter(t => t.due_date && t.due_date <= filterDueDateTo.value)
  if (filterRecurrence.value === 'has') result = result.filter(t => isTaskRecurring(t))
  if (filterRecurrence.value === 'none') result = result.filter(t => !isTaskRecurring(t))

  return result
})

const activeFilterCount = computed(() => {
  let c = 0
  if (filterSearch.value) c++
  if (filterCategory.value) c++
  if (filterStatus.value) c++
  if (filterPriority.value !== null && filterPriority.value !== '') c++
  if (filterGoalId.value) c++
  if (filterRecurrence.value) c++
  if (filterDueDateFrom.value || filterDueDateTo.value) c++
  return c
})

const resetFilters = () => {
  filterSearch.value = ''; filterCategory.value = ''; filterStatus.value = ''
  filterPriority.value = null; filterGoalId.value = null; filterRecurrence.value = ''
  filterDueDateFrom.value = ''; filterDueDateTo.value = ''; quickTab.value = 'all'
}

const openNewForm = () => {
  form.value = { 
    title: '', description: '', register_date: new Date().toISOString().split('T')[0], 
    duration_days: null, category: '', sub_goal_id: null, goal_id: null, 
    last_action_date: '', status: 'not_started', recurrence_type: 'none', 
    recurrence_interval: 1, recurrence_end_date: '', priority: 0, auto_reschedule: true 
  }
  editingTask.value = null; subGoals.value = []; validationErrors.value = {}; showTaskModal.value = true
}

const openEditForm = (task) => {
  form.value = { 
    title: task.title, description: task.description || '', 
    register_date: task.register_date || '', duration_days: task.duration_days || null, 
    category: task.category || '', sub_goal_id: task.sub_goal_id || null, 
    goal_id: task.goal_id || null, last_action_date: task.last_action_date || '', 
    status: task.status, recurrence_type: task.recurrence_type || 'none', 
    recurrence_interval: task.recurrence_interval || 1, 
    recurrence_end_date: task.recurrence_end_date || '', priority: task.priority ?? 0,
    auto_reschedule: task.auto_reschedule !== undefined ? task.auto_reschedule : true
  }
  editingTask.value = task; fetchSubGoals(task.goal_id); validationErrors.value = {}; showTaskModal.value = true
}

const onGoalChange = () => { form.value.sub_goal_id = null; fetchSubGoals(form.value.goal_id) }

const validateForm = () => {
  validationErrors.value = {}
  let hasError = false
  if (!form.value.title || !form.value.title.trim()) { validationErrors.value.title = 'عنوان تسک الزامی است'; hasError = true }
  return !hasError
}

const saveTask = async () => {
  if (!validateForm()) {
    showToast('⚠️ لطفاً عنوان تسک را وارد کنید', 'error');
    return;
  }

  try {
    isLoading.value = true;
    const data = { ...form.value }; 
    
    if (editingTask.value) {
      await api.put(`/tasks/${editingTask.value.id}`, data);
      showToast('✅ تسک بروزرسانی شد');
    } else {
      await api.post('/tasks', data);
      showToast('✅ تسک جدید ساخته شد');
    }

    showTaskModal.value = false;
    await fetchTasks();
  } catch (e) {
    showToast('❌ خطا در ذخیره تسک', 'error');
  } finally {
    isLoading.value = false;
  }
}

// ⚡ تیک زدن آنی و درج خودکار تاریخ امروز در last_action_date
const toggleTask = async (task) => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const isCurrentlyCompleted = task.is_completed || task.status === 'completed'
    const newCompletedState = !isCurrentlyCompleted
    const newStatus = newCompletedState ? 'completed' : 'not_started'

    task.is_completed = newCompletedState
    task.status = newStatus
    task.last_action_date = today

    await api.put(`/tasks/${task.id}`, {
      status: newStatus,
      is_completed: newCompletedState,
      last_action_date: today
    })

    if (newCompletedState) {
      if (isTaskRecurring(task)) {
        showToast('🔄 تسک انجام شد و برای دوره بعدی زمان‌بندی گردید')
      } else {
        showToast('🎉 تسک با موفقیت تکمیل شد و تاریخ اقدام ثبت گردید')
      }
    } else {
      showToast('🔄 تسک به حالت انجام‌نشده برگشت')
    }

    await fetchTasks()
  } catch (e) {
    showToast('❌ خطا در تغییر وضعیت تسک', 'error')
    await fetchTasks()
  }
}

const deleteTask = async (id) => { 
  if (!confirm('مطمئنی می‌خوای این تسک رو حذف کنی؟')) return; 
  try { 
    await api.delete(`/tasks/${id}`); 
    if (selectedTask.value && selectedTask.value.id === id) {
      selectedTask.value = null
    }
    showToast('🗑️ تسک حذف شد'); 
    await fetchTasks() 
  } catch (e) {} 
}

onMounted(async () => {
  await fetchTasks()
  await fetchGoals()
  await fetchCategories()

  const savedGoalId = sessionStorage.getItem('active_goal_id')
  const savedSubGoalId = sessionStorage.getItem('active_sub_goal_id')

  if (savedGoalId) {
    filterGoalId.value = Number(savedGoalId)
    await fetchSubGoals(Number(savedGoalId))
    sessionStorage.removeItem('active_goal_id')
  }

  if (savedSubGoalId) {
    filterSearch.value = ''
    sessionStorage.removeItem('active_sub_goal_id')
    showToast('📍 تسک‌های مربوط به گام انتخابی فیلتر شدند')
  }
})
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto relative min-h-screen text-right" dir="rtl" :class="themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''">

    <!-- Toast Message -->
    <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[300] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl md:text-4xl font-black mb-1 flex items-center gap-3 text-white" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''">
          <ListTodo class="w-8 h-8 text-purple-400" /> اتاق عملیات تسک‌ها
        </h1>
        <p :style="{ color: 'var(--text-secondary)' }" class="text-sm font-bold">مدیریت، زمان‌بندی و پایش پیشرفت کارهای روزانه و دوره‌ای</p>
      </div>

      <!-- 🔤 و 🎨 و 📚 دکمه‌های ابزار سربرگ -->
      <div class="flex gap-2 flex-wrap items-center">
        
        <!-- 📚 کلید راهنمای فارسی -->
        <button @click="showHelpModal = true" class="px-3.5 py-2 rounded-xl border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 font-black text-xs flex items-center gap-1.5 transition shadow-lg shadow-amber-500/10">
          <HelpCircle class="w-4 h-4 text-amber-400 animate-pulse" />
          <span>راهنما و مثال‌ها</span>
        </button>

        <!-- انتخابگر اندازه فونت -->
        <div class="flex items-center gap-1 bg-white/10 p-1 rounded-xl border border-white/10 backdrop-blur-md">
          <Type class="w-4 h-4 text-purple-400 ml-1 mr-2" />
          <button @click="fontSizeMode = 'small'" class="px-2.5 py-1 rounded-lg text-xs font-black transition" :class="fontSizeMode === 'small' ? 'bg-purple-600 text-white shadow' : 'text-gray-300 hover:bg-white/10'">کوچک</button>
          <button @click="fontSizeMode = 'standard'" class="px-2.5 py-1 rounded-lg text-xs font-black transition" :class="fontSizeMode === 'standard' ? 'bg-purple-600 text-white shadow' : 'text-gray-300 hover:bg-white/10'">استاندارد</button>
          <button @click="fontSizeMode = 'large'" class="px-2.5 py-1 rounded-lg text-xs font-black transition" :class="fontSizeMode === 'large' ? 'bg-purple-600 text-white shadow' : 'text-gray-300 hover:bg-white/10'">درشت</button>
        </div>

        <!-- انتخابگر طیف رنگ فونت -->
        <div class="flex items-center gap-1 bg-white/10 p-1 rounded-xl border border-white/10 backdrop-blur-md">
          <button @click="fontColorMode = 'bright'" title="طیف روشن درخشان" class="p-1.5 rounded-lg transition" :class="fontColorMode === 'bright' ? 'bg-amber-500 text-slate-950 shadow' : 'text-gray-300 hover:bg-white/10'"><Sun class="w-4 h-4" /></button>
          <button @click="fontColorMode = 'dark'" title="طیف تیره با کنتراست بالا" class="p-1.5 rounded-lg transition" :class="fontColorMode === 'dark' ? 'bg-purple-600 text-white shadow' : 'text-gray-300 hover:bg-white/10'"><Moon class="w-4 h-4" /></button>
        </div>

        <button @click="showAllTasks = !showAllTasks" class="px-3.5 py-2 rounded-xl transition flex items-center gap-2 text-xs font-bold" :style="showAllTasks ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <List class="w-4 h-4" /> {{ showAllTasks ? 'کارتی' : 'فشرده' }}
        </button>
        
        <button @click="showFilters = !showFilters" class="px-3.5 py-2 rounded-xl transition flex items-center gap-2 text-xs font-bold relative" :style="{ background: showFilters ? 'var(--accent)' : 'var(--bg-hover)', color: showFilters ? '#fff' : 'var(--text-secondary)' }">
          <Filter class="w-4 h-4" /> فیلترها <span v-if="activeFilterCount > 0" class="w-4 h-4 rounded-full text-white text-[9px] flex items-center justify-center font-bold bg-red-500">{{ activeFilterCount }}</span>
        </button>
        
        <button @click="openNewForm" class="px-4 py-2 rounded-xl text-white font-black text-xs md:text-sm transition flex items-center gap-2 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
          <Plus class="w-4 h-4" /> تسک جدید
        </button>
      </div>
    </div>

    <!-- 🌟 تب‌های فیلتر سریع -->
    <div class="flex items-center gap-2 overflow-x-auto pb-3 mb-6">
      <button @click="quickTab = 'all'" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'all' ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">
        همه تسک‌ها ({{ tasks.length }})
      </button>
      <button @click="quickTab = 'today'" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'today' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">
        ☀️ کارهای امروز
      </button>
      <button @click="quickTab = 'overdue'" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'overdue' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30 font-black' : 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20']">
        🚨 عقب‌افتاده‌ها ({{ tasks.filter(t => isTaskOverdue(t)).length }})
      </button>
      <button @click="quickTab = 'recurring'" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'recurring' ? 'bg-amber-500 text-slate-950 font-black shadow-lg shadow-amber-500/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">
        🔄 تسک‌های دوره‌ای
      </button>
      <button @click="quickTab = 'simple'" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'simple' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">
        📌 تسک‌های ساده
      </button>
      <button @click="quickTab = 'completed'" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'completed' ? 'bg-gray-600 text-white shadow-lg' : 'bg-white/5 text-gray-300 hover:bg-white/10']">
        ✅ تکمیل‌شده‌ها
      </button>
    </div>

    <!-- کادر فیلترهای پیشرفته -->
    <div v-if="showFilters" class="mb-6 p-4 rounded-2xl space-y-3 glass-card border border-white/10 animate-in fade-in duration-200">
      <div class="relative">
        <Search class="absolute right-3 top-3 w-4 h-4 text-gray-400" />
        <input v-model="filterSearch" placeholder="جستجو در عنوان و توضیحات تسک‌ها..." class="w-full pr-10 pl-4 py-3 rounded-xl text-sm font-bold bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-purple-500" />
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <select v-model="filterCategory" class="px-3 py-2.5 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option value="">همه دسته‌بندی‌ها</option><option v-for="c in categories" :key="c.value || c" :value="c.value || c">{{ c.label || c }}</option></select>
        <select v-model="filterStatus" class="px-3 py-2.5 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option value="">همه وضعیت‌ها</option><option v-for="(l,k) in statusLabels" :key="k" :value="k">{{ l }}</option></select>
        <select v-model="filterPriority" class="px-3 py-2.5 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option :value="null">همه اولویت‌ها</option><option :value="0">عادی</option><option :value="1">مهم</option><option :value="2">اضطراری</option></select>
        <select v-model="filterGoalId" class="px-3 py-2.5 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option :value="null">همه اهداف</option><option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option></select>
      </div>
      <button @click="resetFilters" class="px-4 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-gray-300 transition">پاکسازی فیلترها</button>
    </div>

    <!-- حالت بدون تسک -->
    <div v-if="filteredTasks.length === 0" class="text-center py-20 glass-card rounded-3xl border border-white/10">
      <div class="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4 text-purple-400">
        <Search class="w-8 h-8" />
      </div>
      <p class="text-xl font-black text-white mb-1">{{ tasks.length === 0 ? 'هنوز تسکی ثبت نکرده‌اید!' : 'تسکی با این فیلترها پیدا نشد' }}</p>
      <p class="text-sm text-gray-400 mb-4">می‌توانید تسک جدیدی برای امروز بپردازید.</p>
      <button @click="openNewForm" class="px-6 py-3 bg-purple-600 text-white font-black rounded-xl text-xs hover:bg-purple-500 transition">ساخت تسک جدید</button>
    </div>

    <!-- 🌟 لیست کارت‌های تسک -->
    <div v-else-if="showAllTasks" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div 
        v-for="task in filteredTasks" 
        :key="task.id" 
        @click="selectTaskForFocus(task)"
        class="p-6 rounded-3xl border-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer flex flex-col justify-between relative group"
        :class="[
          fontColorClasses.cardBg,
          isTaskOverdue(task) ? 'border-red-500 bg-red-500/10 shadow-[0_0_25px_rgba(239,68,68,0.3)]' :
          isTaskRecurring(task) ? 'border-purple-500/40 shadow-[0_0_20px_rgba(168,85,247,0.1)]' :
          fontColorClasses.border
        ]"
      >
        <div>
          <!-- هدر کارت تسک -->
          <div class="flex items-center justify-between gap-2 mb-3">
            
            <div class="flex items-center gap-1.5 flex-wrap">
              <span v-if="isTaskOverdue(task)" class="rounded-xl bg-red-500/30 text-red-300 border border-red-500/50 flex items-center gap-1 font-black" :class="fontSizeClasses.badge">
                <AlertTriangle class="w-3.5 h-3.5 animate-bounce" /> 🚨 عقب‌افتاده
              </span>

              <span v-if="isTaskRecurring(task)" class="rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1" :class="fontSizeClasses.badge">
                <RefreshCw class="w-3.5 h-3.5" /> 🔄 {{ task.recurrence_type === 'daily' ? 'روزانه' : task.recurrence_type === 'weekly' ? 'هفتگی' : task.recurrence_type === 'monthly' ? 'ماهانه' : 'دوره‌ای' }}
              </span>

              <span v-else class="rounded-xl bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1" :class="fontSizeClasses.badge">
                <Tag class="w-3.5 h-3.5" /> 📌 ساده
              </span>
            </div>

            <div class="flex items-center gap-1" @click.stop>
              <button @click="openEditForm(task)" title="ویرایش" class="p-2 text-gray-400 hover:text-white transition"><Edit3 class="w-4 h-4" /></button>
              <button @click="deleteTask(task.id)" title="حذف" class="p-2 text-gray-400 hover:text-red-400 transition"><Trash2 class="w-4 h-4" /></button>
            </div>
          </div>

          <!-- عنوان تسک و چک‌باکس -->
          <div class="flex items-start gap-3 mb-3" @click.stop="toggleTask(task)">
            <button class="w-7 h-7 rounded-xl border-2 flex items-center justify-center transition-all mt-0.5 flex-shrink-0" :class="(task.is_completed || task.status === 'completed') ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30 text-transparent'">
              <Check class="w-5 h-5" />
            </button>
            <h3 class="leading-snug transition" :class="[fontSizeClasses.title, fontColorClasses.title, (task.is_completed || task.status === 'completed') ? 'line-through opacity-40' : '', isTaskOverdue(task) ? 'text-red-300 font-black' : '']">
              {{ task.title }}
            </h3>
          </div>

          <!-- توضیحات -->
          <p v-if="task.description" class="line-clamp-2 mb-4 mr-10" :class="[fontSizeClasses.desc, fontColorClasses.desc]">{{ task.description }}</p>
        </div>

        <!-- 🗓️ فوتر کارت: نمایش صریح تاریخ اقدام / مهلت بعدی + تاریخ آخرین اقدام -->
        <div class="pt-3 border-t space-y-1.5" :class="fontColorClasses.border">
          <div class="flex items-center justify-between text-xs font-bold" :class="fontColorClasses.meta">
            <span class="flex items-center gap-1.5" :class="isTaskOverdue(task) ? 'text-red-400 font-black' : ''">
              <Calendar class="w-4 h-4 text-purple-400" /> 
              <span>اقدام بعدی:</span> 
              <span class="font-black" :class="isTaskOverdue(task) ? 'text-red-400 animate-pulse' : 'text-amber-300'">{{ getNextActionDate(task) }}</span>
            </span>

            <button @click.stop="selectTaskForFocus(task)" class="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded-xl font-black text-xs flex items-center gap-1 transition">
              <Eye class="w-4 h-4 text-amber-400" /> تمرکز
            </button>
          </div>

          <div v-if="task.last_action_date" class="text-[11px] opacity-70 flex items-center gap-1" :class="fontColorClasses.meta">
            <CheckCircle2 class="w-3.5 h-3.5 text-emerald-400" />
            <span>آخرین تکمیل / اقدام: {{ formatDate(task.last_action_date) }}</span>
          </div>
        </div>

      </div>
    </div>

    <!-- نمای فشرده/لیستی -->
    <div v-else class="space-y-3">
      <div 
        v-for="task in filteredTasks" 
        :key="task.id" 
        @click="selectTaskForFocus(task)"
        class="flex items-center justify-between gap-4 px-5 py-4 rounded-2xl transition cursor-pointer border"
        :class="[
          fontColorClasses.cardBg,
          isTaskOverdue(task) ? 'bg-red-500/20 border-red-500/50' :
          isTaskRecurring(task) ? 'bg-purple-500/10 border-purple-500/20' :
          fontColorClasses.border
        ]"
      >
        <div class="flex items-center gap-3 flex-1 min-w-0" @click.stop="toggleTask(task)">
          <button class="w-6 h-6 rounded-lg border-2 flex items-center justify-center flex-shrink-0 transition" :class="(task.is_completed || task.status === 'completed') ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30 text-transparent'">
            <Check class="w-4 h-4" />
          </button>
          <span class="truncate font-black" :class="[fontSizeClasses.title, fontColorClasses.title, (task.is_completed || task.status === 'completed') ? 'line-through opacity-40' : '', isTaskOverdue(task) ? 'text-red-400' : '']">{{ task.title }}</span>
        </div>

        <div class="flex items-center gap-2 flex-shrink-0" @click.stop>
          <span class="text-xs font-bold" :class="isTaskOverdue(task) ? 'text-red-400' : 'text-amber-300'">اقدام بعدی: {{ getNextActionDate(task) }}</span>
          <button @click="openEditForm(task)" class="p-1.5 text-gray-300 hover:text-white"><Edit3 class="w-4 h-4" /></button>
          <button @click="deleteTask(task.id)" class="p-1.5 text-gray-300 hover:text-red-400"><Trash2 class="w-4 h-4" /></button>
        </div>
      </div>
    </div>

    <!-- 📚📚 مودال راهنمای فارسی جامع -->
    <div v-if="showHelpModal" class="fixed inset-0 z-[500] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-300" @click.self="showHelpModal = false">
      <div class="w-full max-w-4xl rounded-3xl p-6 md:p-8 max-h-[90vh] overflow-y-auto border-2 border-amber-500/40 shadow-[0_0_60px_rgba(245,158,11,0.2)] bg-slate-900 text-white relative">
        <div class="flex items-center justify-between pb-4 mb-6 border-b border-white/10">
          <div class="flex items-center gap-3">
            <div class="p-3 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <BookOpen class="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h3 class="text-xl md:text-2xl font-black text-white">راهنمای جامع تعریف تسک‌ها و منطق برنامه</h3>
              <p class="text-xs text-gray-400 mt-1">آموزش گام‌به‌گام تعریف تسک‌های ساده و دوره‌ای با مثال‌های عملی</p>
            </div>
          </div>
          <button @click="showHelpModal = false" class="p-2 text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
        </div>

        <div class="space-y-8 text-right">
          <div class="p-5 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <h4 class="text-base font-black text-amber-400 flex items-center gap-2">
              <Info class="w-5 h-5" /> منطق محاسباتی تاریخ‌ها و تکرار تسک‌ها
            </h4>
            <ul class="text-xs md:text-sm text-gray-300 space-y-2 leading-relaxed list-disc list-inside">
              <li><strong class="text-white">تسک‌های ساده (یک‌باره):</strong> یک تاریخ ثبت و مدت زمان دارند. پس از تیک خوردن، وضعیت به «تکمیل‌شده» تغییر کرده و تاریخ انجام در «آخرین اقدام» ثبت می‌شود.</li>
              <li><strong class="text-white">تسک‌های دوره‌ای (تکرارشونده):</strong> بازه تکرار دارند. با تیک زدن هر دوره، تاریخ امروز در «آخرین اقدام» ثبت شده و تاریخ مهلت بعدی خودکار برای دوره آینده تنظیم می‌شود.</li>
              <li><strong class="text-white">تسک‌های عقب‌افتاده:</strong> هر تسکی که تاریخ مهلت آن قبل از امروز باشد و تیک نخورده باشد، قرمز و در تب «عقب‌افتاده‌ها» قرار می‌گیرد.</li>
            </ul>
          </div>
        </div>

        <div class="mt-8 pt-4 border-t border-white/10 flex justify-end">
          <button @click="showHelpModal = false" class="px-6 py-2.5 bg-amber-500 text-slate-950 font-black rounded-xl text-xs shadow-lg">متوجه شدم</button>
        </div>
      </div>
    </div>

    <!-- 🌟 حالت تمرکز هوشمند روی تسک انتخابی -->
    <div v-if="selectedTask" class="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-300" @click.self="closeTaskFocus">
      <div class="w-full max-w-3xl rounded-3xl p-8 max-h-[90vh] overflow-y-auto border-2 border-purple-500/50 shadow-[0_0_60px_rgba(168,85,247,0.3)] bg-slate-900 text-white relative animate-in zoom-in-95 duration-300">
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
          <button @click="closeTaskFocus" class="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-black rounded-2xl shadow-xl transition flex items-center gap-2">
            <ArrowRight class="w-5 h-5" />
            <span>بازگشت به لیست تسک‌ها</span>
          </button>
          <div class="flex items-center gap-2">
            <button @click="openEditForm(selectedTask)" class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5"><Edit3 class="w-4 h-4 text-purple-400" /> ویرایش</button>
            <button @click="deleteTask(selectedTask.id)" class="px-4 py-2 bg-red-500/20 text-red-400 font-bold rounded-xl text-xs transition flex items-center gap-1.5"><Trash2 class="w-4 h-4" /> حذف</button>
          </div>
        </div>

        <div class="flex items-center gap-2 mb-4 flex-wrap">
          <span class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-300 font-black text-xs"><Sparkles class="w-4 h-4 text-amber-400 animate-spin" /> شناسنامه کامل تسک</span>
          <span v-if="isTaskOverdue(selectedTask)" class="px-3.5 py-1.5 rounded-full bg-red-500/30 text-red-300 font-black text-xs border border-red-500/50">🚨 عقب‌افتاده</span>
          <span v-if="isTaskRecurring(selectedTask)" class="px-3.5 py-1.5 rounded-full bg-amber-500/20 text-amber-300 font-black text-xs border border-amber-500/30">🔄 تکرارشونده</span>
        </div>

        <div class="flex items-start gap-4 mb-6 pb-6 border-b border-white/10">
          <button @click="toggleTask(selectedTask)" class="w-10 h-10 rounded-xl border-2 flex items-center justify-center transition-all mt-1 flex-shrink-0" :class="(selectedTask.is_completed || selectedTask.status === 'completed') ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30 text-transparent'"><Check class="w-6 h-6" /></button>
          <div>
            <h2 class="text-2xl md:text-3xl font-black text-white mb-2" :class="(selectedTask.is_completed || selectedTask.status === 'completed') ? 'line-through opacity-40' : ''">{{ selectedTask.title }}</h2>
            <p v-if="selectedTask.description" class="text-base text-gray-200 leading-relaxed whitespace-pre-line">{{ selectedTask.description }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2.5 bg-blue-500/20 text-blue-400 rounded-xl"><Flag class="w-5 h-5" /></div><div><p class="text-xs text-gray-400 font-bold">درجه اولویت</p><p class="text-base font-black text-white">{{ priorityLabels[selectedTask.priority] || 'عادی' }}</p></div></div>
          <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2.5 bg-purple-500/20 text-purple-400 rounded-xl"><Tag class="w-5 h-5" /></div><div><p class="text-xs text-gray-400 font-bold">دسته‌بندی</p><p class="text-base font-black text-white">{{ selectedTask.category || 'عمومی' }}</p></div></div>
          <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2.5 bg-amber-500/20 text-amber-400 rounded-xl"><Clock class="w-5 h-5" /></div><div><p class="text-xs text-gray-400 font-bold">تاریخ اقدام / مهلت بعدی</p><p class="text-base font-black text-amber-300">{{ getNextActionDate(selectedTask) }}</p></div></div>
          <div v-if="selectedTask.last_action_date" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2.5 bg-emerald-500/20 text-emerald-400 rounded-xl"><CheckCircle2 class="w-5 h-5" /></div><div><p class="text-xs text-gray-400 font-bold">تاریخ آخرین تکمیل / اقدام</p><p class="text-base font-bold text-white">{{ formatDate(selectedTask.last_action_date) }}</p></div></div>
        </div>

        <div class="flex justify-end pt-4 border-t border-white/10">
          <button @click="closeTaskFocus" class="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition">بستن حالت تمرکز</button>
        </div>
      </div>
    </div>

    <TaskFormModal
      v-model="showTaskModal"
      :form="form"
      :validation-errors="validationErrors"
      :categories="categories"
      :goals="goals"
      :sub-goals="subGoals"
      :editing-task="editingTask"
      :is-loading="isLoading"
      @update:form="(value) => form = value"
      @goal-change="onGoalChange"
      @save="saveTask"
    />
  </div>
</template>