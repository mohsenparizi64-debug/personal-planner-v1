<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import {
  ChevronRight, ChevronLeft, Calendar as CalendarIcon,
  Clock, AlertTriangle, Check, ArrowRightLeft, Sun, Globe
} from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import WheelDatePicker from '@/components/WheelDatePicker.vue'
import { toGregorianISO, toShamsiDisplay, isGregorianISO } from '@/utils/date'

const themeStore = useThemeStore()

// --- الگوریتم‌های دقیق تبدیل تاریخ جلالی به میلادی و بالعکس ---
function g2j(gy, gm, gd) {
  var g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  var jy = (gy <= 1600) ? 0 : 979;
  gy -= (gy <= 1600) ? 621 : 1600;
  var gy2 = (gm > 2) ? (gy + 1) : gy;
  var days = (365 * gy) + (Math.floor((gy2 + 3) / 4)) - (Math.floor((gy2 + 99) / 100)) + (Math.floor((gy2 + 399) / 400)) - 80 + gd + g_d_m[gm - 1];
  jy += 33 * (Math.floor(days / 12053));
  days %= 12053;
  jy += 4 * (Math.floor(days / 1461));
  days %= 1461;
  jy += Math.floor((days - 1) / 365);
  if (days > 0) days = (days - 1) % 365;
  var jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
  var jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
  return [jy, jm, jd];
}

