<script setup>
import { ref, watch, computed } from 'vue'
import { Calendar, ChevronRight, ChevronLeft, X, RotateCcw } from 'lucide-vue-next'
import { toShamsiDisplay, toGregorianISO, detectInputType } from '../utils/date'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'تاریخ' },
})
const emit = defineEmits(['update:modelValue'])

const mode = ref('shamsi') // shamsi | gregorian
const text = ref('')
const error = ref('')
const showCalendarPicker = ref(false)

// وضعیت نمای تقویم: 'days' (روزها) | 'months' (انتخاب ماه) | 'years' (انتخاب سال)
const calendarViewMode = ref('days')

// وضعیت تقویم پویا
const currentJalaliYear = ref(1403)
const currentJalaliMonth = ref(12) // ۱ تا ۱۲

const jalaliMonths = [
  'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
]

const weekDays = [
  { name: 'ش', isWeekend: false },
  { name: 'ی', isWeekend: false },
  { name: 'د', isWeekend: false },
  { name: 'س', isWeekend: false },
  { name: 'چ', isWeekend: false },
  { name: 'پ', isWeekend: true },  // پنج‌شنبه قرمز
  { name: 'ج', isWeekend: true }   // جمعه قرمز
]

// بازه سال‌های نمای شبکه‌ای (۱۲ سال متناظر با سال فعلی)
const decadeStartYear = ref(1398)

const decadeYears = computed(() => {
  const years = []
  for (let i = 0; i < 12; i++) {
    years.push(decadeStartYear.value + i)
  }
  return years
})

// الگوریتم تبدیل نجومی تاریخ شمسی به میلادی جهت محاسبه روز دقیق هفته
function jalaliToGregorian(jy, jm, jd) {
  jy = Number(jy); jm = Number(jm); jd = Number(jd);
  var jy1 = jy - 979;
  var j_day_no = 365 * jy1 + Math.floor(jy1 / 33) * 8 + Math.floor((jy1 % 33 + 3) / 4);
  for (var i = 0; i < jm - 1; ++i) {
    j_day_no += (i < 6) ? 31 : 30;
  }
  j_day_no += jd - 1;

  var g_day_no = j_day_no + 79,
      gy = 1600 + 400 * Math.floor(g_day_no / 146097);
  g_day_no = g_day_no % 146097;

  var leap = true;
  if (g_day_no >= 36525) {
    g_day_no--;
    gy += 100 * Math.floor(g_day_no / 36524);
    g_day_no = g_day_no % 36524;
    if (g_day_no >= 365) g_day_no++;
    else leap = false;
  }

  gy += 4 * Math.floor(g_day_no / 1461);
  g_day_no %= 1461;

  if (g_day_no >= 366) {
    leap = false;
    g_day_no--;
    gy += Math.floor(g_day_no / 365);
    g_day_no %= 365;
  }

  for (var i = 0; g_day_no >= ((i === 1 && leap) ? 29 : [31,28,31,30,31,30,31,31,30,31,30,31][i]); i++) {
    g_day_no -= (i === 1 && leap) ? 29 : [31,28,31,30,31,30,31,31,30,31,30,31][i];
  }
  return new Date(gy, i, g_day_no + 1);
}

// بررسی سال کبیسه شمسی
function isJalaliLeapYear(jy) {
  return ((((jy - (jy > 0 ? 474 : 473)) % 2820) + 474 + 38) * 682) % 2816 < 682
}

// تعداد کل روزهای ماه جاری
const totalDaysInMonth = computed(() => {
  const m = currentJalaliMonth.value
  if (m <= 6) return 31
  if (m <= 11) return 30
  return isJalaliLeapYear(currentJalaliYear.value) ? 30 : 29
})

// محاسبه روز هفته برای روز اول ماه (۰=شنبه، ۱=یکشنبه، ...، ۶=جمعه)
const firstDayWeekdayIndex = computed(() => {
  const gDate = jalaliToGregorian(currentJalaliYear.value, currentJalaliMonth.value, 1)
  const day = gDate.getDay() // 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
  return (day + 1) % 7
})

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
    error.value = 'فرمت نادرست — نمونه: ۱۴۰۳/۰۵/۱۵'
  }
}

function selectDay(dayNum) {
  const m = String(currentJalaliMonth.value).padStart(2, '0')
  const d = String(dayNum).padStart(2, '0')
  const shamsiStr = `${currentJalaliYear.value}/${m}/${d}`
  const greg = toGregorianISO(shamsiStr)
  if (greg) {
    emit('update:modelValue', greg)
    text.value = shamsiStr
    showCalendarPicker.value = false
    calendarViewMode.value = 'days'
    error.value = ''
  }
}

function selectMonth(mIdx) {
  currentJalaliMonth.value = mIdx + 1
  calendarViewMode.value = 'days'
}

