<script setup>
import { ref, computed, watch } from 'vue'
import { X, AlertCircle, Calendar, RefreshCw, Star, Tag, AlignLeft } from 'lucide-vue-next'
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

// لود خودکار گام‌ها با تغییر هدف
watch(() => props.form.goal_id, async (newId) => {
  if (newId) {
    try {
      const res = await api.get(`/roadmap/goal/${newId}/subgoals`);
      localSubGoals.value = res.data;
    } catch (e) { localSubGoals.value = []; }
  } else { localSubGoals.value = []; }
}, { immediate: true });

const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'فوری' }
const recurrenceOptions = [
  { value: 'none', label: 'بدون تکرار' },
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
const submit = () => emit('save')
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md overflow-y-auto" @click.self="close">
    <div class="w-full max-w-3xl rounded-[2rem] p-8 shadow-2xl animate-in zoom-in duration-200" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <div class="p-3 rounded-2xl bg-blue-500/10 text-blue-500"><Plus v-if="!editingTask" /><Edit3 v-else /></div>
          <h2 class="text-2xl font-black" :style="{ color: 'var(--text-primary)' }">{{ editingTask ? 'ویرایش تسک' : 'تعریف تسک جدید' }}</h2>
        </div>
        <button @click="close" class="p-2 hover:bg-white/10 rounded-full transition" :style="{ color: 'var(--text-secondary)' }"><X /></button>
      </div>

      <div class="space-y-6 text-right" dir="rtl">
        <!-- عنوان و توضیحات -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div>
              <label class="text-xs font-bold mb-2 block opacity-60 flex items-center gap-2"><Tag class="w-3 h-3" /> عنوان تسک *</label>
              <input v-model="formValue.title" placeholder="چه کاری باید انجام شود؟" class="w-full px-4 py-3 rounded-xl border outline-none focus:ring-2" :style="{ background: 'var(--bg-primary)', borderColor: validationErrors.title ? '#ef4444' : 'var(--border)', color: 'var(--text-primary)', '--tw-ring-color': 'var(--accent)' }" />
            </div>
            <div>
              <label class="text-xs font-bold mb-2 block opacity-60 flex items-center gap-2"><AlignLeft class="w-3 h-3" /> توضیحات</label>
              <textarea v-model="formValue.description" rows="4" placeholder="جزئیات بیشتر..." class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }"></textarea>
            </div>
          </div>

          <div class="space-y-4">
            <!-- هدف و گام -->
            <div class="p-5 rounded-2xl bg-black/5 space-y-4">
              <div>
                <label class="text-xs font-bold mb-2 block opacity-60">متصل به هدف کلان</label>
                <select v-model="formValue.goal_id" @change="formValue.sub_goal_id = null" class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
                  <option :value="null">بدون هدف (تسک عمومی)</option>
                  <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-bold mb-2 block opacity-60">متصل به گام (زیرهدف)</label>
                <select v-model="formValue.sub_goal_id" :disabled="!formValue.goal_id" class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)', opacity: formValue.goal_id ? 1 : 0.5 }">
                  <option :value="null">انتخاب گام عملیاتی...</option>
                  <option v-for="sg in localSubGoals" :key="sg.id" :value="sg.id">{{ sg.title }}</option>
                </select>
              </div>
            </div>
            
            <!-- اهمیت و دسته‌بندی -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-xs font-bold mb-2 block opacity-60">اولویت</label>
                <div class="flex gap-1 bg-black/10 p-1 rounded-xl">
                  <button v-for="(label, val) in priorityLabels" :key="val" @click="formValue.priority = Number(val)" class="flex-1 py-2 rounded-lg text-[10px] font-bold transition" :style="formValue.priority === Number(val) ? { background: 'var(--accent)', color: '#fff' } : { color: 'var(--text-secondary)' }">{{ label }}</button>
                </div>
              </div>
              <div>
                <label class="text-xs font-bold mb-2 block opacity-60">دسته‌بندی</label>
                <select v-model="formValue.category" class="w-full px-4 py-2.5 rounded-xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
                  <option value="">عمومی</option>
                  <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- تاریخ‌ها و تکرار -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-3xl border-2 border-dashed" :style="{ borderColor: 'var(--border)' }">
          <div>
            <label class="text-xs font-bold mb-2 block opacity-60 flex items-center gap-2"><Calendar class="w-3 h-3" /> تاریخ ثبت / مهلت</label>
            <DateInputPersian v-model="formValue.register_date" />
            <div class="mt-4">
              <label class="text-[10px] font-bold opacity-50 block mb-1">مدت زمان (روز)</label>
              <input v-model.number="formValue.duration_days" type="number" class="w-full px-4 py-2 rounded-xl border" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
              <p class="text-[10px] mt-1 text-blue-400">📅 پیشنهاد: {{ suggestedDueDate() }}</p>
            </div>
          </div>

          <div class="space-y-4">
            <label class="text-xs font-bold mb-2 block opacity-60 flex items-center gap-2"><RefreshCw class="w-3 h-3" /> تنظیمات تکرار</label>
            <select v-model="formValue.recurrence_type" class="w-full px-4 py-3 rounded-xl border" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
              <option v-for="opt in recurrenceOptions" :key="val" :value="opt.value">{{ opt.label }}</option>
            </select>
            <div v-if="formValue.recurrence_type !== 'none'" class="grid grid-cols-2 gap-2">
              <input v-model.number="formValue.recurrence_interval" type="number" placeholder="فاصله" class="w-full px-4 py-2 rounded-xl border" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
              <DateInputPersian v-model="formValue.recurrence_end_date" placeholder="تا تاریخ" />
            </div>
          </div>

          <div>
            <label class="text-xs font-bold mb-2 block opacity-60 flex items-center gap-2"><Star class="w-3 h-3" /> وضعیت نهایی</label>
            <select v-model="formValue.status" class="w-full px-4 py-3 rounded-xl border" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }">
              <option value="not_started">شروع نشده</option>
              <option value="in_progress">در حال انجام</option>
              <option value="completed">تکمیل شده</option>
            </select>
            <div class="mt-4">
               <label class="text-[10px] font-bold opacity-50 block mb-1">آخرین اقدام</label>
               <DateInputPersian v-model="formValue.last_action_date" />
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-4 mt-10">
        <button @click="submit" :disabled="isLoading" class="flex-1 py-4 rounded-2xl text-white font-black text-lg shadow-xl transition active:scale-95 disabled:opacity-50" :style="{ background: 'var(--accent)' }">
          {{ editingTask ? 'ذخیره تغییرات تسک' : 'ثبت و ایجاد تسک' }}
        </button>
        <button @click="close" class="px-10 py-4 rounded-2xl font-bold opacity-70 transition hover:bg-white/5" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
      </div>
    </div>
  </div>
</template>