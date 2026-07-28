<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, X, Calendar, Clock, RefreshCw, Filter, Search, Layers, Target, List, Grid3X3, ChevronDown, ChevronUp } from 'lucide-vue-next'
import api from '@/services/api'

const themeStore = useThemeStore()
const tasks = ref([])
const goals = ref([])
const subGoals = ref([])
const categories = ref([])
const showForm = ref(false)
const editingTask = ref(null)
const isLoading = ref(false)
const message = ref('')
const messageType = ref('success')

// نمایش
const viewMode = ref('list') // list, compact
const showAllTasks = ref(false)
const expandedTasks = ref({})

// فیلترها
const showFilters = ref(true)
const filterSearch = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterPriority = ref(null)
const filterGoalId = ref(null)
const filterRecurrence = ref('')
const filterDueDateFrom = ref('')
const filterDueDateTo = ref('')

// فرم
const form = ref({
  title: '', description: '', register_date: new Date().toISOString().split('T')[0],
  due_date: '', category: '', sub_goal_id: null, goal_id: null,
  last_action_date: '', status: 'not_started',
  recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '',
  priority: 0
})

const categoryLabels = {
  'work': 'کاری', 'personal': 'شخصی', 'health': 'سلامتی',
  'study': 'مطالعه', 'finance': 'مالی', 'other': 'سایر'
}
const statusLabels = {
  'not_started': 'شروع نشده', 'in_progress': 'در حال انجام',
  'completed': 'تکمیل', 'on_hold': 'متوقف', 'cancelled': 'لغو شده'
}
const statusColors = {
  'not_started': '#888', 'in_progress': '#8b5cf6',
  'completed': '#22c55e', 'on_hold': '#f59e0b', 'cancelled': '#ef4444'
}
const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'اضطراری' }
const recurrenceLabels = { 'none': 'بدون تکرار', 'daily': 'روزانه', 'weekly': 'هفتگی', 'monthly': 'ماهانه', 'yearly': 'سالیانه' }

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

// ====== Fetch ======
const fetchTasks = async () => {
  try {
    let url = '/tasks?limit=200&'
    if (filterCategory.value) url += `category=${filterCategory.value}&`
    if (filterStatus.value) url += `status=${filterStatus.value}&`
    if (filterPriority.value !== null && filterPriority.value !== '') url += `priority=${filterPriority.value}&`
    if (filterGoalId.value) url += `goal_id=${filterGoalId.value}&`
    const res = await api.get(url)
    tasks.value = res.data
  } catch (e) { console.error(e) }
}

const fetchGoals = async () => {
  try { const res = await api.get('/goals'); goals.value = res.data } catch (e) {}
}

const fetchSubGoals = async (goalId) => {
  if (!goalId) { subGoals.value = []; return }
  try { const res = await api.get(`/roadmap/goal/${goalId}/subgoals`); subGoals.value = res.data } catch (e) {}
}

const fetchCategories = async () => {
  try { const res = await api.get('/tasks/categories'); categories.value = res.data } catch (e) {}
}

// ====== Filtered Tasks ======
const filteredTasks = computed(() => {
  let result = tasks.value

  // جستجوی متنی
  if (filterSearch.value.trim()) {
    const q = filterSearch.value.toLowerCase()
    result = result.filter(t => 
      t.title.toLowerCase().includes(q) ||
      (t.description && t.description.toLowerCase().includes(q)) ||
      (t.category && categoryLabels[t.category]?.includes(q))
    )
  }

  // تاریخ سررسید
  if (filterDueDateFrom.value) {
    result = result.filter(t => t.due_date && t.due_date >= filterDueDateFrom.value)
  }
  if (filterDueDateTo.value) {
    result = result.filter(t => t.due_date && t.due_date <= filterDueDateTo.value)
  }

  // تکرار
  if (filterRecurrence.value) {
    if (filterRecurrence.value === 'has') {
      result = result.filter(t => t.recurrence_type && t.recurrence_type !== 'none')
    } else if (filterRecurrence.value === 'none') {
      result = result.filter(t => !t.recurrence_type || t.recurrence_type === 'none')
    }
  }

  return result
})

