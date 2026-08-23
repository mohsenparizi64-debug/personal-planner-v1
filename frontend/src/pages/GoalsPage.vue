<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, X, Target, Calendar, Flag, AlertTriangle, Zap, History, Clock, ArrowRight, Eye, Sparkles } from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'
import { useRouter } from 'vue-router'

const themeStore = useThemeStore()
const goals = ref([])
const recentLogs = ref([])
const showForm = ref(false)
const showLogs = ref(false)
const editingGoal = ref(null)
const selectedGoal = ref(null) // <--- استیت مربوط به حالت تمرکز و فوکوس روی هدف
const isLoading = ref(false)
const validationErrors = ref({})
const router = useRouter()

const goToRoadmap = (goalId) => {
  sessionStorage.setItem('active_goal_id', goalId)
  router.push('/roadmap')
}

// انتخاب هدف برای حالت تمرکز (Spotlight Focus)
const selectGoalForFocus = (goal) => {
  selectedGoal.value = goal
}

const closeFocusMode = () => {
  selectedGoal.value = null
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
  fetchLogs()
})
</script>

<template>
  <div 
    class="p-6 md:p-10 max-w-7xl mx-auto relative z-10 min-h-screen text-right" dir="rtl"
    :class="themeStore.currentTheme === 'persian-classic' ? 'page-bg-tasks' : themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''"
  >
    <!-- الگوی اسلیمی -->
    <div v-if="themeStore.currentTheme === 'persian-classic'" class="absolute inset-0 persian-pattern opacity-20 pointer-events-none"></div>
    
    <!-- ذرات رباتیک -->
    <div v-if="themeStore.currentTheme === 'cyber-digital'" class="particles">
      <div v-for="i in 15" :key="i" class="particle" :style="{ left: Math.random() * 100 + '%', animationDelay: Math.random() * 4 + 's' }"></div>
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

    <!-- 🌟 چیدمان اصلی دو ستونه اهداف (Two-Column Grid) -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
      <div v-for="goal in goals" :key="goal.id"
           @click="selectGoalForFocus(goal)"
           class="rounded-3xl p-6 transition-all duration-300 border shadow-md hover:shadow-2xl hover:-translate-y-1 cursor-pointer flex flex-col justify-between group relative overflow-hidden"
           :class="themeStore.currentTheme === 'persian-classic' ? 'card-ornament' : themeStore.currentTheme === 'cyber-digital' ? 'neon-border' : ''"
           :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        
        <div>
          <!-- Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <div class="flex items-center gap-2.5 mb-2">
                <Target class="w-6 h-6 group-hover:rotate-12 transition-transform" :style="{ color: 'var(--accent)' }" />
                <h3 class="text-lg font-black group-hover:text-purple-400 transition" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</h3>
              </div>
              <span :class="[priorityColors[goal.priority], 'text-[11px] font-extrabold flex items-center gap-1 bg-white/5 px-2.5 py-1 rounded-lg w-fit']">
                <Flag class="w-3 h-3" /> {{ priorityLabels[goal.priority] }}
              </span>
            </div>

            <div class="flex gap-1" @click.stop>
              <button @click="openEditForm(goal)" title="ویرایش" class="p-2 rounded-xl transition hover:bg-white/10 text-gray-400 hover:text-white">
                <Edit3 class="w-4 h-4" />
              </button>
              <button @click="deleteGoal(goal.id)" title="حذف" class="p-2 rounded-xl transition hover:bg-red-500/10 text-gray-400 hover:text-red-400">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <p v-if="goal.description" :style="{ color: 'var(--text-secondary)' }" class="text-xs opacity-80 mb-4 line-clamp-2 leading-relaxed">{{ goal.description }}</p>

          <!-- خلاصه فیلدها در کارت عمومی -->
          <div class="space-y-2 border-t pt-3" :style="{ borderColor: 'var(--border)' }">
            <div v-if="goal.next_step" class="flex items-center gap-2 text-xs font-bold" :style="{ color: 'var(--accent)' }">
              <Check class="w-3.5 h-3.5 text-green-400" />
              <span class="truncate">گام بعدی: {{ goal.next_step }}</span>
            </div>
            <div v-if="goal.target_date" class="flex items-center gap-2 text-xs opacity-70" :style="{ color: 'var(--text-secondary)' }">
              <Calendar class="w-3.5 h-3.5 text-purple-400" />
              <span>تحقق: {{ formatDate(goal.target_date) }}</span>
            </div>
          </div>
        </div>

        <!-- دکمه‌های پایینی کارت دو ستونه -->
        <div class="flex items-center justify-between gap-2 mt-5 pt-3 border-t" :style="{ borderColor: 'var(--border)' }" @click.stop>
          <button @click="selectGoalForFocus(goal)" class="px-3 py-1.5 rounded-xl font-bold text-xs bg-white/5 hover:bg-white/10 text-white transition flex items-center gap-1.5">
            <Eye class="w-3.5 h-3.5 text-amber-400" />
            <span>تمرکز و کامل</span>
          </button>

          <button @click="goToRoadmap(goal.id)" 
                  class="px-3.5 py-1.5 rounded-xl font-bold text-xs text-white transition flex items-center gap-1.5 shadow-md hover:scale-105 active:scale-95 bg-gradient-to-r from-purple-600 to-indigo-600">
            <span>نقشه راه</span>
            <span>➔</span>
          </button>
        </div>

      </div>
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