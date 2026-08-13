<script setup>
import { ref, computed, watch } from 'vue'
import { X, AlertCircle, Calendar, RefreshCw, Star, Tag, AlignLeft, Target, Layers, Flag, CheckCircle2, Clock, Info } from 'lucide-vue-next'
import DateInputPersian from './DateInputPersian.vue'
import { toShamsiDisplay } from '../utils/date'
import api from '@/services/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  form: { type: Object, required: true },
  validationErrors: { type: Object, default: () => ({}) },
  categories: { type: Array, default: () => [] },
  goals: { type: Array, default: () => [] },
  editingTask: { type: Object, default: null },
  isLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'update:form', 'save', 'goal-change'])

const localSubGoals = ref([])
const localErrors = ref({})

// لود خودکار گام‌ها با تغییر هدف
watch(() => props.form.goal_id, async (newId) => {
  if (newId) {
    try {
      const res = await api.get(`/roadmap/goal/${newId}/subgoals`);
      localSubGoals.value = res.data;
    } catch (e) { localSubGoals.value = []; }
  } else { localSubGoals.value = []; }
}, { immediate: true });

// تنظیم پیش‌فرض برنامه‌ریزی اتوماتیک دوره‌ای
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    localErrors.value = {}
    if (formValue.value.auto_reschedule === undefined) {
      formValue.value.auto_reschedule = true
    }
  }
})

const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'فوری' }
const recurrenceOptions = [
  { value: 'none', label: 'بدون تکرار (یک‌باره)' },
  { value: 'daily', label: 'روزانه' },
  { value: 'weekly', label: 'هفتگی' },
  { value: 'monthly', label: 'ماهانه' },
  { value: 'yearly', label: 'سالیانه' },
]

const formValue = computed({
  get: () => props.form,
  set: (val) => emit('update:form', val)
})

const suggestedDueDate = () => {
  const f = formValue.value
  if (!f.register_date || !f.duration_days) return '--'
  const reg = new Date(f.register_date)
  reg.setDate(reg.getDate() + Number(f.duration_days))
  return toShamsiDisplay(reg.toISOString().split('T')[0])
}

const close = () => emit('update:modelValue', false)

// 🚨 اعتبارسنجی صریح فیلدهای اجباری (عنوان، هدف کلان و گام)
const submit = () => {
  localErrors.value = {}
  let hasError = false

  if (!formValue.value.title || !formValue.value.title.trim()) {
    localErrors.value.title = '⚠️ عنوان تسک الزامی است و نمی‌تواند خالی باشد.'
    hasError = true
  }

  if (!formValue.value.goal_id) {
    localErrors.value.goal_id = '⚠️ انتخاب هدف کلان الزامی است.'
    hasError = true
  }

  if (!formValue.value.sub_goal_id) {
    localErrors.value.sub_goal_id = '⚠️ انتخاب گام عملیاتی (زیرهدف) الزامی است.'
    hasError = true
  }

  if (hasError) return

  // محاسبه خودکار due_date قبل از ذخیره
  if (!formValue.value.due_date && formValue.value.register_date && formValue.value.duration_days) {
    const reg = new Date(formValue.value.register_date)
    reg.setDate(reg.getDate() + Number(formValue.value.duration_days))
    formValue.value.due_date = reg.toISOString().split('T')[0]
  }

  emit('save')
}
</script>

