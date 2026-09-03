<script setup>
/**
 * WheelDatePicker — iOS-style wheel date picker (با تم پروژه)
 * - 3 columns: day / month / year
 * - Snap to value (CSS scroll-snap)
 * - Center row highlighted (سفید bold)، بقیه کم‌رنگ
 * - خط طلایی بالا و پایین ردیف وسط (هماهنگ با تم پروژه)
 * - پشتیبانی شمسی/میلادی
 */
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import * as jalaali from 'jalaali-js'
import { toShamsiDisplay, toGregorianISO, isGregorianISO } from '@/utils/date'

const props = defineProps({
  modelValue: { type: String, default: '' },          // ISO میلادی yyyy-mm-dd
  defaultType: { type: String, default: 'shamsi' },   // 'shamsi' | 'gregorian'
  minYear: { type: Number, default: null },
  maxYear: { type: Number, default: null },
})
const emit = defineEmits(['update:modelValue', 'change'])

const shamsiMonths = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
const gregMonths = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const toPersianDigits = (s) => String(s).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹')

const ITEM_HEIGHT = 40
const VISIBLE = 5

const isOpen = ref(false)
const pickerType = ref(props.defaultType)

const selectedYear = ref(0)
const selectedMonth = ref(0)
const selectedDay = ref(0)

const yearCol = ref(null)
const monthCol = ref(null)
const dayCol = ref(null)

const today = new Date()
const todayGY = today.getFullYear()
const todayGM = today.getMonth() + 1
const todayGD = today.getDate()
const [todayJY, todayJM, todayJD] = jalaali.toJalaali(todayGY, todayGM, todayGD)

const minGY = props.minYear ?? todayGY - 50
const maxGY = props.maxYear ?? todayGY + 10

const yearList = computed(() => {
  const yrs = []
  for (let y = maxGY; y >= minGY; y--) yrs.push(y)
  return yrs
})
const monthList = computed(() => pickerType.value === 'shamsi' ? shamsiMonths : gregMonths)
const daysInMonth = computed(() => {
  if (pickerType.value === 'shamsi') {
    const m = selectedMonth.value
    if (m <= 6) return 31
    if (m <= 11) return 30
    const jy = selectedYear.value
    return (jy % 33 === 1 || jy % 33 === 5 || jy % 33 === 9) ? 30 : 29
  } else {
    return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
  }
})
const dayList = computed(() => {
  const arr = []
  for (let d = 1; d <= daysInMonth.value; d++) arr.push(d)
  return arr
})

function parseInitial() {
  if (props.modelValue && isGregorianISO(props.modelValue)) {
    const [gy, gm, gd] = props.modelValue.split('-').map(Number)
    if (pickerType.value === 'shamsi') {
      const [jy, jm, jd] = jalaali.toJalaali(gy, gm, gd)
      selectedYear.value = jy
      selectedMonth.value = jm
      selectedDay.value = jd
    } else {
      selectedYear.value = gy
      selectedMonth.value = gm
      selectedDay.value = gd
    }
  } else {
    if (pickerType.value === 'shamsi') {
      selectedYear.value = todayJY
      selectedMonth.value = todayJM
      selectedDay.value = todayJD
    } else {
      selectedYear.value = todayGY
      selectedMonth.value = todayGM
      selectedDay.value = todayGD
    }
  }
}

function open() {
  isOpen.value = true
  parseInitial()
  nextTick(() => {
    scrollToValue(yearCol.value, yearList.value.indexOf(selectedYear.value))
    scrollToValue(monthCol.value, selectedMonth.value - 1)
    scrollToValue(dayCol.value, selectedDay.value - 1)
  })
}
function close() { isOpen.value = false }

function scrollToValue(container, index) {
  if (!container || index < 0) return
  const top = index * ITEM_HEIGHT
  container.scrollTo({ top, behavior: 'auto' })
}

function onScroll(col, list, setter) {
  if (!col) return
  const idx = Math.round(col.scrollTop / ITEM_HEIGHT)
  const clamped = Math.max(0, Math.min(list.length - 1, idx))
  const val = list[clamped]
  if (val !== undefined && val !== null) setter(val)
}

function fmtDay(d) { return pickerType.value === 'shamsi' ? toPersianDigits(d) : d }
function fmtYear(y) { return pickerType.value === 'shamsi' ? toPersianDigits(y) : y }

