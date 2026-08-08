<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, X, Target, BarChart3, ChevronDown } from 'lucide-vue-next'
import api from '@/services/api'
import TaskFormModal from '@/components/TaskFormModal.vue'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()

const goals = ref([])
const categories = ref([])
const selectedGoalId = ref(null)
const subGoals = ref([])
const kpis = ref([])
const showTaskModal = ref(false)

const showSubGoalForm = ref(false)
const showKPIForm = ref(false)
const editingSubGoal = ref(null)
const editingKPI = ref(null)
const expandedSubGoals = ref({})

const subGoalForm = ref({ title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 })
const kpiForm = ref({ title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' })
const newTaskTitle = ref({})
const editingTaskId = ref(null)
const editingTaskForm = ref({ title: '', priority: 0, due_date: '', is_completed: false, _isMain: false })
const taskForm = ref({ title: '', description: '', register_date: new Date().toISOString().split('T')[0], duration_days: null, category: '', sub_goal_id: null, goal_id: null, last_action_date: '', status: 'not_started', recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '', priority: 0 })
const editingTask = ref(null)
const validationErrors = ref({})
const isLoading = ref(false)
const message = ref('')
const messageType = ref('success')

const showToast = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

const fetchGoals = async () => {
  try { const res = await api.get('/goals'); goals.value = res.data } catch (e) {}
}
const fetchCategories = async () => {
  try { const res = await api.get('/tasks/categories'); categories.value = res.data } catch (e) {}
}

const fetchSubGoals = async () => {
  if (!selectedGoalId.value) return
  try {
    const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/subgoals`)
    subGoals.value = res.data
    const nextExpanded = {}
    res.data.forEach((sg) => { nextExpanded[sg.id] = true })
    expandedSubGoals.value = nextExpanded
  } catch (e) { console.error(e) }
}

const fetchKPIs = async () => {
  if (!selectedGoalId.value) return
  try { const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/kpis`); kpis.value = res.data } catch (e) {}
}

const selectGoal = (id) => { selectedGoalId.value = id; fetchSubGoals(); fetchKPIs() }

const openNewTaskModal = (subGoalId = null) => {
  taskForm.value = { title: '', description: '', register_date: new Date().toISOString().split('T')[0], duration_days: null, category: '', sub_goal_id: subGoalId, goal_id: selectedGoalId.value, last_action_date: '', status: 'not_started', recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '', priority: 0 }
  editingTask.value = null
  validationErrors.value = {}
  showTaskModal.value = true
}

const openEditTaskModal = (task) => {
  taskForm.value = { title: task.title, description: task.description || '', register_date: task.register_date || '', duration_days: task.duration_days || null, category: task.category || '', sub_goal_id: task.sub_goal_id || null, goal_id: task.goal_id || null, last_action_date: task.last_action_date || '', status: task.status, recurrence_type: task.recurrence_type || 'none', recurrence_interval: task.recurrence_interval || 1, recurrence_end_date: task.recurrence_end_date || '', priority: task.priority ?? 0 }
  editingTask.value = task
  validationErrors.value = {}
  showTaskModal.value = true
}

const onGoalChange = () => { taskForm.value.sub_goal_id = null }

const validateForm = () => {
  validationErrors.value = {}
  let hasError = false
  if (!taskForm.value.title.trim()) { validationErrors.value.title = 'عنوان تسک الزامی است'; hasError = true }
  if (taskForm.value.duration_days && taskForm.value.duration_days < 0) { validationErrors.value.duration_days = 'مدت زمان نمی‌تواند منفی باشد'; hasError = true }
  if (taskForm.value.recurrence_interval && taskForm.value.recurrence_interval < 1) { validationErrors.value.recurrence_interval = 'دوره تکرار باید حداقل ۱ باشد'; hasError = true }
  return !hasError
}

const saveTask = async () => {
  if (!validateForm()) return
  isLoading.value = true
  try {
    const data = { ...taskForm.value }
    if (!data.sub_goal_id) data.sub_goal_id = null
    if (!data.goal_id) data.goal_id = null
    if (!data.duration_days) data.duration_days = null
    for (const key of ['register_date', 'last_action_date', 'recurrence_end_date']) {
      if (data[key] === '') data[key] = null
    }
    if (editingTask.value) await api.put(`/tasks/${editingTask.value.id}`, data)
    else await api.post('/tasks', data)
    showTaskModal.value = false
    editingTask.value = null
    await fetchSubGoals()
    showToast('✅ تسک ذخیره شد')
  } catch (e) { showToast('❌ خطا در ذخیره تسک', 'error') } finally { isLoading.value = false }
}

const saveSubGoal = async () => {
  if (!subGoalForm.value.title.trim()) return
  try {
    if (editingSubGoal.value) {
      await api.put(`/roadmap/subgoals/${editingSubGoal.value.id}`, subGoalForm.value)
      showToast('✅ زیرهدف بروزرسانی شد')
    } else {
      await api.post(`/roadmap/goal/${selectedGoalId.value}/subgoals`, subGoalForm.value)
      showToast('✅ زیرهدف جدید ایجاد شد')
    }
    showSubGoalForm.value = false
    resetSubGoalForm()
    await fetchSubGoals()
  } catch (e) { showToast('❌ خطا در ذخیره', 'error') }
}

const deleteSubGoal = async (id) => {
  try { await api.delete(`/roadmap/subgoals/${id}`); showToast('🗑️ زیرهدف حذف شد'); await fetchSubGoals() } catch (e) {}
}

const editSubGoal = (sg) => {
  subGoalForm.value = { title: sg.title, description: sg.description || '', start_date: sg.start_date || '', target_date: sg.target_date || '', status: sg.status, order_index: sg.order_index }
  editingSubGoal.value = sg
  showSubGoalForm.value = true
}

const resetSubGoalForm = () => {
  subGoalForm.value = { title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 }
  editingSubGoal.value = null
}

const toggleExpand = (id) => { expandedSubGoals.value[id] = !expandedSubGoals.value[id] }

const subGoalProgress = (sg) => {
  if (!sg.tasks || sg.tasks.length === 0) return 0
  return Math.round((sg.tasks.filter(t => t.is_completed).length / sg.tasks.length) * 100)
}

// ====== تشخیص نوع تسک: از جدول Task اصلی یا SubGoalTask ======
const isMainTask = (task) => {
  return task.source === 'main_task' || (task.source === undefined && task.sub_goal_task_id === undefined)
}

const toggleTask = async (task) => {
  try {
    if (isMainTask(task)) {
      const ns = task.is_completed ? 'not_started' : 'completed'
      await api.put(`/tasks/${task.id}`, { status: ns, is_completed: !task.is_completed })
    } else {
      await api.put(`/roadmap/tasks/${task.id}`, { is_completed: !task.is_completed })
    }
    await fetchSubGoals()
  } catch (e) { showToast('❌ خطا در تغییر وضعیت تسک', 'error') }
}

const deleteTask = async (task) => {
  if (!confirm('حذف این تسک؟')) return
  try {
    if (isMainTask(task)) {
      await api.delete(`/tasks/${task.id}`)
    } else {
      await api.delete(`/roadmap/tasks/${task.id}`)
    }
    showToast('🗑️ تسک حذف شد')
    await fetchSubGoals()
  } catch (e) { showToast('❌ خطا در حذف تسک', 'error') }
}

const startEditTask = (task) => {
  editingTaskId.value = task.id
  editingTaskForm.value = {
    title: task.title,
    priority: task.priority ?? 0,
    due_date: task.due_date || '',
    is_completed: !!task.is_completed,
    _isMain: isMainTask(task),
  }
}

const cancelEditTask = () => {
  editingTaskId.value = null
  editingTaskForm.value = { title: '', priority: 0, due_date: '', is_completed: false, _isMain: false }
}

const saveTaskEdit = async (taskId) => {
  try {
    const payload = {
      title: editingTaskForm.value.title.trim(),
      priority: Number(editingTaskForm.value.priority),
      due_date: editingTaskForm.value.due_date || null,
      is_completed: editingTaskForm.value.is_completed,
    }
    if (editingTaskForm.value._isMain) {
      await api.put(`/tasks/${taskId}`, {
        ...payload,
        status: payload.is_completed ? 'completed' : 'not_started',
      })
    } else {
      await api.put(`/roadmap/tasks/${taskId}`, payload)
    }
    await fetchSubGoals()
    editingTaskId.value = null
    showToast('✅ تسک بروزرسانی شد')
  } catch (e) { showToast('❌ خطا در بروزرسانی تسک', 'error') }
}

const saveKPI = async () => {
  if (!kpiForm.value.title.trim()) return
  try {
    if (editingKPI.value) {
      await api.put(`/roadmap/kpis/${editingKPI.value.id}`, kpiForm.value)
      showToast('✅ KPI بروزرسانی شد')
    } else {
      await api.post(`/roadmap/goal/${selectedGoalId.value}/kpis`, kpiForm.value)
      showToast('✅ KPI جدید ایجاد شد')
    }
    showKPIForm.value = false
    resetKPIForm()
    await fetchKPIs()
  } catch (e) { showToast('❌ خطا در ذخیره KPI', 'error') }
}

const editKPI = (kpi) => { kpiForm.value = { ...kpi }; editingKPI.value = kpi; showKPIForm.value = true }
const deleteKPI = async (id) => { try { await api.delete(`/roadmap/kpis/${id}`); showToast('🗑️ KPI حذف شد'); await fetchKPIs() } catch (e) {} }
const resetKPIForm = () => { kpiForm.value = { title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' }; editingKPI.value = null }

const kpiPercent = (kpi) => {
  if (!kpi.target_value) return 0
  return Math.min(100, Math.round((kpi.current_value / kpi.target_value) * 100))
}

onMounted(() => { fetchGoals(); fetchCategories() })
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative z-10 min-h-screen" :class="themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''">

    <div v-if="message" class="fixed top-4 left-1/2 transform -translate-x-1/2 z-[100] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <div class="mb-8"><h1 class="text-3xl font-extrabold mb-2" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">نقشه راه</h1><p :style="{ color: 'var(--text-secondary)' }">اهداف کلان → زیرهدف‌ها → تسک‌ها</p></div>

    <div class="mb-8">
      <label class="block text-sm mb-2" :style="{ color: 'var(--text-secondary)' }">🎯 هدف کلان:</label>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <button v-for="goal in goals" :key="goal.id" @click="selectGoal(goal.id)" class="p-4 rounded-xl text-right transition-all duration-200" :style="selectedGoalId === goal.id ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }"><div class="flex items-center gap-2"><Target class="w-4 h-4" /><span class="font-medium">{{ goal.title }}</span></div></button>
      </div>
    </div>

    <div v-if="selectedGoalId" class="space-y-8">

      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4"><h2 class="text-lg font-bold flex items-center gap-2" :style="{ color: 'var(--text-primary)' }"><BarChart3 class="w-5 h-5" :style="{ color: 'var(--accent)' }" /> KPI ها</h2><button @click="showKPIForm = true; resetKPIForm()" class="px-4 py-2 text-sm rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }"><Plus class="w-4 h-4 inline" /> KPI جدید</button></div>
        <div v-if="kpis.length === 0" class="text-center py-4" :style="{ color: 'var(--text-secondary)' }">هنوز KPI تعریف نشده.</div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="kpi in kpis" :key="kpi.id" class="p-4 rounded-xl" :style="{ background: 'var(--bg-hover)' }">
            <div class="flex justify-between items-start mb-2"><h4 class="font-bold text-sm" :style="{ color: 'var(--text-primary)' }">{{ kpi.title }}</h4><div class="flex gap-1"><button @click="editKPI(kpi)" class="p-1 rounded hover:bg-white/10"><Edit3 class="w-3 h-3" :style="{ color: 'var(--text-secondary)' }" /></button><button @click="deleteKPI(kpi.id)" class="p-1 rounded hover:bg-red-500/10"><Trash2 class="w-3 h-3" :style="{ color: 'var(--text-secondary)' }" /></button></div></div>
            <div class="flex items-end gap-2 mb-2"><span class="text-2xl font-extrabold" :style="{ color: 'var(--accent)' }">{{ kpi.current_value }}</span><span class="text-xs" :style="{ color: 'var(--text-secondary)' }">از {{ kpi.target_value }} {{ kpi.unit }}</span></div>
            <div class="w-full h-2 rounded-full" :style="{ background: 'var(--bg-primary)' }"><div class="h-full rounded-full transition-all" :style="{ width: kpiPercent(kpi) + '%', background: 'var(--accent)' }"></div></div>
            <span class="text-xs" :style="{ color: 'var(--accent)' }">{{ kpiPercent(kpi) }}%</span>
          </div>
        </div>
      </div>

      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4"><h2 class="text-lg font-bold flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">🎯 زیرهدف‌ها و تسک‌ها</h2><button @click="showSubGoalForm = true; resetSubGoalForm()" class="px-4 py-2 text-sm rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }"><Plus class="w-4 h-4 inline" /> زیرهدف جدید</button></div>
        <div v-if="subGoals.length === 0" class="text-center py-8" :style="{ color: 'var(--text-secondary)' }"><Target class="w-10 h-10 mx-auto mb-2 opacity-30" />هنوز زیرهدفی تعریف نشده.</div>
        <div class="space-y-3">
          <div v-for="sg in subGoals" :key="sg.id" class="rounded-xl overflow-hidden" :style="{ background: 'var(--bg-hover)' }">
            <div class="flex items-center justify-between p-4 cursor-pointer" @click="toggleExpand(sg.id)">
              <div class="flex items-center gap-3 flex-1">
                <ChevronDown class="w-4 h-4 transition-transform" :class="expandedSubGoals[sg.id] ? 'rotate-90' : ''" :style="{ color: 'var(--text-secondary)' }" />
                <span class="text-xs px-2 py-1 rounded-full" :style="{ background: sg.status === 'completed' ? 'rgba(34,197,94,0.2)' : sg.status === 'in_progress' ? 'rgba(139,92,246,0.2)' : 'rgba(100,100,100,0.2)', color: sg.status === 'completed' ? '#22c55e' : sg.status === 'in_progress' ? '#8b5cf6' : '#888' }">{{ sg.status === 'completed' ? 'تکمیل' : sg.status === 'in_progress' ? 'در حال انجام' : 'شروع نشده' }}</span>
                <h3 class="font-bold flex-1" :style="{ color: 'var(--text-primary)' }">{{ sg.title }}</h3>
                <div class="flex items-center gap-2"><div class="w-20 h-2 rounded-full" :style="{ background: 'var(--bg-primary)' }"><div class="h-full rounded-full transition-all" :style="{ width: subGoalProgress(sg) + '%', background: 'var(--accent)' }"></div></div><span class="text-xs font-bold w-8 text-left" :style="{ color: 'var(--accent)' }">{{ subGoalProgress(sg) }}%</span></div>
              </div>
              <div class="flex gap-1 mr-2" @click.stop><button @click="editSubGoal(sg)" class="p-1.5 rounded hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-3.5 h-3.5" /></button><button @click="deleteSubGoal(sg.id)" class="p-1.5 rounded hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-3.5 h-3.5" /></button></div>
            </div>
            <div v-if="expandedSubGoals[sg.id]" class="px-4 pb-4 border-t" :style="{ borderColor: 'var(--border)' }">
              <div class="space-y-1.5 mt-3">
                <div v-for="task in sg.tasks" :key="task.id" class="flex items-center gap-2 text-sm py-1">
                  <button @click="toggleTask(task)" class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 transition" :style="{ background: task.is_completed ? 'var(--accent)' : 'transparent', borderColor: task.is_completed ? 'var(--accent)' : 'var(--border)' }"><Check v-if="task.is_completed" class="w-3 h-3 text-white" /></button>

                  <div v-if="editingTaskId === task.id" class="flex-1 flex flex-wrap gap-2">
                    <input v-model="editingTaskForm.title" class="flex-1 min-w-[140px] px-2 py-1 rounded-lg text-xs" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
                    <DateInputPersian v-model="editingTaskForm.due_date" placeholder="مهلت" />
                    <select v-model.number="editingTaskForm.priority" class="px-2 py-1 rounded-lg text-xs" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                      <option :value="0">عادی</option>
                      <option :value="1">مهم</option>
                      <option :value="2">اضطراری</option>
                    </select>
                    <label class="flex items-center gap-1 text-xs" :style="{ color: 'var(--text-secondary)' }"><input v-model="editingTaskForm.is_completed" type="checkbox" /> تکمیل</label>
                    <button @click="saveTaskEdit(task.id)" class="px-2 py-1 rounded-lg text-xs text-white" :style="{ background: 'var(--accent)' }">ذخیره</button>
                    <button @click="cancelEditTask" class="px-2 py-1 rounded-lg text-xs" :style="{ background: 'var(--bg-primary)', color: 'var(--text-secondary)' }">لغو</button>
                  </div>

                  <div v-else class="flex-1 flex items-center gap-2">
                    <span :style="{ color: task.is_completed ? 'var(--text-secondary)' : 'var(--text-primary)', textDecoration: task.is_completed ? 'line-through' : 'none' }">{{ task.title }}</span>
                    <span v-if="task.due_date" class="text-[10px] px-2 py-0.5 rounded-full" :style="{ background: 'rgba(255,255,255,0.08)', color: 'var(--text-secondary)' }">📅 {{ formatDate(task.due_date) }}</span>
                    <span v-if="task.priority === 2" class="text-red-400 text-[10px]">⚡</span>
                  </div>

                  <div v-if="editingTaskId !== task.id" class="flex gap-1">
                    <button @click="startEditTask(task)" class="p-1 rounded hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-3 h-3" /></button>
                    <button @click="deleteTask(task)" class="p-1 rounded hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-3 h-3" /></button>
                  </div>
                </div>
                <div class="flex gap-2 mt-2">
                  <button @click="openNewTaskModal(sg.id)" class="px-3 py-1.5 text-xs rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }"><Plus class="w-3 h-3 inline" /> تسک جدید</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSubGoalForm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="showSubGoalForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4"><h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingSubGoal ? 'ویرایش زیرهدف' : 'زیرهدف جدید' }}</h3><button @click="showSubGoalForm = false; resetSubGoalForm()" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button></div>
        <div class="space-y-3">
          <input v-model="subGoalForm.title" placeholder="عنوان زیرهدف *" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          <div class="grid grid-cols-2 gap-2"><DateInputPersian v-model="subGoalForm.start_date" placeholder="تاریخ شروع" /><DateInputPersian v-model="subGoalForm.target_date" placeholder="تاریخ هدف" /></div>
          <select v-model="subGoalForm.status" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"><option value="not_started">شروع نشده</option><option value="in_progress">در حال انجام</option><option value="completed">تکمیل شده</option></select>
        </div>
        <div class="flex gap-2 mt-4"><button @click="saveSubGoal" class="flex-1 py-2 rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button><button @click="showSubGoalForm = false; resetSubGoalForm()" class="px-4 py-2 rounded-lg" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button></div>
      </div>
    </div>

    <TaskFormModal
      v-model="showTaskModal"
      :form="taskForm"
      :validation-errors="validationErrors"
      :categories="categories"
      :goals="goals"
      :sub-goals="subGoals"
      :editing-task="editingTask"
      :is-loading="isLoading"
      @update:form="(value) => taskForm = value"
      @goal-change="onGoalChange"
      @save="saveTask"
    />

        <div v-if="showKPIForm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="showKPIForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingKPI ? 'ویرایش KPI' : 'KPI جدید' }}</h3>
          <button @click="showKPIForm = false; resetKPIForm()" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <input v-model="kpiForm.title" placeholder="عنوان KPI" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          <div class="grid grid-cols-2 gap-2">
            <select v-model="kpiForm.unit" class="px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="تومان">تومان</option>
              <option value="نفر">نفر</option>
              <option value="ساعت">ساعت</option>
              <option value="عدد">عدد</option>
              <option value="درصد">درصد</option>
            </select>
            <select v-model="kpiForm.frequency" class="px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="daily">روزانه</option>
              <option value="weekly">هفتگی</option>
              <option value="monthly">ماهانه</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <input v-model.number="kpiForm.target_value" type="number" placeholder="هدف" class="px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            <input v-model.number="kpiForm.current_value" type="number" placeholder="فعلی" class="px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="saveKPI" class="flex-1 py-2 rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showKPIForm = false; resetKPIForm()" class="px-4 py-2 rounded-lg" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>