<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, Check, X, Target, Calendar, Flag, AlertTriangle, Zap, History, Clock } from 'lucide-vue-next'
import api from '@/services/api'

const themeStore = useThemeStore()
const goals = ref([])
const recentLogs = ref([])
const showForm = ref(false)
const showLogs = ref(false)
const editingGoal = ref(null)
const isLoading = ref(false)
const validationErrors = ref({})

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
  // پاک کردن خطاهای قبلی
  validationErrors.value = {}
  
  // اعتبارسنجی
  let hasError = false
  
  if (!form.value.title || !form.value.title.trim()) {
    validationErrors.value.title = 'عنوان هدف اجباری است'
    hasError = true
  }
  
  if (form.value.start_date && form.value.target_date) {
    if (new Date(form.value.target_date) < new Date(form.value.start_date)) {
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
    await fetchGoals()
    await fetchLogs()
    showToast('🗑️ همه اهداف حذف شدند')
  } catch (error) {
    console.error('خطا در حذف همه اهداف', error)
  }
}

const showToast = (msg, type = 'success') => {
  // استفاده از message در template
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
    class="p-6 md:p-10 max-w-5xl mx-auto relative z-10 min-h-screen"
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
         class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[100] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between mb-6 relative">
      <div>
        <h1 class="text-3xl font-extrabold" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">اهداف کلان</h1>
        <p :style="{ color: 'var(--text-secondary)' }">مسیر موفقیتت رو مشخص کن</p>
      </div>
      <div class="flex gap-3">
        <button @click="resetAllGoals"
                class="px-4 py-2 rounded-xl transition text-sm"
                :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <Trash2 class="w-4 h-4 inline ml-1" /> حذف همه
        </button>
        <button @click="openNewForm"
                class="px-5 py-2 text-white font-semibold rounded-xl transition flex items-center gap-2"
                :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> هدف جدید
        </button>
      </div>
    </div>

    <!-- Recent Activity Timeline -->
    <div class="mb-10 relative">
      <button @click="showLogs = !showLogs"
              class="flex items-center gap-2 text-sm mb-4 transition"
              :style="{ color: 'var(--accent)' }">
        <History class="w-5 h-5" />
        <span>آخرین تغییرات</span>
        <span :class="showLogs ? 'rotate-90' : ''" class="transition-transform inline-block">▶</span>
        <span class="text-xs px-2 py-0.5 rounded-full" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">{{ recentLogs.length }}</span>
      </button>

      <div v-if="showLogs" class="space-y-3">
        <div v-if="recentLogs.length === 0" class="text-center py-4 rounded-xl" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          هنوز تغییری ثبت نشده.
        </div>
        
        <div v-for="log in recentLogs" :key="log.id"
             class="flex items-start gap-3 p-3 rounded-xl transition"
             :style="{ background: 'var(--bg-hover)' }">
          
          <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
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
            <p class="text-sm" :style="{ color: 'var(--text-primary)' }">{{ log.description }}</p>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-xs px-2 py-0.5 rounded-full"
                    :style="{ 
                      background: log.action === 'created' ? 'rgba(34,197,94,0.15)' : 
                                  log.action === 'deleted' ? 'rgba(239,68,68,0.15)' : 
                                  'rgba(139,92,246,0.15)',
                      color: log.action === 'created' ? '#22c55e' : 
                             log.action === 'deleted' ? '#ef4444' : '#8b5cf6'
                    }">
                {{ log.action === 'created' ? 'ایجاد' : log.action === 'deleted' ? 'حذف' : 'بروزرسانی' }}
              </span>
              <span class="text-xs" :style="{ color: 'var(--text-secondary)' }">
                {{ new Date(log.created_at).toLocaleString('fa-IR') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Modal -->
    <div v-if="showForm" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="w-full max-w-2xl rounded-2xl p-6 max-h-[90vh] overflow-y-auto"
           :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingGoal ? 'ویرایش هدف' : 'هدف جدید' }}</h2>
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
                   class="w-full px-4 py-3 rounded-xl transition text-right"
                   :style="{ 
                     background: 'var(--bg-primary)', 
                     border: validationErrors.title ? '2px solid #ef4444' : '1px solid var(--border)', 
                     color: 'var(--text-primary)' 
                   }" />
            <p v-if="validationErrors.title" class="text-red-400 text-xs mt-1 mr-1">{{ validationErrors.title }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ تعریف هدف</label>
              <input v-model="form.start_date" type="date"
                     class="w-full px-4 py-3 rounded-xl transition text-right"
                     :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: validationErrors.target_date ? '#ef4444' : 'var(--text-secondary)' }">
                تاریخ تحقق هدف {{ validationErrors.target_date ? '⚠️' : '' }}
              </label>
              <input v-model="form.target_date" type="date"
                     class="w-full px-4 py-3 rounded-xl transition text-right"
                     :style="{ 
                       background: 'var(--bg-primary)', 
                       border: validationErrors.target_date ? '2px solid #ef4444' : '1px solid var(--border)', 
                       color: 'var(--text-primary)' 
                     }" />
              <p v-if="validationErrors.target_date" class="text-red-400 text-xs mt-1 mr-1">{{ validationErrors.target_date }}</p>
            </div>
          </div>

          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">آخرین وضعیت</label>
            <textarea v-model="form.current_status" rows="2" placeholder="الان کجای کاری؟"
                      class="w-full px-4 py-3 rounded-xl transition text-right"
                      :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>

          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">مانع فعلی تحقق</label>
            <textarea v-model="form.current_obstacle" rows="2" placeholder="چه چیزی جلوت رو گرفته؟"
                      class="w-full px-4 py-3 rounded-xl transition text-right"
                      :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>

          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">گام بعدی</label>
            <input v-model="form.next_step" type="text" placeholder="قدم بعدی چیه؟"
                   class="w-full px-4 py-3 rounded-xl transition text-right"
                   :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">اولویت</label>
              <select v-model="form.priority"
                      class="w-full px-4 py-3 rounded-xl transition text-right"
                      :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
                <option :value="0">عادی</option>
                <option :value="1">متوسط</option>
                <option :value="2">فوری</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">معیار موفقیت</label>
              <input v-model="form.success_criteria" type="text" placeholder="از کجا بفهمی موفق شدی؟"
                     class="w-full px-4 py-3 rounded-xl transition text-right"
                     :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="saveGoal" :disabled="isLoading"
                  class="flex-1 py-3 text-white font-semibold rounded-xl transition disabled:opacity-50"
                  :style="{ background: 'var(--accent)' }">
            {{ editingGoal ? 'بروزرسانی' : 'ایجاد هدف' }}
          </button>
          <button @click="showForm = false"
                  class="px-6 py-3 rounded-xl transition"
                  :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
            انصراف
          </button>
        </div>
      </div>
    </div>

    <!-- Goals List -->
    <div v-if="goals.length === 0" class="text-center py-20 relative">
      <Target class="w-16 h-16 mx-auto mb-4" :style="{ color: 'var(--accent)' }" />
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">هنوز هیچ هدفی تعریف نکردی!</p>
      <p :style="{ color: 'var(--text-secondary)' }">اولین هدف رو بساز و مسیر موفقیتت رو شروع کن.</p>
      <button @click="openNewForm"
              class="mt-6 px-8 py-3 text-white font-semibold rounded-xl transition inline-flex items-center gap-2"
              :style="{ background: 'var(--accent)' }">
        <Plus class="w-5 h-5" /> ساخت اولین هدف
      </button>
    </div>

    <div v-else class="space-y-6 relative">
      <div v-for="goal in goals" :key="goal.id"
           class="rounded-2xl p-6 transition-all duration-300"
           :class="themeStore.currentTheme === 'persian-classic' ? 'card-ornament' : themeStore.currentTheme === 'cyber-digital' ? 'neon-border' : 'glass-card'"
           :style="{ background: 'var(--bg-card)' }">
        
        <!-- Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <Target class="w-5 h-5" :style="{ color: 'var(--accent)' }" />
              <h3 class="text-xl font-bold" :style="{ color: 'var(--text-primary)' }">{{ goal.title }}</h3>
              <span :class="[priorityColors[goal.priority], 'text-xs flex items-center gap-1']">
                <Flag class="w-3 h-3" /> {{ priorityLabels[goal.priority] }}
              </span>
            </div>
            <p v-if="goal.description" :style="{ color: 'var(--text-secondary)' }" class="text-sm">{{ goal.description }}</p>
          </div>
          <div class="flex gap-2">
            <button @click="openEditForm(goal)" class="p-2 rounded-lg transition hover:bg-white/5" :style="{ color: 'var(--text-secondary)' }">
              <Edit3 class="w-4 h-4" />
            </button>
            <button @click="deleteGoal(goal.id)" class="p-2 rounded-lg transition hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-if="goal.start_date" class="flex items-center gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
            <Calendar class="w-4 h-4" />
            <span>شروع: {{ goal.start_date }}</span>
          </div>
          <div v-if="goal.target_date" class="flex items-center gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
            <Calendar class="w-4 h-4" />
            <span>پایان: {{ goal.target_date }}</span>
          </div>
          <div v-if="goal.current_status" class="flex items-start gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
            <Zap class="w-4 h-4 mt-0.5" />
            <span>وضعیت: {{ goal.current_status }}</span>
          </div>
          <div v-if="goal.current_obstacle" class="flex items-start gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
            <AlertTriangle class="w-4 h-4 mt-0.5" />
            <span>مانع: {{ goal.current_obstacle }}</span>
          </div>
          <div v-if="goal.next_step" class="flex items-start gap-2 text-sm" :style="{ color: 'var(--accent)' }">
            <Check class="w-4 h-4 mt-0.5" />
            <span>گام بعدی: {{ goal.next_step }}</span>
          </div>
          <div v-if="goal.success_criteria" class="flex items-center gap-2 text-sm" :style="{ color: 'var(--text-secondary)' }">
            <Target class="w-4 h-4" />
            <span>معیار موفقیت: {{ goal.success_criteria }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>