function confirm() {
  let gy, gm, gd
  if (pickerType.value === 'shamsi') {
    [gy, gm, gd] = jalaali.toGregorian(selectedYear.value, selectedMonth.value, selectedDay.value)
  } else {
    gy = selectedYear.value; gm = selectedMonth.value; gd = selectedDay.value
  }
  const iso = `${gy}-${String(gm).padStart(2, '0')}-${String(gd).padStart(2, '0')}`
  emit('update:modelValue', iso)
  emit('change', iso)
  isOpen.value = false
}

const displayValue = computed(() => {
  if (!props.modelValue || !isGregorianISO(props.modelValue)) return ''
  if (pickerType.value === 'shamsi') {
    return toShamsiDisplay(props.modelValue) || props.modelValue
  }
  return props.modelValue
})

const typeBadge = computed(() => pickerType.value === 'shamsi' ? 'شمسی' : 'میلادی')

watch(() => props.defaultType, (newType) => {
  pickerType.value = newType
  parseInitial()
})

onMounted(() => {
  pickerType.value = props.defaultType
})
</script>

<template>
  <div class="relative w-full">
    <!-- فیلد ورودی: دکمه‌ای که popup رو باز می‌کنه -->
    <button type="button" @click="open"
            class="w-full px-2.5 py-1.5 rounded-lg bg-black/40 border border-white/10 outline-none text-xs text-white text-right flex items-center justify-between gap-2 hover:border-amber-500/50 focus:ring-2 focus:ring-amber-500/50 transition">
      <span v-if="displayValue" class="font-mono truncate" :dir="pickerType === 'gregorian' ? 'ltr' : 'rtl'">
        {{ displayValue }}
      </span>
      <span v-else class="opacity-50">انتخاب تاریخ...</span>
      <span class="text-[9px] px-1.5 py-0.5 rounded font-bold flex-shrink-0"
            :class="pickerType === 'shamsi' ? 'bg-purple-500/30 text-purple-200' : 'bg-amber-500/30 text-amber-200'">
        {{ typeBadge }}
      </span>
    </button>

    <!-- Popup -->
    <Teleport to="body">
      <Transition name="popup">
        <div v-if="isOpen" class="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
             @click.self="close">
          <div class="bg-slate-900/98 border border-white/20 rounded-3xl shadow-2xl shadow-black/60 p-4 w-full max-w-xs"
               style="backface-visibility: hidden;">

            <!-- هدر: تب شمسی/میلادی -->
            <div class="flex items-center justify-center gap-1 p-1 bg-black/40 rounded-xl border border-white/10 mb-3">
              <button type="button" @click="pickerType = 'shamsi'; parseInitial(); nextTick(() => { scrollToValue(yearCol, yearList.indexOf(selectedYear)); scrollToValue(monthCol, selectedMonth - 1); scrollToValue(dayCol, selectedDay - 1) })"
                      class="flex-1 py-1.5 rounded-lg text-[11px] font-bold transition"
                      :style="pickerType === 'shamsi' ? { background: '#9333ea', color: '#fff' } : { color: 'rgba(255,255,255,0.6)' }">شمسی</button>
              <button type="button" @click="pickerType = 'gregorian'; parseInitial(); nextTick(() => { scrollToValue(yearCol, yearList.indexOf(selectedYear)); scrollToValue(monthCol, selectedMonth - 1); scrollToValue(dayCol, selectedDay - 1) })"
                      class="flex-1 py-1.5 rounded-lg text-[11px] font-bold transition"
                      :style="pickerType === 'gregorian' ? { background: '#f59e0b', color: '#000' } : { color: 'rgba(255,255,255,0.6)' }">میلادی</button>
            </div>

            <!-- Wheel containers: روز | ماه | سال -->
            <div class="flex gap-1 bg-black/30 rounded-2xl border border-white/10 p-2 relative overflow-hidden" style="height: 200px;">

              <!-- روز -->
              <div class="flex-1 relative">
                <div class="absolute top-0 left-0 right-0 z-10 flex justify-center pt-1 pointer-events-none">
                  <span class="text-amber-400 text-[10px]">▲</span>
                </div>
                <div class="absolute bottom-0 left-0 right-0 z-10 flex justify-center pb-1 pointer-events-none">
                  <span class="text-amber-400 text-[10px]">▼</span>
                </div>
                <div class="absolute left-0 right-0 border-t-2 border-amber-400 z-[5] pointer-events-none" style="top: 80px;"></div>
                <div class="absolute left-0 right-0 border-b-2 border-amber-400 z-[5] pointer-events-none" style="top: 120px;"></div>
                <div class="absolute left-0 right-0 bg-amber-500/10 z-[4] pointer-events-none" style="top: 80px; height: 40px;"></div>
                <div ref="dayCol"
                     @scroll="onScroll($event.target, dayList, v => selectedDay = v)"
                     class="h-full overflow-y-scroll no-scrollbar"
                     :style="{ scrollSnapType: 'y mandatory', paddingTop: ((VISIBLE-1)/2 * ITEM_HEIGHT) + 'px', paddingBottom: ((VISIBLE-1)/2 * ITEM_HEIGHT) + 'px' }">
                  <div v-for="d in dayList" :key="d"
                       class="flex items-center justify-center snap-center transition-all duration-150"
                       :style="{ height: ITEM_HEIGHT + 'px' }">
                    <span class="text-sm font-bold"
                          :class="d === selectedDay ? 'text-white scale-110' : 'text-white/30'">
                      {{ fmtDay(d) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- ماه -->
              <div class="flex-1 relative">
                <div class="absolute top-0 left-0 right-0 z-10 flex justify-center pt-1 pointer-events-none">
                  <span class="text-amber-400 text-[10px]">▲</span>
                </div>
                <div class="absolute bottom-0 left-0 right-0 z-10 flex justify-center pb-1 pointer-events-none">
                  <span class="text-amber-400 text-[10px]">▼</span>
                </div>
                <div class="absolute left-0 right-0 border-t-2 border-amber-400 z-[5] pointer-events-none" style="top: 80px;"></div>
                <div class="absolute left-0 right-0 border-b-2 border-amber-400 z-[5] pointer-events-none" style="top: 120px;"></div>
                <div class="absolute left-0 right-0 bg-amber-500/10 z-[4] pointer-events-none" style="top: 80px; height: 40px;"></div>
                <div ref="monthCol"
                     @scroll="onScroll($event.target, monthList, v => selectedMonth = v + 1)"
                     class="h-full overflow-y-scroll no-scrollbar"
                     :style="{ scrollSnapType: 'y mandatory', paddingTop: ((VISIBLE-1)/2 * ITEM_HEIGHT) + 'px', paddingBottom: ((VISIBLE-1)/2 * ITEM_HEIGHT) + 'px' }">
                  <div v-for="(m, i) in monthList" :key="i"
                       class="flex items-center justify-center snap-center transition-all duration-150"
                       :style="{ height: ITEM_HEIGHT + 'px' }">
                    <span class="text-sm font-bold"
                          :class="(i + 1) === selectedMonth ? 'text-white scale-110' : 'text-white/30'">
                      {{ m }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- سال -->
              <div class="flex-1 relative">
                <div class="absolute top-0 left-0 right-0 z-10 flex justify-center pt-1 pointer-events-none">
                  <span class="text-amber-400 text-[10px]">▲</span>
                </div>
                <div class="absolute bottom-0 left-0 right-0 z-10 flex justify-center pb-1 pointer-events-none">
                  <span class="text-amber-400 text-[10px]">▼</span>
                </div>
                <div class="absolute left-0 right-0 border-t-2 border-amber-400 z-[5] pointer-events-none" style="top: 80px;"></div>
                <div class="absolute left-0 right-0 border-b-2 border-amber-400 z-[5] pointer-events-none" style="top: 120px;"></div>
                <div class="absolute left-0 right-0 bg-amber-500/10 z-[4] pointer-events-none" style="top: 80px; height: 40px;"></div>
                <div ref="yearCol"
                     @scroll="onScroll($event.target, yearList, v => selectedYear = v)"
                     class="h-full overflow-y-scroll no-scrollbar"
                     :style="{ scrollSnapType: 'y mandatory', paddingTop: ((VISIBLE-1)/2 * ITEM_HEIGHT) + 'px', paddingBottom: ((VISIBLE-1)/2 * ITEM_HEIGHT) + 'px' }">
                  <div v-for="y in yearList" :key="y"
                       class="flex items-center justify-center snap-center transition-all duration-150"
                       :style="{ height: ITEM_HEIGHT + 'px' }">
                    <span class="text-sm font-bold"
                          :class="y === selectedYear ? 'text-white scale-110' : 'text-white/30'">
                      {{ fmtYear(y) }}
                    </span>
                  </div>
                </div>
              </div>

            </div>

            <!-- دکمه‌های تأیید/انصراف -->
            <div class="flex gap-2 mt-3">
              <button type="button" @click="confirm"
                      class="flex-1 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-900 font-black text-xs transition">
                تأیید
              </button>
              <button type="button" @click="close"
                      class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs transition">
                انصراف
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.popup-enter-active, .popup-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.popup-enter-from, .popup-leave-to { opacity: 0; transform: scale(0.95); }
</style>