function j2g(jy, jm, jd) {
  var gy = (jy <= 979) ? 621 : 1600;
  jy -= (jy <= 979) ? 0 : 979;
  var days = (365 * jy) + ((Math.floor(jy / 33)) * 8) + (Math.floor(((jy % 33) + 3) / 4)) + 78 + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
  gy += 400 * (Math.floor(days / 146097));
  days %= 146097;
  if (days > 36524) {
    gy += 100 * (Math.floor(--days / 36524));
    days %= 36524;
    if (days >= 365) days++;
  }
  gy += 4 * (Math.floor(days / 1461));
  days %= 1461;
  gy += Math.floor((days - 1) / 365);
  if (days > 0) days = (days - 1) % 365;
  var gd = days + 1;
  var sal_a = [0, 31, ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  var gm;
  for (gm = 0; gm < 13; gm++) {
    var v = sal_a[gm];
    if (gd <= v) break;
    gd -= v;
  }
  return [gy, gm, gd];
}

// اسامی ماه‌ها و روزها
const shamsiMonths = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
const englishMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const weekDays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']

// تاریخ امروز واقعی سیستم
const realNow = new Date()
const [realJY, realJM, realJD] = g2j(realNow.getFullYear(), realNow.getMonth() + 1, realNow.getDate())

const currentYear = ref(realJY)
const currentMonth = ref(realJM)
const selectedDayNum = ref(realJD)

// داده‌های کارها
const tasks = ref([])
const overdueTasks = ref([])
const isLoading = ref(false)

// وضعیت آپلود عکس شخصی و پس‌زمینه
const customBgUrl = ref(localStorage.getItem('planner_calendar_custom_bg') || '')
const showUploadModal = ref(false)
const uploadError = ref('')

// عکس پیش‌فرض پیشرفته (رودخانه بزرگ در کوهستان سرسبز)
const defaultRiverBg = 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1920&q=80'

// عکس‌های ۴ فصل (در صورت عدم آپلود شخصی)
const seasonBgs = {
  spring: 'https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=1920&q=80', // شکوفه و کوه
  summer: defaultRiverBg, // رودخانه کوهستانی بزرگ
  autumn: 'https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?auto=format&fit=crop&w=1920&q=80', // پاییز طلایی
  winter: 'https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?auto=format&fit=crop&w=1920&q=80'  // برف کوهستان
}

// تشخیص هوشمند فصل جاری بر اساس ماه (فقط برای رنگ‌بندی تقویم)
const currentSeason = computed(() => {
  const m = currentMonth.value
  if (m >= 1 && m <= 3) return 'spring'
  if (m >= 4 && m <= 6) return 'summer'
  if (m >= 7 && m <= 9) return 'autumn'
  return 'winter'
})

// ====== حالت تقویم: شمسی یا میلادی ======
const calendarMode = ref('shamsi') // 'shamsi' | 'gregorian'

// ====== ابزار تبدیل تاریخ (بالای صفحه) ======
const convertSource = ref('')          // ISO میلادی (از WheelDatePicker)
const convertDirection = ref('sh2g')   // 'sh2g' (شمسی→میلادی) یا 'g2sh' (میلادی→شمسی)
const convertResult = ref('')

// WheelDatePicker مستقیماً ISO میلادی می‌فرسته
function onConvertSourceChange(isoValue) {
  convertSource.value = isoValue || ''
  performConvert()
}

function performConvert() {
  if (!convertSource.value.trim()) {
    convertResult.value = ''
    return
  }
  if (convertDirection.value === 'sh2g') {
    // ISO میلادی → نمایش میلادی
    if (isGregorianISO(convertSource.value.trim())) {
      convertResult.value = convertSource.value.trim()
    } else {
      convertResult.value = 'تاریخ نامعتبر'
    }
  } else {
    // ISO میلادی → شمسی
    if (isGregorianISO(convertSource.value.trim())) {
      const s = toShamsiDisplay(convertSource.value.trim())
      convertResult.value = s || 'تاریخ نامعتبر'
    } else {
      convertResult.value = 'تاریخ نامعتبر'
    }
  }
}

function swapConvertDirection() {
  convertDirection.value = convertDirection.value === 'sh2g' ? 'g2sh' : 'sh2g'
  convertSource.value = ''
  convertResult.value = ''
}

// ====== «برو به تاریخ» ======
const gotoDateValue = ref('')           // ISO میلادی (از WheelDatePicker مستقیم میاد)
const gotoDateType = ref('shamsi')      // نوع نمایش wheel picker

// WheelDatePicker مستقیماً ISO میلادی برمی‌گردونه
function handleGotoDateInput(isoValue) {
  gotoDateValue.value = isoValue || ''
}

function performGoto() {
  if (!gotoDateValue.value) return
  if (calendarMode.value === 'shamsi') {
    const [gy, gm, gd] = gotoDateValue.value.split('-').map(Number)
    const [jy, jm, jd] = g2j(gy, gm, gd)
    currentYear.value = jy
    currentMonth.value = jm
    selectedDayNum.value = jd
  } else {
    const [gy, gm, gd] = gotoDateValue.value.split('-').map(Number)
    currentYear.value = gy
    currentMonth.value = gm
    selectedDayNum.value = gd
  }
}

function swapGotoType() {
  gotoDateType.value = gotoDateType.value === 'shamsi' ? 'gregorian' : 'shamsi'
  gotoDateValue.value = ''
}

// محاسبات شبکه تقویم و کارها
const daysInCurrentMonth = computed(() => {
  if (calendarMode.value === 'gregorian') {
    // میلادی
    return new Date(currentYear.value, currentMonth.value, 0).getDate()
  }
  // شمسی
  const m = currentMonth.value
  if (m <= 6) return 31
  if (m <= 11) return 30
  return (currentYear.value % 33 === 1 || currentYear.value % 33 === 5 || currentYear.value % 33 === 9) ? 30 : 29
})

const startPaddingDays = computed(() => {
  if (calendarMode.value === 'gregorian') {
    // میلادی: getDay() → 0=Sun, 6=Sat. شنبه = 6
    const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1).getDay()
    return (firstDay + 1) % 7
  }
  // شمسی: اولین روز ماه شمسی برابر چندمین روز هفته میلادی است
  const [gy, gm, gd] = j2g(currentYear.value, currentMonth.value, 1)
  const gDate = new Date(gy, gm - 1, gd)
  return (gDate.getDay() + 1) % 7
})

