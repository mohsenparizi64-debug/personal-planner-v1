<script setup>
import { ref, watch, computed } from 'vue'
import { Calendar } from 'lucide-vue-next'
import { toShamsiDisplay, toGregorianISO, detectInputType } from '../utils/date'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'تاریخ' },
})
const emit = defineEmits(['update:modelValue'])

// حالت نمایش: shamsi | gregorian
const mode = ref('shamsi')
const text = ref('')
const error = ref('')

// وقتی مقدار بیرون تغییر کرد، نمایش را همگام کن
watch(() => props.modelValue, (val) => {
  if (!val) { text.value = ''; return }
  if (mode.value === 'shamsi') text.value = toShamsiDisplay(val) || val
  else text.value = val
}, { immediate: true })

const hint = computed(() => {
  if (!text.value) return ''
  const t = detectInputType(text.value)
  if (t === 'shamsi') return 'شمسی'
  if (t === 'gregorian') return 'میلادی'
  return 'نامعتبر'
})

function toggleMode() {
  mode.value = mode.value === 'shamsi' ? 'gregorian' : 'shamsi'
  // تبدیل نمایش فعلی به حالت جدید
  if (props.modelValue) {
    text.value = mode.value === 'shamsi' ? (toShamsiDisplay(props.modelValue) || text.value) : props.modelValue
  }
}

function onInput(e) {
  const v = e.target.value
  text.value = v
  error.value = ''
  if (!v.trim()) { emit('update:modelValue', ''); return }

  const greg = toGregorianISO(v)
  if (greg) {
    emit('update:modelValue', greg)
    error.value = ''
  } else {
    // هنوز ناقص است یا نامعتبر
    error.value = 'فرمت نادرست — نمونه: ۱۴۰۳/۰۵/۱۵ یا 2024-08-05'
  }
}

function onBlur() {
  // اگر نیمه‌کاره بود، به مقدار قبل برگرد
  if (error.value && props.modelValue) {
    text.value = mode.value === 'shamsi' ? (toShamsiDisplay(props.modelValue) || props.modelValue) : props.modelValue
    error.value = ''
  }
}
</script>

<template>
  <div>
    <div class="relative">
      <Calendar class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" :style="{ color: 'var(--text-secondary)' }" />
      <input
        :value="text"
        @input="onInput"
        @blur="onBlur"
        :placeholder="placeholder"
        class="w-full px-9 py-2.5 rounded-lg pr-9"
        :style="{ background: 'var(--bg-primary)', border: error ? '2px solid #ef4444' : '1px solid var(--border)', color: 'var(--text-primary)' }"
      />
      <button
        type="button"
        @click="toggleMode"
        class="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-bold px-2 py-1 rounded-md transition"
        :style="{ background: 'var(--bg-hover)', color: 'var(--accent)' }"
      >
        {{ mode === 'shamsi' ? 'شمسی' : 'میلادی' }}
      </button>
    </div>
    <div class="flex items-center justify-between mt-1">
      <p v-if="error" class="text-red-400 text-xs">{{ error }}</p>
      <span v-else-if="hint" class="text-xs" :style="{ color: 'var(--text-secondary)' }">{{ hint }}</span>
    </div>
  </div>
</template>