const activeFilterCount = computed(() => {
  let count = 0
  if (filterSearch.value) count++
  if (filterCategory.value) count++
  if (filterStatus.value) count++
  if (filterPriority.value !== null && filterPriority.value !== '') count++
  if (filterGoalId.value) count++
  if (filterRecurrence.value) count++
  if (filterDueDateFrom.value || filterDueDateTo.value) count++
  return count
})

const resetFilters = () => {
  filterSearch.value = ''
  filterCategory.value = ''
  filterStatus.value = ''
  filterPriority.value = null
  filterGoalId.value = null
  filterRecurrence.value = ''
  filterDueDateFrom.value = ''
  filterDueDateTo.value = ''
}

// ====== CRUD ======
const openNewForm = () => {
  form.value = {
    title: '', description: '', register_date: new Date().toISOString().split('T')[0],
    due_date: '', category: '', sub_goal_id: null, goal_id: null,
    last_action_date: '', status: 'not_started',
    recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '',
    priority: 0
  }
  editingTask.value = null; subGoals.value = []; showForm.value = true
}

const openEditForm = (task) => {
  form.value = {
    title: task.title, description: task.description || '',
    register_date: task.register_date || '', due_date: task.due_date || '',
    category: task.category || '', sub_goal_id: task.sub_goal_id || null,
    goal_id: task.goal_id || null, last_action_date: task.last_action_date || '',
    status: task.status, recurrence_type: task.recurrence_type || 'none',
    recurrence_interval: task.recurrence_interval || 1,
    recurrence_end_date: task.recurrence_end_date || '',
    priority: task.priority
  }
  editingTask.value = task; fetchSubGoals(task.goal_id); showForm.value = true
}

const onGoalChange = () => { form.value.sub_goal_id = null; fetchSubGoals(form.value.goal_id) }

const saveTask = async () => {
  if (!form.value.title.trim()) return
  isLoading.value = true
  try {
    const data = { ...form.value }
    if (!data.sub_goal_id) data.sub_goal_id = null
    if (!data.goal_id) data.goal_id = null
    if (!data.due_date) data.due_date = null
    if (editingTask.value) {
      await api.put(`/tasks/${editingTask.value.id}`, data)
      showToast('✅ تسک بروزرسانی شد')
    } else {
      await api.post('/tasks', data)
      showToast('✅ تسک جدید ایجاد شد')
    }
    showForm.value = false; editingTask.value = null; await fetchTasks()
  } catch (e) { showToast('❌ خطا در ذخیره', 'error') } finally { isLoading.value = false }
}

const toggleTask = async (task) => {
  const newStatus = task.status === 'completed' ? 'not_started' : 'completed'
  await api.put(`/tasks/${task.id}`, { status: newStatus, is_completed: newStatus === 'completed' })
  await fetchTasks()
}

const deleteTask = async (id) => {
  if (!confirm('مطمئنی؟')) return
  try { await api.delete(`/tasks/${id}`); showToast('🗑️ تسک حذف شد'); await fetchTasks() } catch (e) {}
}

const toggleExpand = (id) => { expandedTasks.value[id] = !expandedTasks.value[id] }

const daysUntilClass = (days) => {
  if (days === null || days === undefined) return ''
  if (days < 0) return 'text-red-400 font-bold'
  if (days <= 2) return 'text-orange-400 font-bold'
  if (days <= 7) return 'text-yellow-400'
  return 'text-gray-400'
}

// Watch filters
watch([filterCategory, filterStatus, filterPriority, filterGoalId], () => {
  fetchTasks()
})