const monthDaysGrid = computed(() => {
  const grid = []
  for (let i = 0; i < startPaddingDays.value; i++) grid.push({ isPadding: true })

  for (let d = 1; d <= daysInCurrentMonth.value; d++) {
    let shamsiSlash, shamsiDash, gregISO, isToday, gregDay, gregMonthName
    if (calendarMode.value === 'gregorian') {
      // حالت میلادی
      shamsiSlash = ''
      shamsiDash = ''
      gregISO = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      gregDay = d
      gregMonthName = englishMonths[currentMonth.value - 1]
      isToday = (currentYear.value === realNow.getFullYear() && currentMonth.value === (realNow.getMonth() + 1) && d === realNow.getDate())
    } else {
      // حالت شمسی
      const [gy, gm, gd] = j2g(currentYear.value, currentMonth.value, d)
      shamsiSlash = `${currentYear.value}/${String(currentMonth.value).padStart(2, '0')}/${String(d).padStart(2, '0')}`
      shamsiDash = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      gregISO = `${gy}-${String(gm).padStart(2, '0')}-${String(gd).padStart(2, '0')}`
      gregDay = gd
      gregMonthName = englishMonths[gm - 1]
      isToday = (currentYear.value === realJY && currentMonth.value === realJM && d === realJD)
    }

    grid.push({
      isPadding: false, dayNum: d, gregDay, gregMonthName,
      shamsiSlash, shamsiDash, gregISO, isToday
    })
  }
  return grid
})

const fetchTasks = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/tasks')
    tasks.value = res.data
    const todayGreg = `${realNow.getFullYear()}-${String(realNow.getMonth() + 1).padStart(2, '0')}-${String(realNow.getDate()).padStart(2, '0')}`
    const todayShamsi = `${realJY}/${String(realJM).padStart(2, '0')}/${String(realJD).padStart(2, '0')}`

    overdueTasks.value = tasks.value.filter(t => !t.is_completed && t.due_date && (t.due_date < todayGreg || t.due_date < todayShamsi))
  } catch (e) {} finally { isLoading.value = false }
}

const getTasksForDayObj = (cell) => {
  if (cell.isPadding) return []
  return tasks.value.filter(t => {
    const d = t.due_date || t.register_date
    if (!d) return false
    return (d === cell.shamsiSlash || d === cell.shamsiDash || d === cell.gregISO)
  })
}

const selectedDayObj = computed(() => monthDaysGrid.value.find(c => !c.isPadding && c.dayNum === selectedDayNum.value) || {})
const tasksForSelectedDay = computed(() => getTasksForDayObj(selectedDayObj.value))

const prevMonth = () => {
  if (calendarMode.value === 'gregorian') {
    if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
    else currentMonth.value--
  } else {
    if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
    else currentMonth.value--
  }
}
const nextMonth = () => {
  if (calendarMode.value === 'gregorian') {
    if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
    else currentMonth.value++
  } else {
    if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
    else currentMonth.value++
  }
}
const goToToday = () => {
  if (calendarMode.value === 'gregorian') {
    currentYear.value = realNow.getFullYear()
    currentMonth.value = realNow.getMonth() + 1
    selectedDayNum.value = realNow.getDate()
  } else {
    currentYear.value = realJY
    currentMonth.value = realJM
    selectedDayNum.value = realJD
  }
}

const toggleTask = async (t) => {
  try {
    const newStatus = !t.is_completed
    await api.put(`/tasks/${t.id}`, { ...t, is_completed: newStatus, status: newStatus ? 'completed' : 'in_progress' })
    await fetchTasks()
  } catch (e) {}
}

// عنوان ماه فعلی برای هدر تقویم
const currentMonthTitle = computed(() => {
  if (calendarMode.value === 'gregorian') {
    return `${englishMonths[currentMonth.value - 1]} ${currentYear.value}`
  }
  return `${shamsiMonths[currentMonth.value - 1]} ${currentYear.value}`
})

