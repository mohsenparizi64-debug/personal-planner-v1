<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, Filter, Search, List } from 'lucide-vue-next'
import api from '@/services/api'
import TaskFormModal from '@/components/TaskFormModal.vue'

const themeStore = useThemeStore()
const tasks = ref([])
const goals = ref([])
const subGoals = ref([])
const categories = ref([])
const showTaskModal = ref(false)
const editingTask = ref(null)
const isLoading = ref(false)
const message = ref('')
const messageType = ref('success')
const validationErrors = ref({})

const showAllTasks = ref(true)
const showFilters = ref(true)
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
  priority: 0
})

const statusLabels = { 'not_started': 'شروع نشده', 'in_progress': 'در حال انجام', 'completed': 'تکمیل', 'on_hold': 'متوقف', 'cancelled': 'لغو شده' }
const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'اضطراری' }

const showToast = (msg, type = 'success') => { message.value = msg; messageType.value = type; setTimeout(() => message.value = '', 3000) }

const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
    showToast('⚠️ خطا در بارگذاری تسک‌ها', 'error')
  }
}
const fetchGoals = async () => { try { const res = await api.get('/goals'); goals.value = res.data } catch (e) {} }
const fetchSubGoals = async (goalId) => { if (!goalId) { subGoals.value = []; return }; try { const res = await api.get(`/roadmap/goal/${goalId}/subgoals`); subGoals.value = res.data } catch (e) {} }
const fetchCategories = async () => { try { const res = await api.get('/tasks/categories'); categories.value = res.data } catch (e) {} }