function selectYear(y) {
  currentJalaliYear.value = y
  calendarViewMode.value = 'days'
}

function selectToday() {
  const today = new Date().toISOString().split('T')[0]
  emit('update:modelValue', today)
  text.value = toShamsiDisplay(today)
  showCalendarPicker.value = false
  calendarViewMode.value = 'days'
}

function prevMonth() {
  if (currentJalaliMonth.value === 1) {
    currentJalaliMonth.value = 12
    currentJalaliYear.value--
  } else {
    currentJalaliMonth.value--
  }
}

function nextMonth() {
  if (currentJalaliMonth.value === 12) {
    currentJalaliMonth.value = 1
    currentJalaliYear.value++
  } else {
    currentJalaliMonth.value++
  }
}

function openMonthSelector() {
  calendarViewMode.value = 'months'
}

function openYearSelector() {
  decadeStartYear.value = currentJalaliYear.value - 4
  calendarViewMode.value = 'years'
}

function prevDecade() {
  decadeStartYear.value -= 12
}

function nextDecade() {
  decadeStartYear.value += 12
}
</script>

<template>
  <div class="relative">
    <div class="relative">
      <button 
        type="button" 
        @click="showCalendarPicker = !showCalendarPicker; calendarViewMode = 'days'"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-purple-400 hover:text-white transition"
        title="فتح تقویم ماهانه"
      >
        <Calendar class="w-4 h-4" />
      </button>

      <input
        :value="text"
        @input="onInput"
        :placeholder="placeholder"
        class="w-full px-9 py-2.5 rounded-xl text-xs md:text-sm font-bold pr-9 outline-none"
        :style="{ background: 'var(--bg-primary)', border: error ? '2px solid #ef4444' : '1px solid var(--border)', color: 'var(--text-primary)' }"
      />

      <button
        type="button"
        @click="toggleMode"
        class="absolute left-2 top-1/2 -translate-y-1/2 text-[10px] font-bold px-2 py-1 rounded-md transition border border-white/10"
        :style="{ background: 'var(--bg-hover)', color: 'var(--accent)' }"
      >
        {{ mode === 'shamsi' ? 'شمسی' : 'میلادی' }}
      </button>
    </div>

    <div class="flex items-center justify-between mt-1">
      <p v-if="error" class="text-red-400 text-[10px] font-bold">{{ error }}</p>
      <span v-else-if="hint" class="text-[10px] opacity-70" :style="{ color: 'var(--text-secondary)' }">{{ hint }}</span>
    </div>

    <!-- 🗓️ پاپ‌آور تقویم ماهانه شمسی با دکمه‌های سوئیچ شبکه‌ای سال و ماه (Grid Switcher) -->
    <div v-if="showCalendarPicker" class="absolute right-0 top-12 z-[10000] w-72 p-4 rounded-3xl glass-card border-2 border-purple-500/60 shadow-2xl space-y-3 bg-slate-900 text-white animate-in zoom-in-95 duration-200">
      
      <!-- ۱. هدر اصلی تقویم شامل دکمه‌های انتخابی درخشان سال و ماه + بستن X -->
      <div class="flex items-center justify-between border-b border-white/10 pb-2">
        
        <!-- دکمه‌های جابجایی ماه -->
        <div v-if="calendarViewMode === 'days'" class="flex items-center gap-1">
          <button type="button" @click="prevMonth" class="p-1 hover:bg-white/10 rounded-lg" title="ماه قبل"><ChevronRight class="w-4 h-4 text-purple-300" /></button>
          <button type="button" @click="nextMonth" class="p-1 hover:bg-white/10 rounded-lg" title="ماه بعد"><ChevronLeft class="w-4 h-4 text-purple-300" /></button>
        </div>

        <div v-else-if="calendarViewMode === 'years'" class="flex items-center gap-1">
          <button type="button" @click="prevDecade" class="p-1 hover:bg-white/10 rounded-lg" title="۱۲ سال قبل"><ChevronRight class="w-4 h-4 text-amber-300" /></button>
          <button type="button" @click="nextDecade" class="p-1 hover:bg-white/10 rounded-lg" title="۱۲ سال بعد"><ChevronLeft class="w-4 h-4 text-amber-300" /></button>
        </div>

        <div v-else></div>

        <!-- دکمه‌های درخشان تعویض سریع ماه و سال -->
        <div class="flex items-center gap-1">
          <button 
            type="button" 
            @click="openMonthSelector"
            class="px-2.5 py-1 rounded-xl bg-purple-600/30 hover:bg-purple-600 border border-purple-500/40 text-xs font-black text-amber-300 transition"
          >
            {{ jalaliMonths[currentJalaliMonth - 1] }}
          </button>

          <button 
            type="button" 
            @click="openYearSelector"
            class="px-2.5 py-1 rounded-xl bg-purple-600/30 hover:bg-purple-600 border border-purple-500/40 text-xs font-black text-amber-300 transition"
          >
            {{ currentJalaliYear }}
          </button>
        </div>

        <!-- دکمه بستن X -->
        <button type="button" @click="showCalendarPicker = false" class="p-1 text-gray-400 hover:text-white rounded-lg" title="بستن تقویم">
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- ---------------------------------------------------- -->
      <!-- حالت ۱: شبکه روزهای واقعی ماه (Default View) -->
      <!-- ---------------------------------------------------- -->
      <div v-if="calendarViewMode === 'days'" class="space-y-3">
        <!-- ایام هفته با هایلایت قرمز پنج‌شنبه (پ) و جمعه (ج) -->
        <div class="grid grid-cols-7 gap-1 text-center text-xs font-black pt-1">
          <span 
            v-for="d in weekDays" 
            :key="d.name" 
            :class="d.isWeekend ? 'text-red-400 font-black' : 'text-gray-300'"
          >
            {{ d.name }}
          </span>
        </div>

        <!-- شبکه روزهای واقعی ماه با پرکننده خالی روز اول -->
        <div class="grid grid-cols-7 gap-1 text-center text-xs">
          <div v-for="pad in firstDayWeekdayIndex" :key="'pad-' + pad" class="p-1.5"></div>

          <button 
            v-for="day in totalDaysInMonth" 
            :key="day"
            type="button"
            @click="selectDay(day)"
            class="p-1.5 rounded-xl font-bold transition hover:bg-purple-600 hover:text-white"
            :class="[
              ((firstDayWeekdayIndex + day - 1) % 7 >= 5) ? 'text-red-400 bg-red-500/10 border border-red-500/20' : 'text-gray-200 bg-white/5'
            ]"
          >
            {{ day }}
          </button>
        </div>
      </div>

      <!-- ---------------------------------------------------- -->
      <!-- حالت ۲: شبکه ۱۲ تایی انتخاب ماه (3x4 Month Grid) -->
      <!-- ---------------------------------------------------- -->
      <div v-else-if="calendarViewMode === 'months'" class="space-y-2">
        <p class="text-[10px] font-bold text-gray-400 text-center mb-1">ماه مورد نظر را انتخاب کنید:</p>
        <div class="grid grid-cols-3 gap-2">
          <button 
            v-for="(mName, idx) in jalaliMonths" 
            :key="idx"
            type="button"
            @click="selectMonth(idx)"
            class="py-2.5 px-1 rounded-xl text-xs font-bold transition border"
            :class="currentJalaliMonth === (idx + 1) ? 'bg-purple-600 text-white border-purple-400 font-black shadow-lg' : 'bg-white/5 hover:bg-white/10 text-gray-200 border-white/10'"
          >
            {{ mName }}
          </button>
        </div>
      </div>

      <!-- ---------------------------------------------------- -->
      <!-- حالت ۳: شبکه ۱۲ تایی انتخاب سال (3x4 Year Grid) -->
      <!-- ---------------------------------------------------- -->
      <div v-else-if="calendarViewMode === 'years'" class="space-y-2">
        <p class="text-[10px] font-bold text-gray-400 text-center mb-1">سال مورد نظر را انتخاب کنید (بازه {{ decadeStartYear }} تا {{ decadeStartYear + 11 }}):</p>
        <div class="grid grid-cols-3 gap-2">
          <button 
            v-for="y in decadeYears" 
            :key="y"
            type="button"
            @click="selectYear(y)"
            class="py-2.5 px-1 rounded-xl text-xs font-bold transition border"
            :class="currentJalaliYear === y ? 'bg-purple-600 text-white border-purple-400 font-black shadow-lg' : 'bg-white/5 hover:bg-white/10 text-gray-200 border-white/10'"
          >
            {{ y }}
          </button>
        </div>
      </div>

      <!-- دکمه‌های پایینی پاپ‌آور -->
      <div class="pt-2 border-t border-white/10 flex items-center gap-2">
        <button type="button" @click="selectToday" class="flex-1 py-1.5 bg-purple-600/30 hover:bg-purple-600 text-purple-200 hover:text-white text-[11px] font-bold rounded-xl border border-purple-500/30 transition">
          انتخاب امروز
        </button>

        <button 
          v-if="calendarViewMode !== 'days'" 
          type="button" 
          @click="calendarViewMode = 'days'" 
          class="px-3 py-1.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-[11px] font-bold rounded-xl border border-amber-500/30 transition flex items-center gap-1"
        >
          <RotateCcw class="w-3.5 h-3.5" /> بازگشت
        </button>

        <button type="button" @click="showCalendarPicker = false" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-gray-300 text-[11px] font-bold rounded-xl transition">
          بستن
        </button>
      </div>

    </div>
  </div>
</template>