onMounted(() => {
  fetchTasks()
})
</script>
<template>
  <div class="relative min-h-screen text-right p-3 sm:p-4 md:p-8 lg:p-10 overflow-hidden" dir="rtl">

    <!-- ۱. پس‌زمینه ثابت (gradient تیره شیشه‌ای برای یکپارچگی با داشبورد) -->
    <div class="fixed inset-0 z-0 bg-cover bg-center"
         style="background-image: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);">
      <div class="absolute inset-0 bg-black/30"></div>
    </div>

    <!-- ۲. محتوای اصلی تقویم -->
    <div class="relative z-20 max-w-7xl mx-auto space-y-4 sm:space-y-6">

      <!-- ═══════ هدر اصلی + ابزارها ═══════ -->
      <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 text-white shadow-2xl space-y-4">
        <!-- ردیف اول: عنوان + دکمه‌های اصلی -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h1 class="text-xl sm:text-2xl md:text-3xl font-black drop-shadow-md flex items-center gap-2">
              <CalendarIcon class="w-6 h-6 sm:w-7 sm:h-7 text-purple-400" />
              تقویم و برنامه‌ها
            </h1>
            <p class="text-[11px] sm:text-xs opacity-70 mt-0.5">
              امروز: {{ weekDays[(new Date().getDay() + 1) % 7] }} {{ realJD }} {{ shamsiMonths[realJM - 1] }} {{ realJY }}
              <span class="opacity-50"> | </span>
              <span dir="ltr">{{ realNow.toISOString().split('T')[0] }}</span>
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <!-- سوییچر شمسی/میلادی -->
            <div class="flex items-center gap-1 p-1 bg-black/40 rounded-xl border border-white/10">
              <button @click="calendarMode = 'shamsi'"
                      class="px-2.5 sm:px-3 py-1.5 rounded-lg text-[11px] sm:text-xs font-bold transition flex items-center gap-1"
                      :style="calendarMode === 'shamsi' ? { background: '#9333ea', color: '#fff' } : { color: 'rgba(255,255,255,0.6)' }">
                <Sun class="w-3.5 h-3.5" /> شمسی
              </button>
              <button @click="calendarMode = 'gregorian'"
                      class="px-2.5 sm:px-3 py-1.5 rounded-lg text-[11px] sm:text-xs font-bold transition flex items-center gap-1"
                      :style="calendarMode === 'gregorian' ? { background: '#9333ea', color: '#fff' } : { color: 'rgba(255,255,255,0.6)' }">
                <Globe class="w-3.5 h-3.5" /> میلادی
              </button>
            </div>

            <!-- دکمه بازگشت به امروز -->
            <button @click="goToToday"
                    class="px-3 py-2 rounded-xl text-[11px] sm:text-xs font-bold bg-white/10 hover:bg-white/20 text-white transition">
              امروز
            </button>
          </div>
        </div>

        <!-- ردیف دوم: ابزار تبدیل تاریخ + برو به تاریخ -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 border-t border-white/10">
          <!-- ابزار تبدیل تاریخ: دو wheel picker (ورودی + خروجی) -->
          <div class="p-3 rounded-xl bg-black/30 border border-white/10 space-y-2">
            <div class="flex items-center justify-between">
              <p class="text-[11px] font-black opacity-80 flex items-center gap-1.5">
                <ArrowRightLeft class="w-3.5 h-3.5 text-blue-400" /> تبدیل تاریخ
              </p>
              <div class="flex items-center gap-1 text-[10px]">
                <span class="px-2 py-0.5 rounded-md font-bold"
                      :class="convertDirection === 'sh2g' ? 'bg-blue-500/30 text-blue-300' : 'opacity-50'">شمسی</span>
                <button @click="swapConvertDirection" class="p-1 rounded hover:bg-white/10" title="تغییر جهت">
                  <ArrowRightLeft class="w-3 h-3" />
                </button>
                <span class="px-2 py-0.5 rounded-md font-bold"
                      :class="convertDirection === 'g2sh' ? 'bg-blue-500/30 text-blue-300' : 'opacity-50'">میلادی</span>
              </div>
            </div>
            <div class="flex gap-2 items-center">
              <div class="flex-1">
                <WheelDatePicker
                  :model-value="convertSource"
                  @update:model-value="onConvertSourceChange"
                  :default-type="convertDirection === 'sh2g' ? 'shamsi' : 'gregorian'" />
              </div>
              <ArrowRightLeft class="w-4 h-4 text-amber-400 flex-shrink-0" />
              <div class="flex-1 px-2.5 py-1.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-xs font-mono flex items-center min-h-[28px]"
                   :class="convertDirection === 'g2sh' ? 'justify-end' : 'justify-start'">
                <span v-if="convertResult" class="font-black text-amber-300 truncate w-full text-center" dir="ltr">{{ convertResult }}</span>
                <span v-else class="opacity-50 text-center w-full">خروجی</span>
              </div>
            </div>
          </div>

          <!-- برو به تاریخ -->
          <div class="p-3 rounded-xl bg-black/30 border border-white/10 space-y-2">
            <div class="flex items-center justify-between">
              <p class="text-[11px] font-black opacity-80 flex items-center gap-1.5">
                <CalendarIcon class="w-3.5 h-3.5 text-amber-400" /> برو به تاریخ
              </p>
              <div class="flex items-center gap-1 text-[10px]">
                <span class="px-2 py-0.5 rounded-md font-bold"
                      :class="gotoDateType === 'shamsi' ? 'bg-amber-500/30 text-amber-300' : 'opacity-50'">شمسی</span>
                <button @click="swapGotoType" class="p-1 rounded hover:bg-white/10" title="تغییر نوع">
                  <ArrowRightLeft class="w-3 h-3" />
                </button>
                <span class="px-2 py-0.5 rounded-md font-bold"
                      :class="gotoDateType === 'gregorian' ? 'bg-amber-500/30 text-amber-300' : 'opacity-50'">میلادی</span>
              </div>
            </div>
            <div class="flex gap-2">
              <div class="flex-1">
                <WheelDatePicker
                  :model-value="gotoDateValue"
                  @update:model-value="handleGotoDateInput"
                  :default-type="gotoDateType" />
              </div>
              <button @click="performGoto"
                      :disabled="!gotoDateValue"
                      class="px-4 py-1.5 rounded-lg bg-amber-500/90 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed text-black font-black text-xs transition flex items-center gap-1">
                برو
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- بنر کارهای عقب‌افتاده -->
      <div v-if="overdueTasks.length > 0" class="p-4 rounded-2xl bg-red-900/40 backdrop-blur-md border border-red-500/50 flex flex-col md:flex-row md:items-center justify-between gap-3 text-white shadow-2xl">
        <div class="flex items-center gap-3">
          <AlertTriangle class="w-5 h-5 sm:w-6 sm:h-6 text-red-400 shrink-0 animate-bounce" />
          <div>
            <h3 class="font-black text-sm sm:text-base">توجه: {{ overdueTasks.length }} کار عقب‌افتاده دارید</h3>
            <p class="text-[10px] sm:text-xs opacity-70">مهلت انجام این کارها به پایان رسیده است.</p>
          </div>
        </div>
        <div class="flex gap-2 overflow-x-auto pb-1">
          <div v-for="t in overdueTasks.slice(0, 3)" :key="t.id" class="px-2.5 py-1 rounded-lg bg-red-500/30 text-white text-[10px] sm:text-xs font-bold truncate max-w-[180px]">
            {{ t.title }}
          </div>
        </div>
      </div>

      <!-- ═══════ شبکه تقویم و پنل روز ═══════ -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">

        <!-- ۱. جدول ماهانه شیشه‌ای (۸ ستون) -->
        <div class="lg:col-span-8 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 space-y-4 text-white">

          <!-- ناوبری ماه -->
          <div class="flex items-center justify-between">
            <button @click="prevMonth" class="p-2 sm:p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition flex items-center gap-1 text-[11px] sm:text-xs font-bold">
              <ChevronRight class="w-4 h-4 sm:w-5 sm:h-5" /> <span class="hidden sm:inline">ماه قبل</span>
            </button>

            <h2 class="text-base sm:text-xl md:text-2xl font-black drop-shadow-md text-center">
              {{ currentMonthTitle }}
            </h2>

            <button @click="nextMonth" class="p-2 sm:p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition flex items-center gap-1 text-[11px] sm:text-xs font-bold">
              <span class="hidden sm:inline">ماه بعد</span> <ChevronLeft class="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
          </div>

          <!-- روزهای هفته (شنبه تا جمعه) -->
          <div class="grid grid-cols-7 gap-1 sm:gap-2 text-center text-[10px] sm:text-xs font-black opacity-80 pb-2 border-b border-white/10">
            <div v-for="w in weekDays" :key="w">{{ w }}</div>
          </div>

          <!-- خانه های تقویم -->
          <div class="grid grid-cols-7 gap-1 sm:gap-2 md:gap-3 text-center">
            <template v-for="(cell, index) in monthDaysGrid" :key="index">

              <div v-if="cell.isPadding" class="aspect-square rounded-xl sm:rounded-2xl opacity-5 bg-white/5"></div>

              <button v-else
                      @click="selectedDayNum = cell.dayNum"
                      class="aspect-square rounded-xl sm:rounded-2xl border p-0.5 sm:p-1 md:p-2 relative flex flex-col justify-between transition-all duration-200 hover:scale-105 active:scale-95 group shadow-lg"
                      :class="selectedDayNum === cell.dayNum ?
                        'bg-purple-600 border-purple-400 text-white ring-2 ring-purple-400/50 shadow-purple-500/40' :
                        cell.isToday ?
                        'bg-amber-500/25 border-amber-400 text-white ring-2 ring-amber-400/60 shadow-lg shadow-amber-500/30' :
                        'bg-white/10 border-white/10 text-white hover:bg-white/20'">

                <!-- عدد روز -->
                <div class="flex justify-between items-start w-full">
                  <span class="text-xs sm:text-base md:text-lg font-black leading-none drop-shadow">{{ cell.dayNum }}</span>
                  <span v-if="cell.isToday" class="text-[7px] sm:text-[9px] px-1 rounded bg-amber-500 text-black font-black">امروز</span>
                </div>

                <!-- نشانگر کارها: دایره‌های رنگی + شمارنده -->
                <div class="flex justify-center items-center gap-0.5 my-0.5 min-h-[6px]">
                  <span v-for="(t, idx) in getTasksForDayObj(cell).slice(0, 3)" :key="idx"
                        class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full shadow-sm"
                        :style="{ background: t.is_completed ? '#22c55e' : '#f97316' }">
                  </span>
                  <span v-if="getTasksForDayObj(cell).length > 3"
                        class="text-[7px] sm:text-[9px] font-black opacity-70">
                    +{{ getTasksForDayObj(cell).length - 3 }}
                  </span>
                </div>

                <!-- معادل تاریخ دیگر زیر خانه -->
                <div class="text-[7px] sm:text-[9px] text-center opacity-60 font-mono leading-none truncate" :dir="calendarMode === 'gregorian' ? 'rtl' : 'ltr'">
                  <template v-if="calendarMode === 'shamsi'">
                    {{ cell.gregDay }} {{ cell.gregMonthName }}
                  </template>
                  <template v-else-if="cell.shamsiSlash">
                    <span dir="rtl">{{ cell.shamsiSlash }}</span>
                  </template>
                </div>
              </button>

            </template>
          </div>

          <!-- راهنمای پایین -->
          <div class="flex flex-wrap items-center justify-center gap-3 sm:gap-4 pt-3 border-t border-white/5 text-[10px] sm:text-xs opacity-70">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-md bg-amber-500/30 ring-1 ring-amber-400"></span> امروز</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-md bg-purple-600 ring-1 ring-purple-400"></span> انتخاب‌شده</span>
            <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-500"></span> انجام‌شده</span>
            <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-orange-500"></span> مانده</span>
          </div>
        </div>

        <!-- ۲. پنل کارهای روز انتخابی (۴ ستون) -->
        <div class="lg:col-span-4 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 flex flex-col justify-between text-white">

          <div>
            <div class="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
              <div class="min-w-0">
                <p class="text-[10px] sm:text-xs opacity-60 font-bold">برنامه‌های روز انتخابی</p>
                <h3 class="text-base sm:text-xl font-black truncate">
                  {{ selectedDayNum }} {{ calendarMode === 'gregorian' ? englishMonths[currentMonth - 1] : shamsiMonths[currentMonth - 1] }} {{ currentYear }}
                </h3>
                <p v-if="selectedDayObj.gregISO" class="text-[10px] sm:text-xs opacity-50 font-mono mt-0.5 truncate" dir="ltr">
                  <span v-if="calendarMode === 'shamsi'">{{ selectedDayObj.gregDay }} {{ selectedDayObj.gregMonthName }} ({{ selectedDayObj.gregISO }})</span>
                  <span v-else>{{ selectedDayObj.shamsiSlash }}</span>
                </p>
              </div>
              <div class="p-2.5 sm:p-3 rounded-xl bg-purple-500/20 text-purple-400 flex-shrink-0">
                <CalendarIcon class="w-5 h-5 sm:w-6 sm:h-6" />
              </div>
            </div>

            <!-- لیست کارها -->
            <div v-if="tasksForSelectedDay.length === 0" class="py-12 text-center opacity-50 space-y-2">
              <Clock class="w-10 h-10 sm:w-12 sm:h-12 mx-auto" />
              <p class="text-xs sm:text-sm font-bold">هیچ برنامه‌ای برای این روز ثبت نشده</p>
            </div>

            <div v-else class="space-y-2.5 max-h-[450px] overflow-y-auto pr-1 custom-scrollbar">
              <div v-for="t in tasksForSelectedDay" :key="t.id"
                   class="p-3 rounded-xl border border-white/10 backdrop-blur-md transition-all flex items-center justify-between gap-2.5 bg-white/5 hover:bg-white/10">
                <div class="flex items-center gap-2.5 min-w-0 flex-1">
                  <button @click="toggleTask(t)"
                          class="w-5 h-5 sm:w-6 sm:h-6 rounded-md sm:rounded-lg border-2 flex items-center justify-center transition shrink-0"
                          :style="{ borderColor: t.is_completed ? '#22c55e' : 'rgba(255,255,255,0.3)', background: t.is_completed ? '#22c55e' : 'transparent' }">
                    <Check v-if="t.is_completed" class="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                  </button>
                  <div class="min-w-0 flex-1">
                    <p class="font-bold text-xs sm:text-sm truncate" :class="t.is_completed ? 'line-through opacity-40' : ''">
                      {{ t.title }}
                    </p>
                    <p v-if="t.category" class="text-[9px] sm:text-[10px] opacity-60 mt-0.5 truncate">{{ t.category }}</p>
                  </div>
                </div>
                <span v-if="t.priority > 0" class="text-[8px] sm:text-[9px] font-black px-1.5 sm:px-2 py-0.5 rounded-full text-white flex-shrink-0" :style="{ background: t.priority === 2 ? '#ef4444' : '#eab308' }">
                  {{ t.priority === 2 ? 'فوری' : 'مهم' }}
                </span>
              </div>
            </div>
          </div>

          <div class="pt-4 border-t border-white/10 mt-4 text-center opacity-60 text-[10px] sm:text-xs">
            مجموع کارهای این روز: {{ tasksForSelectedDay.length }} مورد
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 10px; }
.glass-card {
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
</style>