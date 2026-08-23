<script setup>
import { DatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const props = defineProps({ modelValue: { type: String, default: '' } })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <DatePicker
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    locale="fa"
    format="yyyy-MM-dd"
    :enable-time-picker="false"
    auto-apply
    text-input
  />
</template>