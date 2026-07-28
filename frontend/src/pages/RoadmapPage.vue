<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, X, Target, Calendar, Flag, Zap, BarChart3, ChevronDown, ChevronUp } from 'lucide-vue-next'
import api from '@/services/api'

const themeStore = useThemeStore()

const goals = ref([])
const selectedGoalId = ref(null)
const subGoals = ref([])
const kpis = ref([])

// فرم‌ها
const showSubGoalForm = ref(false)
const showKPIForm = ref(false)
const editingSubGoal = ref(null)
const editingKPI = ref(null)
const expandedSubGoals = ref({})

const subGoalForm = ref({ title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 })
const kpiForm = ref({ title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' })
const newTaskTitle = ref({})
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

const fetchSubGoals = async () => {
  if (!selectedGoalId.value) return
  try {
    const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/subgoals`)
    subGoals.value = res.data
  } catch (e) {}
}

const fetchKPIs = async () => {
  if (!selectedGoalId.value) return
  try {
    const res = await api.get(`/roadmap/goal/${selectedGoalId.value}/kpis`)
    kpis.value = res.data
  } catch (e) {}
}

const selectGoal = (id) => {
  selectedGoalId.value = id
  fetchSubGoals()
  fetchKPIs()
}

// ====== SubGoal ======
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
  try {
    await api.delete(`/roadmap/subgoals/${id}`)
    showToast('🗑️ زیرهدف حذف شد')
    await fetchSubGoals()
  } catch (e) {}
}

const editSubGoal = (sg) => {
  subGoalForm.value = { 
    title: sg.title, description: sg.description || '', 
    start_date: sg.start_date || '', target_date: sg.target_date || '', 
    status: sg.status, order_index: sg.order_index 
  }
  editingSubGoal.value = sg
  showSubGoalForm.value = true
}

const resetSubGoalForm = () => {
  subGoalForm.value = { title: '', description: '', start_date: '', target_date: '', status: 'not_started', order_index: 0 }
  editingSubGoal.value = null
}

const toggleExpand = (id) => {
  expandedSubGoals.value[id] = !expandedSubGoals.value[id]
}

const subGoalProgress = (sg) => {
  if (!sg.tasks || sg.tasks.length === 0) return 0
  const done = sg.tasks.filter(t => t.is_completed).length
  return Math.round((done / sg.tasks.length) * 100)
}

// ====== Tasks ======
const addTask = async (subGoalId) => {
  const title = newTaskTitle.value[subGoalId]
  if (!title?.trim()) return
  try {
    await api.post(`/roadmap/subgoals/${subGoalId}/tasks`, { title, priority: 0 })
    newTaskTitle.value[subGoalId] = ''
    await fetchSubGoals()
  } catch (e) {}
}

const toggleTask = async (task) => {
  try {
    await api.put(`/roadmap/tasks/${task.id}`, { is_completed: !task.is_completed })
    await fetchSubGoals()
  } catch (e) {}
}

const deleteTask = async (taskId) => {
  try {
    await api.delete(`/roadmap/tasks/${taskId}`)
    await fetchSubGoals()
  } catch (e) {}
}

// ====== KPI ======
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

const editKPI = (kpi) => {
  kpiForm.value = { ...kpi }
  editingKPI.value = kpi
  showKPIForm.value = true
}

const deleteKPI = async (id) => {
  try {
    await api.delete(`/roadmap/kpis/${id}`)
    showToast('🗑️ KPI حذف شد')
    await fetchKPIs()
  } catch (e) {}
}

const resetKPIForm = () => {
  kpiForm.value = { title: '', unit: 'عدد', target_value: 0, current_value: 0, frequency: 'monthly' }
  editingKPI.value = null
}

const kpiPercent = (kpi) => {
  if (!kpi.target_value) return 0
  return Math.min(100, Math.round((kpi.current_value / kpi.target_value) * 100))
}

onMounted(fetchGoals)
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative z-10 min-h-screen"
       :class="themeStore.currentTheme === 'persian-classic' ? 'page-bg-tasks' : themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''">
    
    <!-- Toast -->
    <div v-if="message" 
         class="fixed top-4 left-1/2 transform -translate-x-1/2 z-[100] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold mb-2" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">نقشه راه</h1>
      <p :style="{ color: 'var(--text-secondary)' }">اهداف کلان رو به قدم‌های کوچک تقسیم کن و پیشرفت رو اندازه بگیر</p>
    </div>

    <!-- انتخاب هدف کلان -->
    <div class="mb-8">
      <label class="block text-sm mb-2" :style="{ color: 'var(--text-secondary)' }">🎯 هدف کلان مورد نظر رو انتخاب کن:</label>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <button 
          v-for="goal in goals" :key="goal.id"
          @click="selectGoal(goal.id)"
          class="p-4 rounded-xl text-right transition-all duration-200"
          :style="selectedGoalId === goal.id 
            ? { background: 'var(--accent)', color: '#fff' } 
            : { background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }"
        >
          <div class="flex items-center gap-2">
            <Target class="w-4 h-4" />
            <span class="font-medium">{{ goal.title }}</span>
          </div>
          <p class="text-xs mt-1 opacity-70">{{ goal.current_status || 'بدون وضعیت' }}</p>
        </button>
      </div>
      <p v-if="goals.length === 0" :style="{ color: 'var(--text-secondary)' }" class="mt-2 text-sm">
        اول برو به صفحه <router-link to="/goals" style="color: var(--accent)">اهداف</router-link> و یه هدف کلان بساز.
      </p>
    </div>

    <!-- محتوا -->
    <div v-if="selectedGoalId" class="space-y-8">
      
      <!-- ============ KPI ها ============ -->
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            <BarChart3 class="w-5 h-5" :style="{ color: 'var(--accent)' }" /> شاخص‌های کلیدی (KPI)
          </h2>
          <button @click="showKPIForm = true; resetKPIForm()" class="px-4 py-2 text-sm rounded-lg text-white font-semibold flex items-center gap-1" :style="{ background: 'var(--accent)' }">
            <Plus class="w-4 h-4" /> KPI جدید
          </button>
        </div>
        
        <div v-if="kpis.length === 0" class="text-center py-6" :style="{ color: 'var(--text-secondary)' }">
          <BarChart3 class="w-10 h-10 mx-auto mb-2 opacity-30" />
          هنوز KPI تعریف نشده. شاخص‌های عددی برای سنجش پیشرفتت تعریف کن.
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="kpi in kpis" :key="kpi.id" class="p-4 rounded-xl relative group" :style="{ background: 'var(--bg-hover)' }">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-bold text-sm" :style="{ color: 'var(--text-primary)' }">{{ kpi.title }}</h4>
              <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                <button @click="editKPI(kpi)" class="p-1 rounded hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-3 h-3" /></button>
                <button @click="deleteKPI(kpi.id)" class="p-1 rounded hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-3 h-3" /></button>
              </div>
            </div>
            <div class="flex items-end gap-2 mb-2">
              <span class="text-2xl font-extrabold" :style="{ color: 'var(--accent)' }">{{ kpi.current_value.toLocaleString() }}</span>
              <span class="text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">از {{ kpi.target_value.toLocaleString() }} {{ kpi.unit }}</span>
            </div>
            <div class="w-full h-2 rounded-full" :style="{ background: 'var(--bg-primary)' }">
              <div class="h-full rounded-full transition-all duration-500" 
                   :style="{ width: kpiPercent(kpi) + '%', background: kpiPercent(kpi) >= 100 ? '#22c55e' : 'var(--accent)' }"></div>
            </div>
            <div class="flex justify-between mt-1">
              <span class="text-xs font-bold" :style="{ color: 'var(--accent)' }">{{ kpiPercent(kpi) }}%</span>
              <span class="text-xs" :style="{ color: 'var(--text-secondary)' }">{{ kpi.frequency === 'daily' ? 'روزانه' : kpi.frequency === 'weekly' ? 'هفتگی' : 'ماهانه' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ زیرهدف‌ها ============ -->
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            🎯 زیرهدف‌ها و تسک‌ها
          </h2>
          <button @click="showSubGoalForm = true; resetSubGoalForm()" class="px-4 py-2 text-sm rounded-lg text-white font-semibold flex items-center gap-1" :style="{ background: 'var(--accent)' }">
            <Plus class="w-4 h-4" /> زیرهدف جدید
          </button>
        </div>

        <div v-if="subGoals.length === 0" class="text-center py-8" :style="{ color: 'var(--text-secondary)' }">
          <Target class="w-10 h-10 mx-auto mb-2 opacity-30" />
          هنوز زیرهدفی تعریف نشده. هدف کلان رو به قدم‌های کوچک تقسیم کن!
        </div>

        <div class="space-y-3">
          <div v-for="sg in subGoals" :key="sg.id" class="rounded-xl overflow-hidden" :style="{ background: 'var(--bg-hover)' }">
            
            <!-- هدر زیرهدف -->
            <div class="flex items-center justify-between p-4 cursor-pointer" @click="toggleExpand(sg.id)">
              <div class="flex items-center gap-3 flex-1">
                <button @click.stop="toggleExpand(sg.id)" class="transition-transform" :class="expandedSubGoals[sg.id] ? 'rotate-90' : ''">
                  <ChevronDown class="w-4 h-4" :style="{ color: 'var(--text-secondary)' }" />
                </button>
                
                <!-- وضعیت -->
                <span class="text-xs px-2 py-1 rounded-full flex-shrink-0" :style="{ 
                  background: sg.status === 'completed' ? 'rgba(34,197,94,0.2)' : sg.status === 'in_progress' ? 'rgba(139,92,246,0.2)' : 'rgba(100,100,100,0.2)',
                  color: sg.status === 'completed' ? '#22c55e' : sg.status === 'in_progress' ? '#8b5cf6' : '#888'
                }">{{ sg.status === 'completed' ? 'تکمیل' : sg.status === 'in_progress' ? 'در حال انجام' : 'شروع نشده' }}</span>
                
                <h3 class="font-bold flex-1" :style="{ color: 'var(--text-primary)' }">{{ sg.title }}</h3>
                
                <!-- درصد پیشرفت -->
                <div class="flex items-center gap-2">
                  <div class="w-20 h-2 rounded-full" :style="{ background: 'var(--bg-primary)' }">
                    <div class="h-full rounded-full transition-all" :style="{ width: subGoalProgress(sg) + '%', background: 'var(--accent)' }"></div>
                  </div>
                  <span class="text-xs font-bold w-8 text-left" :style="{ color: 'var(--accent)' }">{{ subGoalProgress(sg) }}%</span>
                </div>
              </div>
              
              <div class="flex gap-1 mr-2" @click.stop>
                <button @click="editSubGoal(sg)" class="p-1.5 rounded hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-3.5 h-3.5" /></button>
                <button @click="deleteSubGoal(sg.id)" class="p-1.5 rounded hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-3.5 h-3.5" /></button>
              </div>
            </div>

            <!-- بدنه (بازشو) -->
            <div v-if="expandedSubGoals[sg.id]" class="px-4 pb-4 border-t" :style="{ borderColor: 'var(--border)' }">
              
              <!-- اطلاعات -->
              <div v-if="sg.start_date || sg.target_date || sg.description" class="grid grid-cols-1 md:grid-cols-3 gap-3 my-3 text-xs" :style="{ color: 'var(--text-secondary)' }">
                <span v-if="sg.start_date">📅 شروع: {{ sg.start_date }}</span>
                <span v-if="sg.target_date">🏁 پایان: {{ sg.target_date }}</span>
                <span v-if="sg.description">📝 {{ sg.description }}</span>
              </div>

              <!-- تسک‌ها -->
              <div class="space-y-1.5 mt-3">
                <div v-for="task in sg.tasks" :key="task.id" class="flex items-center gap-2 text-sm py-1">
                  <button @click="toggleTask(task)" 
                          class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 transition"
                          :style="{ background: task.is_completed ? 'var(--accent)' : 'transparent', borderColor: task.is_completed ? 'var(--accent)' : 'var(--border)' }">
                    <Check v-if="task.is_completed" class="w-3 h-3 text-white" />
                  </button>
                  <span class="flex-1" :style="{ color: task.is_completed ? 'var(--text-secondary)' : 'var(--text-primary)', textDecoration: task.is_completed ? 'line-through' : 'none' }">{{ task.title }}</span>
                  <button @click="deleteTask(task.id)" class="opacity-0 hover:opacity-100 text-xs transition" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-3 h-3" /></button>
                </div>
                
                <!-- افزودن تسک -->
                <div class="flex gap-2 mt-2">
                  <input 
                    v-model="newTaskTitle[sg.id]"
                    @keyup.enter="addTask(sg.id)"
                    placeholder="تسک جدید..."
                    class="flex-1 px-3 py-1.5 text-xs rounded-lg"
                    :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"
                  />
                  <button @click="addTask(sg.id)" class="px-3 py-1.5 text-xs rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }">
                    <Plus class="w-3 h-3 inline" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ========== مودال زیرهدف ========== -->
    <div v-if="showSubGoalForm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="showSubGoalForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingSubGoal ? 'ویرایش زیرهدف' : 'زیرهدف جدید' }}</h3>
          <button @click="showSubGoalForm = false; resetSubGoalForm()" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <input v-model="subGoalForm.title" placeholder="عنوان زیرهدف *" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          <textarea v-model="subGoalForm.description" placeholder="توضیحات (اختیاری)" rows="2" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">تاریخ شروع</label>
              <input v-model="subGoalForm.start_date" type="date" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
            <div>
              <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">تاریخ پایان</label>
              <input v-model="subGoalForm.target_date" type="date" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
          </div>
          <div>
            <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">وضعیت</label>
            <select v-model="subGoalForm.status" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="not_started">شروع نشده</option>
              <option value="in_progress">در حال انجام</option>
              <option value="completed">تکمیل شده</option>
            </select>
          </div>
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="saveSubGoal" class="flex-1 py-2 rounded-lg text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showSubGoalForm = false; resetSubGoalForm()" class="px-4 py-2 rounded-lg" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>

    <!-- ========== مودال KPI ========== -->
    <div v-if="showKPIForm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="showKPIForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingKPI ? 'ویرایش KPI' : 'KPI جدید' }}</h3>
          <button @click="showKPIForm = false; resetKPIForm()" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <input v-model="kpiForm.title" placeholder="عنوان KPI (مثلاً: درآمد ماهانه)" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">واحد</label>
              <select v-model="kpiForm.unit" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option value="تومان">تومان</option>
                <option value="نفر">نفر</option>
                <option value="ساعت">ساعت</option>
                <option value="کیلو">کیلو</option>
                <option value="عدد">عدد</option>
                <option value="درصد">درصد</option>
              </select>
            </div>
            <div>
              <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">بازه</label>
              <select v-model="kpiForm.frequency" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option value="daily">روزانه</option>
                <option value="weekly">هفتگی</option>
                <option value="monthly">ماهانه</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">مقدار هدف</label>
              <input v-model.number="kpiForm.target_value" type="number" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
            <div>
              <label class="text-xs mb-1 block" :style="{ color: 'var(--text-secondary)' }">مقدار فعلی</label>
              <input v-model.number="kpiForm.current_value" type="number" class="w-full px-3 py-2 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
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