<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, X, Target, BarChart3, ChevronDown, 
  ChevronUp, Calendar, ListTodo, Activity, CheckCircle2 
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

// --- Modals State ---
const showTaskModal = ref(false)
const showSubGoalForm = ref(false)
const showKPIForm = ref(false)
const showFullDesc = ref(false)
const currentDescText = ref('')

// --- Forms State ---
const editingSubGoal = ref(null)
const editingKPI = ref(null)
const editingTaskId = ref(null)
const subGoalForm = ref({ title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 })
const kpiForm = ref({ title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' })
const editingTaskForm = ref({ title: '', description: '', priority: 0, due_date: '', is_completed: false, last_action_date: '', _isMain: false })
const taskForm = ref({ 
  title: '', description: '', 
  register_date: new Date().toISOString().split('T')[0], 
  duration_days: null, category: '', 
  sub_goal_id: null, goal_id: null, 
  last_action_date: '', status: 'not_started', 
  recurrence_type: 'none', recurrence_interval: 1, 
  recurrence_end_date: '', priority: 0 
})

// --- Functions ---
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
    subGoals.value = res.data.map(sg => ({
      ...sg,
      tasks: sg.tasks || sg.linked_tasks || []
    }))
    res.data.forEach(sg => { if (expandedSubGoals.value[sg.id] === undefined) expandedSubGoals.value[sg.id] = true })
  } catch (e) {}
}

