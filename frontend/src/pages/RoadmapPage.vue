<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, X, Target, BarChart3, ChevronDown, 
  ChevronUp, Calendar, ListTodo, Activity, CheckCircle2, Flag, AlertCircle
} from 'lucide-vue-next'
import api from '@/services/api'
import TaskFormModal from '@/components/TaskFormModal.vue'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()

// --- State Management ---
const goals = ref([])
const categories = ref([])
const selectedGoalId = ref(null)
const subGoals = ref([])
const kpis = ref([])
const expandedSubGoals = ref({})
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
  try { const res = await api.get('/goals'); goals.value = res.data } catch (e) {}
}

const fetchSubGoals = async () => {
  if (!selectedGoalId.value) return
  try {
    const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/subgoals`)
    // هماهنگی داده‌ها از منابع مختلف
    subGoals.value = res.data.map(sg => ({
      ...sg,
      tasks: sg.tasks || sg.sub_goal_tasks || sg.linked_tasks || []
    }))
    res.data.forEach(sg => { if (expandedSubGoals.value[sg.id] === undefined) expandedSubGoals.value[sg.id] = true })
  } catch (e) {}
}

const fetchKPIs = async () => {
  if (!selectedGoalId.value) return
  try { const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/kpis`); kpis.value = res.data } catch (e) {}
}

const selectGoal = (id) => { selectedGoalId.value = id; fetchSubGoals(); fetchKPIs() }
import { useRouter } from 'vue-router'
const router = useRouter()

// تابع جهش مستقیم به صفحه تسک‌ها همراه با فیلتر هوشمند این گام
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
    // پاکسازی تاریخ از فرمت ISO طولانی
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
  // کپی کردن تمام ۱۱ فیلد برای ویرایش کامل
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
  try { await api.delete(`/roadmap/subgoals/${id}`); await fetchSubGoals(); showToast('🗑️ گام حذف شد') } catch (e) {}
}

const subGoalProgress = (sg) => {
  if (!sg.tasks || sg.tasks.length === 0) return 0
  return Math.round((sg.tasks.filter(t => t.is_completed).length / sg.tasks.length) * 100)
}

onMounted(() => { 
  fetchGoals()
  api.get('/tasks/categories').then(res => categories.value = res.data)
})
onMounted(() => {
  fetchGoals().then(() => {
    // اگر از صفحه اهداف روی دکمه جهش کلیک شده بود، آن هدف را خودکار باز کن
    const savedGoalId = sessionStorage.getItem('active_goal_id')
    if (savedGoalId) {
      selectGoal(Number(savedGoalId))
      sessionStorage.removeItem('active_goal_id') // پاکسازی حافظه موقت
    }
  })
  api.get('/tasks/categories').then(res => categories.value = res.data)
})
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen text-right" dir="rtl">
    
    <!-- Toast -->
    <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
      <div class="animate-in slide-in-from-right duration-500">
        <h1 class="text-5xl font-black mb-3" :style="{ color: 'var(--text-primary)' }">نقشه راه</h1>
        <p class="opacity-70 text-xl" :style="{ color: 'var(--text-secondary)' }">مسیر هوشمند رسیدن به اهداف</p>
      </div>
      <button v-if="selectedGoalId" @click="showSubGoalForm = true; editingSubGoal = null" class="px-8 py-4 rounded-[1.5rem] text-white font-black text-lg transition shadow-xl hover:scale-105 active:scale-95 shadow-blue-500/20" :style="{ background: 'var(--accent)' }">
        <Plus class="w-6 h-6 inline-block ml-2" /> تعریف گام جدید
      </button>
    </div>

    <!-- Goal Selection Grid -->
    <div class="mb-12">
      <label class="text-xs font-bold mb-4 block opacity-50 uppercase tracking-widest">انتخاب هدف فعال شما</label>
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
      <section class="rounded-[2.5rem] p-10 border-2 shadow-sm" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-black flex items-center gap-3"><Activity class="w-8 h-8 text-blue-500" /> شاخص‌های کلیدی (KPI)</h2>
        </div>
        <div v-if="kpis.length === 0" class="text-center py-10 opacity-30">شاخصی تعریف نشده است.</div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="kpi in kpis" :key="kpi.id" class="p-6 rounded-3xl border-2" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }">
            <p class="text-sm font-bold opacity-60 mb-4">{{ kpi.title }}</p>
            <div class="flex items-baseline gap-2 mb-4">
              <span class="text-4xl font-black">{{ kpi.current_value }}</span>
              <span class="text-sm opacity-40">از {{ kpi.target_value }} {{ kpi.unit }}</span>
            </div>
            <div class="w-full h-2.5 rounded-full bg-black/10 overflow-hidden">
              <div class="h-full bg-blue-500 transition-all duration-1000 shadow-[0_0_10px_rgba(59,130,246,0.5)]" :style="{ width: (kpi.current_value/kpi.target_value*100) + '%' }"></div>
            </div>
          </div>
        </div>
      </section>
      <!-- Steps & Tasks List Section -->
      <section class="space-y-8">
        <h2 class="text-2xl font-black px-4 flex items-center gap-3"><ListTodo class="w-8 h-8 text-purple-500" /> نقشه‌ی اجرایی گام‌ها</h2>
        <div v-for="sg in subGoals" :key="sg.id" class="rounded-[3rem] border-2 overflow-hidden shadow-md transition-all hover:shadow-xl" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
          
          <!-- SubGoal Card Header -->
          <div class="p-8 flex flex-wrap items-center justify-between gap-6 cursor-pointer hover:bg-white/[0.01]" @click="expandedSubGoals[sg.id] = !expandedSubGoals[sg.id]">
            <div class="flex items-center gap-6 flex-1">
              <div class="w-14 h-14 rounded-[1.2rem] flex items-center justify-center transition-transform border-2" :class="expandedSubGoals[sg.id] ? '' : '-rotate-90'" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }">
                <ChevronDown class="w-8 h-8" />
              </div>
              <div>
                <h3 class="text-2xl font-black" :style="{ color: 'var(--text-primary)' }">{{ sg.title }}</h3>
                <p class="text-base opacity-50 mt-1" :style="{ color: 'var(--text-secondary)' }">{{ sg.description || 'بدون توضیح' }}</p>
              </div>
            </div>
            <div class="flex items-center gap-8">
               <div class="flex items-center gap-4">
                 <div class="w-32 h-2.5 rounded-full bg-black/10 shadow-inner">
                    <div class="h-full rounded-full transition-all duration-700" :style="{ width: subGoalProgress(sg) + '%', background: 'var(--accent)' }"></div>
                 </div>
                 <span class="text-xl font-black" :style="{ color: 'var(--accent)' }">{{ subGoalProgress(sg) }}%</span>
                 <button @click.stop="goToTasks(sg.id, selectedGoalId)" 
        class="px-3.5 py-1.5 rounded-xl font-bold text-xs text-white transition flex items-center gap-1.5 shadow-md hover:scale-105 active:scale-95 bg-gradient-to-r from-purple-600 to-indigo-600">
  <span>تسک‌های این گام در اتاق عملیات</span>
  <span>➔</span>
