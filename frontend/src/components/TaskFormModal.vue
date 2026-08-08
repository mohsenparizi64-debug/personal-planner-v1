<script setup>
import { computed } from 'vue'
import { X, AlertCircle } from 'lucide-vue-next'
import DateInputPersian from './DateInputPersian.vue'  // کمپوننت تاریخ هوشمند
import { toShamsiDisplay, toGregorianISO } from '../utils/date'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  form: { type: Object, required: true },
  validationErrors: { type: Object, default: () => ({}) },
  categories: { type: Array, default: () => [] },
  goals: { type: Array, default: () => [] },
  subGoals: { type: Array, default: () => [] },
  editingTask: { type: Object, default: null },
  isLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'update:form', 'save', 'goal-change'])

const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'اضطراری' }
const statusLabels = { not_started: 'شروع نشده', in_progress: 'در حال انجام', completed: 'تکمیل', on_hold: 'متوقف', cancelled: 'لغو شده' }

const formValue = computed({
  get: () => props.form,
  set: (value) => emit('update:form', value),
})

const validationErrors = computed(() => props.validationErrors)

// محاسبه تاریخ پیشنهادی به شکل میلادی
const suggestedDueDateGreg = () => {
  const f = formValue.value
  if (f.recurrence_type && f.recurrence_type !== 'none' && f.last_action_date) {
    const last = new Date(f.last_action_date)
    const days = f.recurrence_type === 'daily' ? f.recurrence_interval
      : f.recurrence_type === 'weekly' ? f.recurrence_interval * 7
      : f.recurrence_type === 'monthly' ? f.recurrence_interval * 30
      : f.recurrence_interval * 365
    last.setDate(last.getDate() + days)
    return last.toISOString().split('T')[0]
  } else if (f.duration_days && f.register_date) {
    const reg = new Date(f.register_date)
    reg.setDate(reg.getDate() + Number(f.duration_days))
    return reg.toISOString().split('T')[0]
  }
  return null
}

// نمایش به شمسی برای کاربر
const suggestedDueDate = () => {
  const g = suggestedDueDateGreg()
  return g ? toShamsiDisplay(g) : '--'
}

const close = () => emit('update:modelValue', false)
const submit = () => emit('save')
const onGoalChange = () => emit('goal-change')
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-[500] flex items-start justify-center p-4 pt-20 pb-20 bg-black/60 backdrop-blur-sm overflow-y-auto" @click.self="close">
    <div class="w-full max-w-2xl rounded-2xl p-6 relative z-[501]" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingTask ? 'ویرایش تسک' : 'تسک جدید' }}</h2>
        <button @click="close" :style="{ color: 'var(--text-secondary)' }"><X class="w-6 h-6" /></button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm mb-1" :style="{ color: validationErrors.title ? '#ef4444' : 'var(--text-secondary)' }">عنوان تسک *</label>
          <input v-model="formValue.title" placeholder="عنوان تسک" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: validationErrors.title ? '2px solid #ef4444' : '1px solid var(--border)', color: 'var(--text-primary)' }" />
          <p v-if="validationErrors.title" class="text-red-400 text-xs mt-1 flex items-center gap-1"><AlertCircle class="w-3 h-3" /> {{ validationErrors.title }}</p>
        </div>

        <div>
          <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">توضیحات</label>
          <textarea v-model="formValue.description" rows="2" placeholder="توضیحات" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت</label>
            <DateInputPersian v-model="formValue.register_date" placeholder="تاریخ ثبت" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: validationErrors.duration_days ? '#ef4444' : 'var(--text-secondary)' }">مدت زمان (روز)</label>
            <input v-model.number="formValue.duration_days" type="number" min="0" placeholder="مثلاً ۷" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: validationErrors.duration_days ? '2px solid #ef4444' : '1px solid var(--border)', color: 'var(--text-primary)' }" />
            <p v-if="validationErrors.duration_days" class="text-red-400 text-xs mt-1 flex items-center gap-1"><AlertCircle class="w-3 h-3" /> {{ validationErrors.duration_days }}</p>
            <p class="text-xs mt-1" :style="{ color: 'var(--accent)' }">📅 تاریخ پیشنهادی: {{ suggestedDueDate() || '--' }}</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">دسته‌بندی</label>
            <select v-model="formValue.category" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="">انتخاب کنید...</option>
              <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">اهمیت</label>
            <div class="flex gap-2">
              <button v-for="(label, val) in priorityLabels" :key="val" @click="formValue.priority = Number(val)" class="flex-1 py-2.5 rounded-lg text-sm font-semibold transition" :style="formValue.priority === Number(val) ? { background: val === 2 ? '#ef4444' : val === 1 ? '#f97316' : '#6b7280', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">{{ label }}</button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">هدف کلان</label>
            <select v-model="formValue.goal_id" @change="onGoalChange" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option :value="null">بدون هدف</option>
              <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">زیرهدف</label>
            <select v-model="formValue.sub_goal_id" :disabled="!formValue.goal_id" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)', opacity: formValue.goal_id ? 1 : 0.5 }">
              <option :value="null">بدون زیرهدف</option>
              <option v-for="sg in subGoals" :key="sg.id" :value="sg.id">{{ sg.title }}</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">وضعیت</label>
            <select v-model="formValue.status" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option v-for="(label, key) in statusLabels" :key="key" :value="key">{{ label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ آخرین اقدام</label>
            <DateInputPersian v-model="formValue.last_action_date" placeholder="تاریخ آخرین اقدام" />
          </div>
        </div>

        <div>
          <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">دوره تکرار</label>
          <div class="grid grid-cols-3 gap-2">
            <select v-model="formValue.recurrence_type" class="px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="none">بدون تکرار</option>
              <option value="daily">روزانه</option>
              <option value="weekly">هفتگی</option>
              <option value="monthly">ماهانه</option>
              <option value="yearly">سالیانه</option>
            </select>
            <div v-if="formValue.recurrence_type !== 'none'">
              <label class="block text-xs mb-1" :style="{ color: validationErrors.recurrence_interval ? '#ef4444' : 'var(--text-secondary)' }">هر چند؟</label>
              <input v-model.number="formValue.recurrence_interval" type="number" min="1" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: validationErrors.recurrence_interval ? '2px solid #ef4444' : '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
            <div v-if="formValue.recurrence_type !== 'none'">
              <label class="block text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">پایان تکرار</label>
              <DateInputPersian v-model="formValue.recurrence_end_date" placeholder="پایان تکرار" />
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-3 mt-6">
        <button @click="submit" :disabled="isLoading" class="flex-1 py-3 rounded-xl text-white font-semibold transition disabled:opacity-50" :style="{ background: 'var(--accent)' }">{{ editingTask ? 'بروزرسانی' : 'ایجاد تسک' }}</button>
        <button @click="close" class="px-6 py-3 rounded-xl transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
      </div>
    </div>
  </div>
</template>