const fetchKPIs = async () => {
  if (!selectedGoalId.value) return
  try { const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/kpis`); kpis.value = res.data } catch (e) {}
}

const selectGoal = (id) => { selectedGoalId.value = id; fetchSubGoals(); fetchKPIs() }
const isMainTask = (task) => task.source === 'main_task' || (task.source === undefined && task.sub_goal_task_id === undefined)

const toggleTask = async (task) => {
  try {
    const newStatus = !task.is_completed
    const today = new Date().toISOString().split('T')[0]
    const payload = { 
      title: task.title,
      is_completed: newStatus,
      last_action_date: newStatus ? today : (task.last_action_date || today),
      priority: task.priority || 0,
      due_date: task.due_date,
      description: task.description
    }
    if (isMainTask(task)) {
      await api.put(`/tasks/${task.id}`, { ...payload, status: newStatus ? 'completed' : 'in_progress' })
    } else {
      await api.put(`/roadmap/tasks/${task.id}`, payload)
    }
    await fetchSubGoals()
  } catch (e) { showToast('❌ خطا در بروزرسانی', 'error') }
}

const startEditTask = (task) => {
  editingTaskId.value = task.id
  editingTaskForm.value = {
    title: task.title,
    description: task.description || '',
    priority: task.priority ?? 0,
    due_date: task.due_date || '',
    is_completed: !!task.is_completed,
    last_action_date: task.last_action_date || '',
    _isMain: isMainTask(task)
  }
}

const saveTaskEdit = async (taskId) => {
  try {
    const today = new Date().toISOString().split('T')[0]
    if (editingTaskForm.value.is_completed && !editingTaskForm.value.last_action_date) {
      editingTaskForm.value.last_action_date = today
    }
    const payload = { ...editingTaskForm.value }
    if (payload.last_action_date && payload.last_action_date.includes('T')) {
      payload.last_action_date = payload.last_action_date.split('T')[0]
    }
    if (payload._isMain) {
      await api.put(`/tasks/${taskId}`, { ...payload, status: payload.is_completed ? 'completed' : 'in_progress' })
    } else {
      await api.put(`/roadmap/tasks/${taskId}`, payload)
    }
    editingTaskId.value = null; await fetchSubGoals(); showToast('✅ تغییرات اعمال شد')
  } catch (e) { showToast('❌ خطا', 'error') }
}

const saveSubGoal = async () => {
  if (!subGoalForm.value.title.trim()) return
  try {
    if (editingSubGoal.value) await api.put(`/roadmap/subgoals/${editingSubGoal.value.id}`, subGoalForm.value)
    else await api.post(`/roadmap/goal/${selectedGoalId.value}/subgoals`, subGoalForm.value)
    showSubGoalForm.value = false; await fetchSubGoals(); showToast('✅ گام ذخیره شد')
  } catch (e) { showToast('❌ خطا', 'error') }
}

const saveKPI = async () => {
  if (!kpiForm.value.title.trim()) return
  try {
    if (editingKPI.value) await api.put(`/roadmap/kpis/${editingKPI.value.id}`, kpiForm.value)
    else await api.post(`/roadmap/goal/${selectedGoalId.value}/kpis`, kpiForm.value)
    showKPIForm.value = false; await fetchKPIs(); showToast('✅ شاخص ثبت شد')
  } catch (e) {}
}

const subGoalProgress = (sg) => {
  if (!sg.tasks || sg.tasks.length === 0) return 0
  return Math.round((sg.tasks.filter(t => t.is_completed).length / sg.tasks.length) * 100)
}

const deleteSubGoal = async (id) => {
  if (!confirm('حذف این گام؟')) return
  try { await api.delete(`/roadmap/subgoals/${id}`); await fetchSubGoals() } catch (e) {}
}

onMounted(() => { fetchGoals(); api.get('/tasks/categories').then(res => categories.value = res.data) })
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen text-right" dir="rtl">
    <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
      <div>
        <h1 class="text-4xl font-black mb-2" :style="{ color: 'var(--text-primary)' }">نقشه راه</h1>
        <p class="opacity-70 text-lg" :style="{ color: 'var(--text-secondary)' }">شکستن اهداف بزرگ به قدم‌های کوچک</p>
      </div>
      <button v-if="selectedGoalId" @click="showSubGoalForm = true; editingSubGoal = null" class="px-6 py-3 rounded-xl text-white font-bold transition shadow-lg hover:scale-105" :style="{ background: 'var(--accent)' }"><Plus class="w-5 h-5 inline-block ml-1" /> گام جدید</button>
    </div>

    <div class="mb-10">
      <label class="text-xs font-bold mb-3 block opacity-50 tracking-widest">انتخاب هدف فعال</label>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
        <button v-for="goal in goals" :key="goal.id" @click="selectGoal(goal.id)" class="p-4 rounded-2xl transition-all border font-bold" :style="selectedGoalId === goal.id ? { background: 'var(--accent)', borderColor: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">{{ goal.title }}</button>
      </div>
    </div>

    <div v-if="selectedGoalId" class="space-y-10">
      <section class="rounded-3xl p-8 border shadow-sm" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-xl font-black flex items-center gap-3"><Activity class="w-6 h-6 text-blue-500" /> شاخص‌های عملکرد (KPI)</h2>
          <button @click="showKPIForm = true; editingKPI = null" class="text-sm font-bold underline" :style="{ color: 'var(--accent)' }">افزودن</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="kpi in kpis" :key="kpi.id" class="p-5 rounded-2xl border" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }">
            <div class="flex justify-between mb-2"><span class="text-xs font-bold opacity-60">{{ kpi.title }}</span>
              <div class="flex gap-2">
                <button @click="editingKPI = kpi; kpiForm = {...kpi}; showKPIForm = true" class="p-1 hover:text-blue-400"><Edit3 class="w-4 h-4" /></button>
                <button @click="api.delete(`/roadmap/kpis/${kpi.id}`).then(fetchKPIs)" class="p-1 hover:text-red-500"><Trash2 class="w-4 h-4" /></button>
              </div>
            </div>
            <div class="flex items-baseline gap-2 mb-3"><span class="text-3xl font-black">{{ kpi.current_value }}</span><span class="text-xs opacity-50">/ {{ kpi.target_value }} {{ kpi.unit }}</span></div>
            <div class="w-full h-1.5 rounded-full bg-black/10 overflow-hidden"><div class="h-full bg-blue-500 transition-all duration-1000" :style="{ width: (kpi.current_value/kpi.target_value*100) + '%' }"></div></div>
          </div>
        </div>
      </section>

      <section class="space-y-6">
        <h2 class="text-xl font-black px-2 flex items-center gap-3"><ListTodo class="w-6 h-6 text-purple-500" /> نقشه گام‌ها</h2>
        <div v-for="sg in subGoals" :key="sg.id" class="rounded-[2rem] border overflow-hidden shadow-sm" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
          <div class="p-6 flex flex-wrap items-center justify-between gap-4 cursor-pointer hover:bg-white/[0.01]" @click="expandedSubGoals[sg.id] = !expandedSubGoals[sg.id]">
            <div class="flex items-center gap-4 flex-1"><ChevronDown class="w-6 h-6 transition-transform" :class="expandedSubGoals[sg.id] ? '' : '-rotate-90'" /><h3 class="text-lg font-black">{{ sg.title }}</h3></div>
            <div class="flex items-center gap-6">
               <span class="text-sm font-black" :style="{ color: 'var(--accent)' }">{{ subGoalProgress(sg) }}%</span>
               <div class="flex gap-1" @click.stop>
                 <button @click="editingSubGoal = sg; subGoalForm = {...sg}; showSubGoalForm = true" class="p-2 hover:bg-white/10 rounded-lg"><Edit3 class="w-5 h-5" /></button>
                 <button @click="deleteSubGoal(sg.id)" class="p-2 hover:bg-red-500/10 text-red-500 rounded-lg"><Trash2 class="w-5 h-5" /></button>
               </div>
            </div>
          </div>
          <div v-if="expandedSubGoals[sg.id]" class="p-6 pt-0 border-t" :style="{ borderColor: 'var(--border)' }">
            <div class="space-y-4 mt-6">
              <div v-for="task in sg.tasks" :key="task.id" 
                   class="p-4 rounded-xl border border-white/5 mb-3" 
                   :style="{ background: 'var(--bg-primary)' }">
                <div class="flex items-start gap-4">
                  <!-- وضعیت تسک -->
                  <button @click="toggleTask(task)" 
                          class="w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 mt-1 transition-all" 
                          :style="{ borderColor: task.is_completed ? '#22c55e' : 'var(--border)', background: task.is_completed ? '#22c55e' : 'transparent' }">
                    <Check v-if="task.is_completed" class="w-4 h-4 text-white" />
                  </button>

                  <div class="flex-1">
                    <p class="font-bold text-lg" :class="task.is_completed ? 'line-through opacity-40' : ''">
                      {{ task.title }}
                    </p>
                    
                    <!-- نمایش توضیحات -->
                    <p v-if="task.description" 
                       @click="task.description.length > 80 ? openFullDesc(task.description) : null"
                       class="text-sm opacity-60 mt-1 border-r-2 pr-2 border-blue-500/30 cursor-pointer hover:opacity-100 transition-all">
                      {{ task.description.length > 80 ? task.description.substring(0, 80) + '...' : task.description }}
                    </p>

                    <!-- تاریخ‌ها -->
                    <div class="flex gap-4 mt-2 text-[11px] font-bold opacity-50 uppercase">
                      <span v-if="task.due_date">📅 مهلت: {{ formatDate(task.due_date) }}</span>
                      <span v-if="task.last_action_date" :class="task.is_completed ? 'text-green-500 font-bold' : ''">
                        ⏱ {{ task.is_completed ? 'تکمیل شده:' : 'اقدام:' }} {{ formatDate(task.last_action_date) }}
                      </span>
                    </div>
                  </div>

                  <!-- دکمه حذف -->
                  <button @click="api.delete(isMainTask(task) ? `/tasks/${task.id}` : `/roadmap/tasks/${task.id}`).then(fetchSubGoals)" 
                          class="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-all">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Modals -->
    <div v-if="showFullDesc" class="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click="showFullDesc = false">
      <div class="w-full max-w-2xl rounded-[2.5rem] p-10 shadow-2xl" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }" @click.stop>
        <div class="flex justify-between items-center mb-6"><h3 class="text-2xl font-black">توضیحات کامل</h3><button @click="showFullDesc = false"><X class="w-8 h-8" /></button></div>
        <div class="text-xl leading-loose opacity-90 overflow-y-auto max-h-[50vh] p-4 text-justify">{{ currentDescText }}</div>
        <button @click="showFullDesc = false" class="w-full mt-8 py-4 rounded-2xl font-black text-white" :style="{ background: 'var(--accent)' }">بستن</button>
      </div>
    </div>

    <div v-if="showSubGoalForm" class="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md" @click.self="showSubGoalForm = false">
      <div class="w-full max-w-lg rounded-[2.5rem] p-8 shadow-2xl" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <h3 class="text-2xl font-black mb-6">{{ editingSubGoal ? 'ویرایش گام' : 'گام جدید' }}</h3>
        <input v-model="subGoalForm.title" placeholder="عنوان" class="w-full px-5 py-4 rounded-xl border mb-4 outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }" />
        <textarea v-model="subGoalForm.description" placeholder="توضیح..." class="w-full px-5 py-4 rounded-xl border mb-4 outline-none h-24" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }"></textarea>
        <div class="grid grid-cols-2 gap-3 mb-6">
           <DateInputPersian v-model="subGoalForm.start_date" placeholder="شروع" />
           <DateInputPersian v-model="subGoalForm.target_date" placeholder="پایان" />
        </div>
        <div class="flex gap-3"><button @click="saveSubGoal" class="flex-1 py-4 rounded-xl text-white font-bold" :style="{ background: 'var(--accent)' }">ذخیره</button></div>
      </div>
    </div>

    <div v-if="showKPIForm" class="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md" @click.self="showKPIForm = false">
       <div class="w-full max-w-md rounded-[2.5rem] p-10 shadow-2xl" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
         <h3 class="text-2xl font-black mb-8">{{ editingKPI ? 'ویرایش شاخص' : 'شاخص جدید' }}</h3>
         <input v-model="kpiForm.title" placeholder="عنوان شاخص" class="w-full px-5 py-4 rounded-2xl border mb-4 outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }" />
         <div class="grid grid-cols-2 gap-4 mb-4">
           <select v-model="kpiForm.unit" class="px-5 py-4 rounded-2xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }"><option value="عدد">عدد</option><option value="درصد">درصد</option></select>
           <select v-model="kpiForm.frequency" class="px-5 py-4 rounded-2xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }"><option value="monthly">ماهانه</option><option value="daily">روزانه</option></select>
         </div>
         <div class="grid grid-cols-2 gap-4 mb-8">
           <input v-model.number="kpiForm.target_value" type="number" placeholder="هدف" class="px-5 py-4 rounded-2xl border text-center font-bold" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }" />
           <input v-model.number="kpiForm.current_value" type="number" placeholder="فعلی" class="px-5 py-4 rounded-2xl border text-center font-bold" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }" />
         </div>
         <div class="flex gap-4"><button @click="saveKPI" class="flex-1 py-4 rounded-2xl text-white font-bold shadow-lg" :style="{ background: 'var(--accent)' }">ذخیره</button></div>
       </div>
    </div>
  </div>
</template>

<style scoped>
.animate-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>