</button>
               </div>
               <div class="flex gap-2" @click.stop>
                 <button @click="editingSubGoal = sg; subGoalForm = {...sg}; showSubGoalForm = true" class="p-3 hover:bg-white/10 rounded-xl transition"><Edit3 class="w-6 h-6" /></button>
                 <button @click="deleteSubGoal(sg.id)" class="p-3 text-red-500 hover:bg-red-500/10 rounded-xl transition"><Trash2 class="w-6 h-6" /></button>
               </div>
            </div>
          </div>

          <!-- Tasks Area Inside Step -->
          <div v-if="expandedSubGoals[sg.id]" class="p-8 pt-0 border-t-2" :style="{ borderColor: 'var(--border)' }">
            <div class="space-y-5 mt-8">
              <div v-for="task in sg.tasks" :key="task.id" class="group relative p-7 rounded-[2rem] border-2 transition-all duration-300 shadow-sm" :style="{ background: task.is_completed ? 'var(--bg-hover)' : 'var(--bg-primary)', borderColor: 'var(--border)' }">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-8">
                  <div class="flex items-start gap-6 flex-1">
                    <!-- Toggle Success -->
                    <button @click="toggleTask(task)" class="w-12 h-12 rounded-[1rem] border-2 flex items-center justify-center transition-all mt-1" :style="{ background: task.is_completed ? 'var(--accent)' : 'transparent', borderColor: task.is_completed ? 'var(--accent)' : 'var(--border)' }">
                      <Check v-if="task.is_completed" class="w-7 h-7 text-white" />
                    </button>
                    <div class="flex-1">
                      <div class="flex items-center gap-5 mb-2">
                        <p class="font-black text-3xl" :class="task.is_completed ? 'line-through opacity-40' : ''" :style="{ color: 'var(--text-primary)' }">{{ task.title }}</p>
                        <span v-if="task.priority > 0" class="text-xs font-black px-4 py-1.5 rounded-full text-white" :style="{ background: task.priority === 2 ? '#ef4444' : '#eab308' }">{{ task.priority === 2 ? 'فوری' : 'مهم' }}</span>
                      </div>
                      <!-- Description with vertical line -->
                      <p v-if="task.description" @click="task.description.length > 100 ? openFullDesc(task.description) : null" class="text-lg opacity-80 mb-5 cursor-pointer leading-loose border-r-4 pr-5 transition-all hover:opacity-100" :style="{ color: 'var(--text-secondary)', borderColor: 'var(--accent)', background: 'rgba(255,255,255,0.02)' }">
                        {{ task.description.length > 100 ? task.description.substring(0, 100) + '...' : task.description }}
                      </p>
                      <!-- Dates with labels -->
                      <div class="flex flex-wrap gap-10 mt-4">
                        <span v-if="task.due_date" class="text-base flex items-center gap-2 opacity-70"><Calendar class="w-5 h-5" /> <b>مهلت:</b> {{ formatDate(task.due_date) }}</span>
                        <span v-if="task.last_action_date" class="text-base flex items-center gap-2 font-black" :class="task.is_completed ? 'text-green-500' : 'text-blue-400'">
                          <Activity v-if="!task.is_completed" class="w-6 h-6" /> <CheckCircle2 v-else class="w-6 h-6" />
                          {{ task.is_completed ? 'تکمیل شده در:' : 'آخرین اقدام:' }} {{ formatDate(task.last_action_date) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <!-- Edit/Delete Actions -->
                  <div class="flex gap-4 md:opacity-0 group-hover:opacity-100 transition-all duration-300">
                    <button @click="openEditTask(task)" class="p-4 rounded-2xl border-2 bg-white/5 hover:bg-white/10 transition shadow-sm"><Edit3 class="w-7 h-7" /></button>
                    <button @click="api.delete(isMainTask(task) ? `/tasks/${task.id}` : `/roadmap/tasks/${task.id}`).then(fetchSubGoals)" class="p-4 rounded-2xl border-2 border-red-500/40 bg-red-500/5 text-red-500 hover:bg-red-500/10 transition shadow-sm"><Trash2 class="w-7 h-7" /></button>
                  </div>
                </div>
              </div>
              <!-- Guidance for adding tasks -->
              <div class="text-center py-8 border-2 border-dashed rounded-[2rem] opacity-30 text-lg font-bold border-white/20">تسک جدید را در صفحه تسک‌ها به این گام متصل کنید</div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Modals Section -->
    <div v-if="showFullDesc" class="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-black/85 backdrop-blur-md" @click="showFullDesc = false">
      <div class="w-full max-w-2xl rounded-[3rem] p-12 bg-gray-900 border-2 border-white/10 shadow-2xl shadow-black/50" @click.stop>
        <div class="flex justify-between items-center mb-8 text-white"><h3 class="text-3xl font-black">توضیحات کامل</h3><button @click="showFullDesc = false" class="p-2"><X class="w-10 h-10" /></button></div>
        <div class="text-2xl text-gray-200 leading-loose max-h-[50vh] overflow-y-auto text-justify pl-4 custom-scrollbar">{{ currentDescText }}</div>
        <button @click="showFullDesc = false" class="w-full mt-10 py-5 rounded-[1.5rem] bg-blue-600 text-white font-black text-xl hover:bg-blue-500 transition shadow-lg shadow-blue-500/30">بستن</button>
      </div>
    </div>

    <div v-if="showSubGoalForm" class="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md" @click.self="showSubGoalForm = false">
      <div class="w-full max-w-xl rounded-[3rem] p-12 bg-gray-800 border-2 border-white/5 shadow-2xl shadow-black" @click.stop>
        <h3 class="text-3xl font-black mb-8 text-white">تعریف گام عملیاتی جدید</h3>
        <div class="space-y-6">
          <input v-model="subGoalForm.title" placeholder="عنوان گام..." class="w-full p-5 rounded-2xl bg-gray-700 text-white border-2 border-transparent focus:border-blue-500 outline-none transition text-lg" />
          <textarea v-model="subGoalForm.description" placeholder="توضیحات مختصر..." class="w-full p-5 rounded-2xl bg-gray-700 text-white border-2 border-transparent focus:border-blue-500 outline-none h-32 text-lg"></textarea>
          <div class="grid grid-cols-2 gap-4">
             <div><label class="text-xs font-bold opacity-40 mb-2 block">تاریخ شروع</label><DateInputPersian v-model="subGoalForm.start_date" /></div>
             <div><label class="text-xs font-bold opacity-40 mb-2 block">تاریخ پایان</label><DateInputPersian v-model="subGoalForm.target_date" /></div>
          </div>
        </div>
        <div class="flex gap-5 mt-10">
          <button @click="saveSubGoal" class="flex-1 py-5 bg-blue-600 text-white font-black text-xl rounded-[1.5rem] hover:bg-blue-500 transition shadow-xl shadow-blue-500/20">ذخیره گام</button>
          <button @click="showSubGoalForm = false" class="px-10 py-5 bg-gray-600 text-white font-bold rounded-[1.5rem] hover:bg-gray-500 transition">لغو</button>
        </div>
      </div>
    </div>

    <!-- Task Modal Connector -->
    <TaskFormModal v-model="showTaskModal" :form="taskForm" :categories="categories" :goals="goals" :sub-goals="subGoals" :editing-task="editingTask" :is-loading="isLoading" @save="saveTask" />

  </div>
</template>

<style scoped>
.animate-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
</style>
      