onMounted(() => { fetchTasks(); fetchGoals(); fetchCategories() })
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto relative min-h-screen"
       :class="themeStore.currentTheme === 'persian-classic' ? 'page-bg-tasks' : themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''">
    
    <!-- Toast -->
    <div v-if="message" 
         class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-extrabold mb-1" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">تسک‌ها</h1>
        <p :style="{ color: 'var(--text-secondary)' }">
          {{ filteredTasks.length }} تسک
          <span v-if="activeFilterCount > 0">({{ activeFilterCount }} فیلتر فعال)</span>
        </p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <!-- نمایش همه -->
        <button @click="showAllTasks = !showAllTasks" 
                class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm"
                :style="showAllTasks ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <List class="w-4 h-4" /> 
          {{ showAllTasks ? 'نمایش فشرده' : 'نمایش همه' }}
        </button>

        <!-- فیلتر -->
        <button @click="showFilters = !showFilters" 
                class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm relative"
                :style="{ background: showFilters ? 'var(--accent)' : 'var(--bg-hover)', color: showFilters ? '#fff' : 'var(--text-secondary)' }">
          <Filter class="w-4 h-4" /> فیلترها
          <span v-if="activeFilterCount > 0" 
                class="absolute -top-1 -right-1 w-5 h-5 rounded-full text-white text-xs flex items-center justify-center font-bold"
                style="background: #ef4444">{{ activeFilterCount }}</span>
        </button>

        <button @click="openNewForm" 
                class="px-5 py-2 rounded-xl text-white font-semibold transition flex items-center gap-2"
                :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> تسک جدید
        </button>
      </div>
    </div>

    <!-- ========== فیلترها ========== -->
    <div v-if="showFilters" 
         class="mb-6 p-4 rounded-xl space-y-3"
         :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      
      <!-- جستجو -->
      <div class="relative">
        <Search class="absolute right-3 top-2.5 w-5 h-5" :style="{ color: 'var(--text-secondary)' }" />
        <input v-model="filterSearch" placeholder="جستجو در عنوان و توضیحات..."
               class="w-full pr-10 pl-4 py-2.5 rounded-lg text-sm"
               :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
      </div>

      <!-- ردیف ۱ فیلترها -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <select v-model="filterCategory" 
                class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option value="">همه دسته‌بندی‌ها</option>
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>

        <select v-model="filterStatus" 
                class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option value="">همه وضعیت‌ها</option>
          <option v-for="(label, key) in statusLabels" :key="key" :value="key">{{ label }}</option>
        </select>

        <select v-model="filterPriority" 
                class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option :value="null">همه اهمیت‌ها</option>
          <option :value="0">عادی</option>
          <option :value="1">مهم</option>
          <option :value="2">اضطراری</option>
        </select>

        <select v-model="filterGoalId" 
                class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option :value="null">همه اهداف</option>
          <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
        </select>
      </div>

      <!-- ردیف ۲ فیلترها -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <select v-model="filterRecurrence" 
                class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option value="">همه تکرارها</option>
          <option value="has">دارای تکرار</option>
          <option value="none">بدون تکرار</option>
        </select>

        <input v-model="filterDueDateFrom" type="date" placeholder="مهلت از"
               class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
        
        <input v-model="filterDueDateTo" type="date" placeholder="مهلت تا"
               class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />

        <button @click="resetFilters" 
                class="px-3 py-2 rounded-lg text-sm transition hover:bg-red-500/10"
                :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          حذف همه فیلترها
        </button>
      </div>
    </div>

    <!-- ========== لیست تسک‌ها ========== -->
    <div v-if="filteredTasks.length === 0" class="text-center py-20">
      <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4" :style="{ background: 'var(--bg-hover)' }">
        <Search class="w-10 h-10" :style="{ color: 'var(--accent)' }" />
      </div>
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">
        {{ tasks.length === 0 ? 'هنوز تسکی ثبت نکردی!' : 'تسکی با این فیلترها پیدا نشد' }}
      </p>
      <p :style="{ color: 'var(--text-secondary)' }">
        {{ tasks.length === 0 ? 'اولین تسک رو با ۱۱ فیلد پیشرفته بساز.' : 'فیلترها رو تغییر بده.' }}
      </p>
    </div>

    <!-- نمایش همه (Compact) -->
    <div v-if="showAllTasks && filteredTasks.length > 0" class="space-y-1">
      <div v-for="task in filteredTasks" :key="task.id"
           class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition"
           :style="{ background: task.status === 'completed' ? 'var(--bg-primary)' : 'var(--bg-hover)', opacity: task.status === 'completed' ? 0.6 : 1 }">
        <button @click="toggleTask(task)" 
                class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0"
                :style="{ background: task.status === 'completed' ? 'var(--accent)' : 'transparent', borderColor: task.status === 'completed' ? 'var(--accent)' : 'var(--border)' }">
          <Check v-if="task.status === 'completed'" class="w-3 h-3 text-white" />
        </button>
        <span class="flex-1 truncate" :style="{ color: 'var(--text-primary)', textDecoration: task.status === 'completed' ? 'line-through' : 'none' }">{{ task.title }}</span>
        <span v-if="task.priority === 2" class="text-red-400 text-xs">⚡</span>
        <span v-if="task.due_date" class="text-xs" :class="daysUntilClass(task.days_until_due)">{{ task.due_date }}</span>
        <button @click="openEditForm(task)" class="p-1 rounded hover:bg-white/10 opacity-0 group-hover:opacity-100" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-3 h-3" /></button>
        <button @click="deleteTask(task.id)" class="p-1 rounded hover:bg-red-500/10 opacity-0 group-hover:opacity-100" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-3 h-3" /></button>
      </div>
    </div>

    <!-- نمایش کامل (Detail) -->
    <div v-if="!showAllTasks && filteredTasks.length > 0" class="space-y-2">
      <div v-for="task in filteredTasks" :key="task.id"
           class="rounded-xl overflow-hidden transition-all duration-200 border"
           :style="{ 
             background: task.status === 'completed' ? 'var(--bg-primary)' : 'var(--bg-card)',
             borderColor: task.priority === 2 ? 'rgba(239,68,68,0.3)' : 'var(--border)',
             opacity: task.status === 'completed' ? 0.6 : 1
           }">
        
        <div class="flex items-start gap-3 p-4 cursor-pointer" @click="toggleExpand(task.id)">
          <button @click.stop="toggleTask(task)" 
                  class="w-5 h-5 rounded-lg border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition"
                  :style="{ 
                    background: task.status === 'completed' ? 'var(--accent)' : 'transparent',
                    borderColor: task.status === 'completed' ? 'var(--accent)' : 'var(--border)'
                  }">
            <Check v-if="task.status === 'completed'" class="w-3.5 h-3.5 text-white" />
          </button>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="font-semibold" :style="{ color: 'var(--text-primary)', textDecoration: task.status === 'completed' ? 'line-through' : 'none' }">
                {{ task.title }}
              </h3>
              <span v-if="task.priority === 2" class="text-xs px-1.5 py-0.5 rounded-full font-bold text-red-400" style="background: rgba(239,68,68,0.15)">اضطراری</span>
              <span v-else-if="task.priority === 1" class="text-xs px-1.5 py-0.5 rounded-full font-bold text-orange-400" style="background: rgba(249,115,22,0.15)">مهم</span>
              <span class="text-xs px-1.5 py-0.5 rounded-full" :style="{ background: statusColors[task.status] + '20', color: statusColors[task.status] }">
                {{ statusLabels[task.status] }}
              </span>
            </div>

            <div class="flex flex-wrap gap-2 mt-1.5 text-xs">
              <span v-if="task.category" class="flex items-center gap-1 px-1.5 py-0.5 rounded-full" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
                {{ categoryLabels[task.category] || task.category }}
              </span>
              <span v-if="task.register_date" :style="{ color: 'var(--text-secondary)' }">📅 {{ task.register_date }}</span>
              <span v-if="task.due_date" :class="['flex items-center gap-1', daysUntilClass(task.days_until_due)]">
                ⏰ {{ task.due_date }}
                <span v-if="task.days_until_due !== null && task.days_until_due < 0" class="text-red-400">({{ Math.abs(task.days_until_due) }} روز گذشته)</span>
                <span v-else-if="task.days_until_due === 0" class="text-orange-400">(امروز)</span>
                <span v-else>({{ task.days_until_due }} روز)</span>
              </span>
              <span v-if="task.recurrence_type && task.recurrence_type !== 'none'" :style="{ color: 'var(--text-secondary)' }">🔄 {{ recurrenceLabels[task.recurrence_type] }}</span>
              <span v-if="task.goal_id" :style="{ color: 'var(--accent)' }">🎯 {{ task.goal?.title || 'هدف' }}</span>
            </div>
          </div>

          <div class="flex gap-1 flex-shrink-0" @click.stop>
            <button @click="openEditForm(task)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-4 h-4" /></button>
            <button @click="deleteTask(task.id)" class="p-1.5 rounded-lg hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-4 h-4" /></button>
            <button class="p-1.5" :style="{ color: 'var(--text-secondary)' }">
              <ChevronDown v-if="!expandedTasks[task.id]" class="w-4 h-4" />
              <ChevronUp v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- جزئیات بیشتر -->
        <div v-if="expandedTasks[task.id]" class="px-4 pb-4 border-t" :style="{ borderColor: 'var(--border)' }">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
            <div><span :style="{ color: 'var(--text-secondary)' }">توضیحات:</span> <span :style="{ color: 'var(--text-primary)' }">{{ task.description || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت:</span> <span :style="{ color: 'var(--text-primary)' }">{{ task.register_date || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">آخرین اقدام:</span> <span :style="{ color: 'var(--text-primary)' }">{{ task.last_action_date || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تکرار:</span> <span :style="{ color: 'var(--text-primary)' }">{{ recurrenceLabels[task.recurrence_type] || 'ندارد' }} {{ task.recurrence_type !== 'none' ? 'هر ' + task.recurrence_interval : '' }}</span></div>
            <div v-if="task.sub_goal"><span :style="{ color: 'var(--text-secondary)' }">زیرهدف:</span> <span :style="{ color: 'var(--accent)' }">{{ task.sub_goal?.title }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">روزهای مانده:</span> <span :class="daysUntilClass(task.days_until_due)">{{ task.days_until_due !== null ? task.days_until_due + ' روز' : '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تا تکرار بعدی:</span> <span :style="{ color: 'var(--text-primary)' }">{{ task.days_until_recurrence !== null ? task.days_until_recurrence + ' روز' : '-' }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== مودال ========== -->
    <div v-if="showForm" class="fixed inset-0 z-[100] flex items-start justify-center p-4 pt-20 pb-20 bg-black/60 backdrop-blur-sm overflow-y-auto" @click.self="showForm = false">
      <div class="w-full max-w-2xl rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingTask ? 'ویرایش تسک' : 'تسک جدید' }}</h2>
          <button @click="showForm = false" :style="{ color: 'var(--text-secondary)' }"><X class="w-6 h-6" /></button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">عنوان تسک *</label>
            <input v-model="form.title" placeholder="عنوان تسک" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>

          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">توضیحات</label>
            <textarea v-model="form.description" rows="2" placeholder="توضیحات" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۱- تاریخ ثبت</label>
              <input v-model="form.register_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۳- مهلت انجام</label>
              <input v-model="form.due_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۴- دسته‌بندی</label>
              <select v-model="form.category" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option value="">انتخاب کنید...</option>
                <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۱۱- اهمیت</label>
              <div class="flex gap-2">
                <button v-for="(label, val) in priorityLabels" :key="val" @click="form.priority = Number(val)"
                        class="flex-1 py-2.5 rounded-lg text-sm font-semibold transition"
                        :style="form.priority === Number(val) ? { background: val === 2 ? '#ef4444' : val === 1 ? '#f97316' : '#6b7280', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
                  {{ label }}
                </button>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۵- هدف کلان</label>
              <select v-model="form.goal_id" @change="onGoalChange" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option :value="null">بدون هدف</option>
                <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۵- زیرهدف</label>
              <select v-model="form.sub_goal_id" :disabled="!form.goal_id" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)', opacity: form.goal_id ? 1 : 0.5 }">
                <option :value="null">بدون زیرهدف</option>
                <option v-for="sg in subGoals" :key="sg.id" :value="sg.id">{{ sg.title }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۷- وضعیت</label>
              <select v-model="form.status" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option v-for="(label, key) in statusLabels" :key="key" :value="key">{{ label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۶- تاریخ آخرین اقدام</label>
              <input v-model="form.last_action_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
          </div>

          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۸- دوره تکرار</label>
            <div class="grid grid-cols-3 gap-2">
              <select v-model="form.recurrence_type" class="px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option value="none">بدون تکرار</option>
                <option value="daily">روزانه</option>
                <option value="weekly">هفتگی</option>
                <option value="monthly">ماهانه</option>
                <option value="yearly">سالیانه</option>
              </select>
              <div v-if="form.recurrence_type !== 'none'">
                <label class="block text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">هر چند؟</label>
                <input v-model.number="form.recurrence_interval" type="number" min="1" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
              </div>
              <div v-if="form.recurrence_type !== 'none'">
                <label class="block text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">پایان تکرار</label>
                <input v-model="form.recurrence_end_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="saveTask" :disabled="isLoading" class="flex-1 py-3 rounded-xl text-white font-semibold transition disabled:opacity-50" :style="{ background: 'var(--accent)' }">
            {{ editingTask ? 'بروزرسانی' : 'ایجاد تسک' }}
          </button>
          <button @click="showForm = false" class="px-6 py-3 rounded-xl transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>

  </div>
</template>