// ====== اعمال تمام فیلترها روی کلاینت ======
const filteredTasks = computed(() => {
  let result = tasks.value

  if (filterSearch.value.trim()) {
    const q = filterSearch.value.toLowerCase()
    result = result.filter(t =>
      (t.title && t.title.toLowerCase().includes(q)) ||
      (t.description && t.description.toLowerCase().includes(q))
    )
  }
  if (filterCategory.value) {
    result = result.filter(t => t.category === filterCategory.value)
  }
  if (filterStatus.value) {
    result = result.filter(t => t.status === filterStatus.value)
  }
  if (filterPriority.value !== null && filterPriority.value !== '') {
    result = result.filter(t => t.priority === Number(filterPriority.value))
  }
  if (filterGoalId.value) {
    result = result.filter(t => t.goal_id === filterGoalId.value)
  }
  if (filterDueDateFrom.value) result = result.filter(t => t.due_date && t.due_date >= filterDueDateFrom.value)
  if (filterDueDateTo.value) result = result.filter(t => t.due_date && t.due_date <= filterDueDateTo.value)
  if (filterRecurrence.value === 'has') result = result.filter(t => t.recurrence_type && t.recurrence_type !== 'none')
  if (filterRecurrence.value === 'none') result = result.filter(t => !t.recurrence_type || t.recurrence_type === 'none')

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
  filterDueDateFrom.value = ''; filterDueDateTo.value = ''
}

const openNewForm = () => {
  form.value = { title: '', description: '', register_date: new Date().toISOString().split('T')[0], duration_days: null, category: '', sub_goal_id: null, goal_id: null, last_action_date: '', status: 'not_started', recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '', priority: 0 }
  editingTask.value = null; subGoals.value = []; validationErrors.value = {}; showTaskModal.value = true
}
const openEditForm = (task) => {
  form.value = { title: task.title, description: task.description || '', register_date: task.register_date || '', duration_days: task.duration_days || null, category: task.category || '', sub_goal_id: task.sub_goal_id || null, goal_id: task.goal_id || null, last_action_date: task.last_action_date || '', status: task.status, recurrence_type: task.recurrence_type || 'none', recurrence_interval: task.recurrence_interval || 1, recurrence_end_date: task.recurrence_end_date || '', priority: task.priority ?? 0 }
  editingTask.value = task; fetchSubGoals(task.goal_id); validationErrors.value = {}; showTaskModal.value = true
}
const onGoalChange = () => { form.value.sub_goal_id = null; fetchSubGoals(form.value.goal_id) }

const validateForm = () => {
  validationErrors.value = {}
  let hasError = false
  if (!form.value.title.trim()) { validationErrors.value.title = 'عنوان تسک الزامی است'; hasError = true }
  if (form.value.duration_days && form.value.duration_days < 0) { validationErrors.value.duration_days = 'مدت زمان نمی‌تواند منفی باشد'; hasError = true }
  if (form.value.recurrence_interval && form.value.recurrence_interval < 1) { validationErrors.value.recurrence_interval = 'دوره تکرار باید حداقل ۱ باشد'; hasError = true }
  return !hasError
}

const saveTask = async () => {
  // ۱. بررسی اعتبار فرم قبل از ارسال
  if (!validateForm()) {
    showToast('⚠️ لطفاً عنوان تسک را وارد کنید', 'error');
    return;
  }

  try {
    isLoading.value = true;
    // ۲. استفاده از نام صحیح متغیر یعنی form به جای taskForm
    const data = { ...form.value }; 
    
    if (editingTask.value) {
      await api.put(`/tasks/${editingTask.value.id}`, data);
      showToast('✅ تسک بروزرسانی شد');
    } else {
      await api.post('/tasks', data);
      showToast('✅ تسک جدید ساخته شد');
    }

    showTaskModal.value = false;
    await fetchTasks(); // رفرش کردن لیست
  } catch (e) {
    console.error(e);
    showToast('❌ خطا در ذخیره تسک', 'error');
  } finally {
    isLoading.value = false;
  }
}
const toggleTask = async (task) => {
  const ns = task.status === 'completed' ? 'not_started' : 'completed'
  await api.put(`/tasks/${task.id}`, { status: ns, is_completed: ns === 'completed' })
  await fetchTasks()
}
const deleteTask = async (id) => { if (!confirm('مطمئنی؟')) return; try { await api.delete(`/tasks/${id}`); showToast('🗑️ تسک حذف شد'); await fetchTasks() } catch (e) {} }

onMounted(() => { fetchTasks(); fetchGoals(); fetchCategories() })
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto relative min-h-screen" :class="themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''">

    <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div><h1 class="text-3xl font-extrabold mb-1" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">تسک‌ها</h1><p :style="{ color: 'var(--text-secondary)' }">{{ filteredTasks.length }} تسک <span v-if="activeFilterCount > 0">({{ activeFilterCount }} فیلتر)</span></p></div>
      <div class="flex gap-2 flex-wrap">
        <button @click="showAllTasks = !showAllTasks" class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm" :style="showAllTasks ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }"><List class="w-4 h-4" /> {{ showAllTasks ? 'فشرده' : 'همه' }}</button>
        <button @click="showFilters = !showFilters" class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm relative" :style="{ background: showFilters ? 'var(--accent)' : 'var(--bg-hover)', color: showFilters ? '#fff' : 'var(--text-secondary)' }"><Filter class="w-4 h-4" /> فیلترها <span v-if="activeFilterCount > 0" class="absolute -top-1 -right-1 w-5 h-5 rounded-full text-white text-xs flex items-center justify-center font-bold" style="background: #ef4444">{{ activeFilterCount }}</span></button>
        <button @click="openNewForm" class="px-5 py-2 rounded-xl text-white font-semibold transition flex items-center gap-2" :style="{ background: 'var(--accent)' }"><Plus class="w-5 h-5" /> تسک جدید</button>
      </div>
    </div>

    <div v-if="showFilters" class="mb-6 p-4 rounded-xl space-y-3" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      <div class="relative"><Search class="absolute right-3 top-2.5 w-5 h-5" :style="{ color: 'var(--text-secondary)' }" /><input v-model="filterSearch" placeholder="جستجو..." class="w-full pr-10 pl-4 py-2.5 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" /></div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
        <select v-model="filterCategory" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"><option value="">همه دسته‌بندی‌ها</option><option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option></select>
        <select v-model="filterStatus" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"><option value="">همه وضعیت‌ها</option><option v-for="(l,k) in statusLabels" :key="k" :value="k">{{ l }}</option></select>
        <select v-model="filterPriority" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"><option :value="null">همه اهمیت‌ها</option><option :value="0">عادی</option><option :value="1">مهم</option><option :value="2">اضطراری</option></select>
        <select v-model="filterGoalId" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"><option :value="null">همه اهداف</option><option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option></select>
      </div>
      <button @click="resetFilters" class="px-3 py-2 rounded-lg text-sm transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">حذف فیلترها</button>
    </div>

    <div v-if="filteredTasks.length === 0" class="text-center py-20"><div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4" :style="{ background: 'var(--bg-hover)' }"><Search class="w-10 h-10" :style="{ color: 'var(--accent)' }" /></div><p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">{{ tasks.length === 0 ? 'هنوز تسکی ثبت نکردی!' : 'تسکی با این فیلترها پیدا نشد' }}</p></div>

    <div v-if="filteredTasks.length > 0" class="space-y-1">
      <div v-for="task in filteredTasks" :key="task.id" class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition" :style="{ background: task.status === 'completed' ? 'var(--bg-primary)' : 'var(--bg-hover)' }">
        <button @click="toggleTask(task)" class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0" :style="{ background: task.status === 'completed' ? 'var(--accent)' : 'transparent', borderColor: task.status === 'completed' ? 'var(--accent)' : 'var(--border)' }"><Check v-if="task.status === 'completed'" class="w-3 h-3 text-white" /></button>
        <span class="flex-1 truncate" :style="{ color: 'var(--text-primary)', textDecoration: task.status === 'completed' ? 'line-through' : 'none' }">{{ task.title }}</span>
        <span v-if="task.priority === 2" class="text-red-400 text-xs">⚡</span>
        <span v-if="task.category" class="text-[10px] px-2 py-0.5 rounded-full" :style="{ background: 'rgba(255,255,255,0.08)', color: 'var(--text-secondary)' }">{{ task.category }}</span>
        <button @click="openEditForm(task)" class="p-1 rounded hover:bg-white/10"><Edit3 class="w-3 h-3" :style="{ color: 'var(--text-secondary)' }" /></button>
        <button @click="deleteTask(task.id)" class="p-1 rounded hover:bg-red-500/10"><Trash2 class="w-3 h-3" :style="{ color: 'var(--text-secondary)' }" /></button>
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