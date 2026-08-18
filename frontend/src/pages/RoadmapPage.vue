<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, X, Target, BarChart3, ChevronDown, 
  ChevronUp, Calendar, ListTodo, Activity, CheckCircle2, Flag, AlertCircle,
  Eye, ArrowRight, Sparkles, BookOpen, Info
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
      tasks: sg.tasks || sg.sub_goal_tasks || sg.linked_tasks || []
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
  sessionStorage.setItem('active_goal_id', goalId)
  sessionStorage.setItem('active_sub_goal_id', subGoalId)
  router.push('/tasks')
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
    showToast('✅ تغییرات تسک با موفقیت ذخیره شد')
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
  <div class="p-6 md:p-10 max-w-7xl mx-auto relative min-h-screen text-right" dir="rtl">
    
    <!-- Toast -->
    <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
      <div class="animate-in slide-in-from-right duration-500">
        <h1 class="text-4xl md:text-5xl font-black mb-3 text-white flex items-center gap-3">
          <Activity class="w-10 h-10 text-purple-400" /> نقشه راه
        </h1>
        <p class="opacity-70 text-lg md:text-xl" :style="{ color: 'var(--text-secondary)' }">مسیر هوشمند و دو ستونه رسیدن به اهداف</p>
      </div>

      <div v-if="selectedGoalId" class="flex items-center gap-3">
        <button @click="openNewKPIForm" class="px-6 py-4 rounded-2xl text-white font-bold text-sm bg-white/10 hover:bg-white/20 transition shadow-lg border border-white/10">
          <Plus class="w-5 h-5 inline-block ml-1 text-blue-400" /> افزودن KPI
        </button>

        <button @click="openNewSubGoalForm" class="px-8 py-4 rounded-2xl text-white font-black text-base md:text-lg transition shadow-xl hover:scale-105 active:scale-95 shadow-purple-500/20 bg-gradient-to-r from-purple-600 to-indigo-600">
          <Plus class="w-6 h-6 inline-block ml-2" /> تعریف گام جدید
        </button>
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
        <button v-for="goal in goals" :key="goal.id" @click="selectGoal(goal.id)" 
                class="p-5 rounded-2xl transition-all border-2 font-black text-sm text-center"
                :style="selectedGoalId === goal.id ? { background: 'var(--accent)', borderColor: 'var(--accent)', color: '#fff', boxShadow: '0 12px 30px -5px var(--accent)' } : { background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
          {{ goal.title }}
        </button>
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

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="sg in subGoals" :key="sg.id" 
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
                <span>تمرکز و تسک‌ها</span>
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
              <ListTodo class="w-5 h-5 text-purple-400" /> تسک‌های مربوط به این گام
            </h4>
            <button @click="goToTasks(selectedSubGoal.id, selectedGoalId)" class="text-xs text-purple-400 hover:underline font-bold">
              مدیریت پیشرفته در اتاق عملیات ➔
            </button>
          </div>

          <div v-if="!selectedSubGoal.tasks || selectedSubGoal.tasks.length === 0" class="text-center py-8 rounded-2xl bg-white/5 border border-white/10 opacity-60">
            هیچ تسکی برای این گام ثبت نشده است.
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
            <span>انتقال تسک‌ها به اتاق عملیات</span>
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

  </div>
</template>

<style scoped>
.animate-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
</style>