<template>
  <!-- 🚀 استفاده از Teleport جهت انتقال مستقیم مودال به rیشه مرورگر (دقیقاً مرکز مانیتور) -->
  <Teleport to="body">
    <div v-if="modelValue" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 md:p-6 bg-black/80 backdrop-blur-md">
      
      <!-- بدنه اصلی فرم فیکس‌شده در مرکز دید بدون حرکت -->
      <div class="w-full max-w-4xl max-h-[85vh] flex flex-col justify-between rounded-3xl p-6 md:p-8 shadow-2xl animate-in zoom-in duration-200 glass-card border-2 border-purple-500/50" :style="{ background: 'var(--bg-card)' }">
        
        <!-- Header -->
        <div class="flex items-center justify-between pb-4 mb-4 border-b flex-shrink-0" :style="{ borderColor: 'var(--border)' }">
          <div class="flex items-center gap-3">
            <div class="p-3 rounded-2xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Tag class="w-6 h-6" />
            </div>
            <div>
              <h2 class="text-2xl font-black" :style="{ color: 'var(--text-primary)' }">{{ editingTask ? 'ویرایش تسک' : 'تعریف تسک جدید' }}</h2>
              <p class="text-xs font-bold opacity-70 mt-1" :style="{ color: 'var(--text-secondary)' }">فرم ساخت تسک با الزامات و راهنمای شفاف کادرها</p>
            </div>
          </div>
          <button @click="close" class="p-2 hover:bg-white/10 rounded-full transition text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
        </div>

        <!-- محتوای فرم با اسکرول بار داخلی -->
        <div class="space-y-6 text-right overflow-y-auto pl-2 pr-1 custom-scrollbar max-h-[65vh]" dir="rtl">
          
          <!-- بخش ۱: عنوان و توضیحات تسک -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              
              <!-- عنوان تسک (اجباری با حاشیه ۲پیکسلی مشخص) -->
              <div>
                <label class="text-sm font-black mb-1.5 flex items-center gap-2" :class="(localErrors.title || validationErrors.title) ? 'text-red-500' : ''" :style="{ color: (localErrors.title || validationErrors.title) ? '#ef4444' : 'var(--text-primary)' }">
                  <Tag class="w-4 h-4 text-purple-400" /> عنوان تسک *
                </label>
                <input 
                  v-model="formValue.title" 
                  placeholder="خلاصه کاری که باید انجام شود..." 
                  class="w-full px-4 py-3.5 rounded-2xl border-2 border-slate-300 dark:border-white/30 text-sm md:text-base font-bold outline-none transition focus:border-purple-500" 
                  :style="{ 
                    background: 'var(--bg-primary)', 
                    borderColor: (localErrors.title || validationErrors.title) ? '#ef4444' : 'var(--border)', 
                    color: 'var(--text-primary)' 
                  }" 
                />
                <p v-if="localErrors.title || validationErrors.title" class="text-xs text-red-500 font-bold mt-1.5 flex items-center gap-1 bg-red-500/10 p-2.5 rounded-xl border border-red-500/30">
                  <AlertCircle class="w-4 h-4" /> {{ localErrors.title || validationErrors.title }}
                </p>
                <p v-else class="text-xs md:text-sm font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">عنوان شفاف و واضح تسک (مثلاً: مطالعه فصل ۳ کتاب پایتون)</p>
              </div>

              <!-- توضیحات تکمیلی (با حاشیه ۲پیکسلی مشخص) -->
              <div>
                <label class="text-sm font-black mb-1.5 flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                  <AlignLeft class="w-4 h-4 text-blue-400" /> توضیحات و جزئیات
                </label>
                <textarea 
                  v-model="formValue.description" 
                  rows="4" 
                  placeholder="جزئیات، نکات کلیدی یا چک‌لیست مربوط به این تسک..." 
                  class="w-full px-4 py-3.5 rounded-2xl border-2 border-slate-300 dark:border-white/30 text-sm font-medium outline-none transition focus:border-purple-500" 
                  :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }"
                ></textarea>
                <p class="text-xs md:text-sm font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">توضیحات اختیاری جهت یادآوری جزئیات کار</p>
              </div>

            </div>

            <!-- بخش ۲: اتصال اجباری به اهداف، گام‌ها، اولویت و دسته‌بندی -->
            <div class="space-y-4">
              
              <div class="p-5 rounded-2xl bg-black/5 dark:bg-white/5 border-2 border-slate-300 dark:border-white/20 space-y-4">
                <!-- متصل به هدف کلان (اجباری) -->
                <div>
                  <label class="text-sm font-black mb-1.5 flex items-center gap-2" :class="localErrors.goal_id ? 'text-red-500' : ''" :style="{ color: localErrors.goal_id ? '#ef4444' : 'var(--text-primary)' }">
                    <Target class="w-4 h-4 text-purple-400" /> متصل به هدف کلان *
                  </label>
                  <select v-model="formValue.goal_id" @change="formValue.sub_goal_id = null" class="w-full px-4 py-3.5 rounded-xl border-2 border-slate-300 dark:border-white/30 text-sm font-bold outline-none" :style="{ background: 'var(--bg-card)', borderColor: localErrors.goal_id ? '#ef4444' : 'var(--border)', color: 'var(--text-primary)' }">
                    <option :value="null">انتخاب هدف کلان (الزامی)...</option>
                    <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
                  </select>
                  <p v-if="localErrors.goal_id" class="text-xs text-red-500 font-bold mt-1.5 flex items-center gap-1 bg-red-500/10 p-2 rounded-xl border border-red-500/30">
                    <AlertCircle class="w-4 h-4" /> {{ localErrors.goal_id }}
                  </p>
                  <p v-else class="text-xs md:text-sm font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">انتخاب هدف بزرگی که این تسک در راستای آن است (الزامی)</p>
                </div>

                <!-- متصل به گام عملیاتی (اجباری) -->
                <div>
                  <label class="text-sm font-black mb-1.5 flex items-center gap-2" :class="localErrors.sub_goal_id ? 'text-red-500' : ''" :style="{ color: localErrors.sub_goal_id ? '#ef4444' : 'var(--text-primary)' }">
                    <Layers class="w-4 h-4 text-indigo-400" /> متصل به گام عملیاتی (نقشه راه) *
                  </label>
                  <select v-model="formValue.sub_goal_id" :disabled="!formValue.goal_id" class="w-full px-4 py-3.5 rounded-xl border-2 border-slate-300 dark:border-white/30 text-sm font-bold outline-none" :style="{ background: 'var(--bg-card)', borderColor: localErrors.sub_goal_id ? '#ef4444' : 'var(--border)', color: 'var(--text-primary)', opacity: formValue.goal_id ? 1 : 0.5 }">
                    <option :value="null">انتخاب گام عملیاتی در نقشه راه (الزامی)...</option>
                    <option v-for="sg in localSubGoals" :key="sg.id" :value="sg.id">{{ sg.title }}</option>
                  </select>
                  <p v-if="localErrors.sub_goal_id" class="text-xs text-red-500 font-bold mt-1.5 flex items-center gap-1 bg-red-500/10 p-2 rounded-xl border border-red-500/30">
                    <AlertCircle class="w-4 h-4" /> {{ localErrors.sub_goal_id }}
                  </p>
                  <p v-else class="text-xs md:text-sm font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">اتصال تسک به فاز مشخصی از نقشه راه (الزامی)</p>
                </div>
              </div>
              
              <!-- اولویت و دسته‌بندی -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="text-sm font-black mb-1.5 flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                    <Flag class="w-4 h-4 text-amber-400" /> اولویت
                  </label>
                  <div class="flex gap-1 bg-black/5 dark:bg-black/20 p-1.5 rounded-xl border-2 border-slate-300 dark:border-white/20">
                    <button 
                      v-for="(label, val) in priorityLabels" 
                      :key="val" 
                      type="button"
                      @click="formValue.priority = Number(val)" 
                      class="flex-1 py-2 rounded-lg text-xs font-black transition" 
                      :style="formValue.priority === Number(val) ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-secondary)' }"
                    >
                      {{ label }}
                    </button>
                  </div>
                  <p class="text-xs font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">درجه اهمیت کار (عادی، مهم، فوری)</p>
                </div>

                <div>
                  <label class="text-sm font-black mb-1.5 flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                    <Tag class="w-4 h-4 text-emerald-400" /> دسته‌بندی
                  </label>
                  <select v-model="formValue.category" class="w-full px-4 py-3 rounded-xl border-2 border-slate-300 dark:border-white/30 text-sm font-bold outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
                    <option value="">عمومی</option>
                    <option v-for="c in categories" :key="c.value || c" :value="c.value || c">{{ c.label || c }}</option>
                  </select>
                  <p class="text-xs font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">حوزه کاری مربوطه (شغلی، شخصی و...)</p>
                </div>
              </div>

            </div>
          </div>

          <!-- بخش ۳: تنظیمات زمان‌بندی، تکرار و وضعیت -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-3xl border-2 border-dashed bg-black/5 dark:bg-white/5" :style="{ borderColor: 'var(--border)' }">
            
            <!-- تاریخ و مدت -->
            <div>
              <label class="text-sm font-black mb-2 flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                <Calendar class="w-4 h-4 text-blue-400" /> تاریخ ثبت و مدت زمان
              </label>
              <DateInputPersian v-model="formValue.register_date" />
              <p class="text-xs font-bold mt-1.5 mb-3" :style="{ color: 'var(--text-secondary)' }">تاریخ شروع یا ثبت کار در سیستم</p>

              <label class="text-xs font-bold block mb-1" :style="{ color: 'var(--text-secondary)' }">مدت زمان برآورد شده (روز)</label>
              <input v-model.number="formValue.duration_days" type="number" min="1" placeholder="مثلاً: ۳" class="w-full px-4 py-2.5 rounded-xl border-2 border-slate-300 dark:border-white/30 text-sm font-bold outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
              <p class="text-xs text-blue-500 font-bold mt-1.5">📅 پیشنهادی مهلت: {{ suggestedDueDate() }}</p>
            </div>

            <!-- تنظیمات تکرار + گزینه برنامه‌ریزی اتوماتیک -->
            <div class="space-y-3">
              <label class="text-sm font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                <RefreshCw class="w-4 h-4 text-amber-400" /> تنظیمات تکرار دوره
              </label>
              <select v-model="formValue.recurrence_type" class="w-full px-4 py-3 rounded-xl border-2 border-slate-300 dark:border-white/30 text-sm font-bold outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
                <option v-for="opt in recurrenceOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
              <p class="text-xs font-bold" :style="{ color: 'var(--text-secondary)' }">بازه تکرار خودکار تسک در برنامه</p>

              <div v-if="formValue.recurrence_type !== 'none'" class="space-y-3 pt-2">
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <input v-model.number="formValue.recurrence_interval" type="number" min="1" placeholder="فاصله (مثلاً ۱)" class="w-full px-3 py-2 rounded-xl border-2 border-slate-300 dark:border-white/30 text-xs font-bold" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
                    <p class="text-xs font-bold mt-1" :style="{ color: 'var(--text-secondary)' }">ضریب تکرار</p>
                  </div>
                  <div>
                    <DateInputPersian v-model="formValue.recurrence_end_date" placeholder="تا تاریخ..." />
                    <p class="text-xs font-bold mt-1" :style="{ color: 'var(--text-secondary)' }">پایان دوره</p>
                  </div>
                </div>

                <!-- 🔄 گزینه جدید: تیک برنامه‌ریزی اتوماتیک دوره‌ای -->
                <div class="p-3.5 rounded-2xl bg-purple-500/10 border-2 border-purple-500/40 mt-2">
                  <label class="flex items-center gap-2 cursor-pointer text-xs font-black text-purple-400 dark:text-purple-300">
                    <input type="checkbox" v-model="formValue.auto_reschedule" class="w-4 h-4 rounded border-white/30 text-purple-600 focus:ring-purple-500" />
                    <span>🔄 برنامه‌ریزی اتوماتیک دوره‌ای</span>
                  </label>
                  <p class="text-xs font-bold mt-1.5 leading-relaxed" :style="{ color: 'var(--text-secondary)' }">
                    با تیک زدن تسک، مهلت آن خودکار برای فردا/دوره بعدی تنظیم می‌شود.
                  </p>
                </div>
              </div>
            </div>

            <!-- وضعیت نهایی و آخرین اقدام -->
            <div class="space-y-3">
              <label class="text-sm font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                <CheckCircle2 class="w-4 h-4 text-emerald-400" /> وضعیت و آخرین اقدام
              </label>
              <select v-model="formValue.status" class="w-full px-4 py-3 rounded-xl border-2 border-slate-300 dark:border-white/30 text-sm font-bold outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
                <option value="not_started">شروع نشده</option>
                <option value="in_progress">در حال انجام</option>
                <option value="completed">تکمیل شده</option>
              </select>
              <p class="text-xs font-bold" :style="{ color: 'var(--text-secondary)' }">مرحله فعلی پیشرفت کار</p>

              <div class="pt-1">
                <label class="text-xs font-bold block mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ آخرین اقدام</label>
                <DateInputPersian v-model="formValue.last_action_date" />
                <p class="text-xs font-bold mt-1.5" :style="{ color: 'var(--text-secondary)' }">آخرین بار چه زمانی روی این کار اقدام کرده‌اید</p>
              </div>
            </div>

          </div>

        </div>

        <!-- Action Buttons -->
        <div class="flex gap-4 mt-6 pt-4 border-t flex-shrink-0" :style="{ borderColor: 'var(--border)' }">
          <button 
            type="button"
            @click="submit" 
            :disabled="isLoading" 
            class="flex-1 py-4 rounded-2xl text-white font-black text-base md:text-lg shadow-xl transition active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2" 
            :style="{ background: 'var(--accent)' }"
          >
            <span>{{ editingTask ? 'ذخیره تغییرات تسک' : 'ثبت و ایجاد تسک' }}</span>
          </button>
          <button 
            type="button"
            @click="close" 
            class="px-8 py-4 rounded-2xl font-bold transition hover:bg-white/10 text-sm" 
            :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }"
          >
            انصراف
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>