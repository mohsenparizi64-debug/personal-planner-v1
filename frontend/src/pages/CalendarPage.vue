<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  ChevronRight, ChevronLeft, Calendar as CalendarIcon, 
  Clock, AlertTriangle, Check, Upload, Image as ImageIcon, 
  Volume2, VolumeX, RotateCcw, Sparkles, X 
} from 'lucide-vue-next'
import api from '@/services/api'

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

// داده‌های تسک‌ها
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

// تشخیص هوشمند فصل جاری بر اساس ماه
const currentSeason = computed(() => {
  const m = currentMonth.value
  if (m >= 1 && m <= 3) return 'spring'
  if (m >= 4 && m <= 6) return 'summer'
  if (m >= 7 && m <= 9) return 'autumn'
  return 'winter'
})

// تصویر پس‌زمینه فعلی (عکس شخصی یا عکس پیش‌فرض فصل)
const activeBgUrl = computed(() => {
  if (customBgUrl.value) return customBgUrl.value
  return seasonBgs[currentSeason.value]
})

// سیستم صدای زنده طبیعت
const isAudioPlaying = ref(false)
let ambientAudio = null

const toggleAudio = () => {
  if (!ambientAudio) {
    // لینک صدا طبیعت واقعی
    ambientAudio = new Audio('https://cdn.pixabay.com/download/audio/2022/05/16/audio_db6591201e.mp3?filename=birds-in-forest-20770.mp3')
    ambientAudio.loop = true
    ambientAudio.volume = 0.4
  }
  if (isAudioPlaying.value) {
    ambientAudio.pause()
    isAudioPlaying.value = false
  } else {
    ambientAudio.play().catch(() => {})
    isAudioPlaying.value = true
  }
}

// آپلود عکس اختصاصی از کامپیوتر کاربر
const handleImageUpload = (e) => {
  const file = e.target.files[0]
  uploadError.value = ''
  if (!file) return

  // چک کردن حجم (حداکثر ۵ مگابایت)
  if (file.size > 5 * 1024 * 1024) {
    uploadError.value = 'حجم عکس نباید بیشتر از ۵ مگابایت باشد.'
    return
  }

  // چک کردن فرمت
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    uploadError.value = 'فرمت فایل باید JPG، PNG یا WEBP باشد.'
    return
  }

  const reader = new FileReader()
  reader.onload = (event) => {
    const result = event.target.result
    customBgUrl.value = result
    localStorage.setItem('planner_calendar_custom_bg', result)
    showUploadModal.value = false
  }
  reader.readAsDataURL(file)
}

const resetDefaultBg = () => {
  customBgUrl.value = ''
  localStorage.removeItem('planner_calendar_custom_bg')
}

// انیمیشن زنده باران و برف رو بوم (Canvas Engine)
let canvasAnimId = null

const initCanvasWeather = () => {
  const canvas = document.getElementById('weatherCanvas')
  if (!canvas) return
  const ctx = canvas.getContext('2d')

  let width = canvas.width = window.innerWidth
  let height = canvas.height = window.innerHeight

  const handleResize = () => {
    width = canvas.width = window.innerWidth
    height = canvas.height = window.innerHeight
  }
  window.addEventListener('resize', handleResize)

  // ساخت ذرات متناسب با فصل
  const particles = []
  const particleCount = currentSeason.value === 'spring' || currentSeason.value === 'winter' ? 70 : 40

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      length: Math.random() * 20 + 10,
      speedY: Math.random() * 3 + 2,
      speedX: Math.random() * 1 - 0.5,
      size: Math.random() * 3 + 1,
      opacity: Math.random() * 0.5 + 0.2
    })
  }

  const render = () => {
    ctx.clearRect(0, 0, width, height)

    particles.forEach(p => {
      ctx.beginPath()
      if (currentSeason.value === 'spring') {
        // باران بهاری
        ctx.strokeStyle = `rgba(180, 220, 255, ${p.opacity})`
        ctx.lineWidth = 1.5
        ctx.moveTo(p.x, p.y)
        ctx.lineTo(p.x + p.speedX * 2, p.y + p.length)
        ctx.stroke()
      } else if (currentSeason.value === 'winter') {
        // برف زمستانی
        ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()
      } else if (currentSeason.value === 'autumn') {
        // برگ پاییزی
        ctx.fillStyle = `rgba(245, 158, 11, ${p.opacity})`
        ctx.arc(p.x, p.y, p.size * 1.5, 0, Math.PI * 2)
        ctx.fill()
      } else {
        // ذرات طلایی تابستان
        ctx.fillStyle = `rgba(253, 224, 71, ${p.opacity})`
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()
      }

      p.y += p.speedY
      p.x += p.speedX

      if (p.y > height) {
        p.y = -10
        p.x = Math.random() * width
      }
    })

    canvasAnimId = requestAnimationFrame(render)
  }

  render()
}

// محاسبات شبکه تقویم و تسک‌ها
const daysInCurrentMonth = computed(() => {
  const m = currentMonth.value
  if (m <= 6) return 31
  if (m <= 11) return 30
  return (currentYear.value % 33 === 1 || currentYear.value % 33 === 5 || currentYear.value % 33 === 9) ? 30 : 29
})

const startPaddingDays = computed(() => {
  const [gy, gm, gd] = j2g(currentYear.value, currentMonth.value, 1)
  const gDate = new Date(gy, gm - 1, gd)
  return (gDate.getDay() + 1) % 7
})

const monthDaysGrid = computed(() => {
  const grid = []
  for (let i = 0; i < startPaddingDays.value; i++) grid.push({ isPadding: true })

  for (let d = 1; d <= daysInCurrentMonth.value; d++) {
    const [gy, gm, gd] = j2g(currentYear.value, currentMonth.value, d)
    const shamsiSlash = `${currentYear.value}/${String(currentMonth.value).padStart(2, '0')}/${String(d).padStart(2, '0')}`
    const shamsiDash = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const gregISO = `${gy}-${String(gm).padStart(2, '0')}-${String(gd).padStart(2, '0')}`
    const isToday = (currentYear.value === realJY && currentMonth.value === realJM && d === realJD)

    grid.push({
      isPadding: false, dayNum: d, gregDay: gd, gregMonthName: englishMonths[gm - 1],
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

    overdueTasks.value = tasks.value.filter(t => !t.is_completed && t.due_date && (t.due_date < todayGreg && t.due_date < todayShamsi))
  } catch (e) {} finally { isLoading.value = false }
}

const getTasksForDayObj = (cell) => {
  if (cell.isPadding) return []
  return tasks.value.filter(t => {
    const d = t.due_date || t.register_date
    return (d === cell.shamsiSlash || d === cell.shamsiDash || d === cell.gregISO)
  })
}

const selectedDayObj = computed(() => monthDaysGrid.value.find(c => !c.isPadding && c.dayNum === selectedDayNum.value) || {})
const tasksForSelectedDay = computed(() => getTasksForDayObj(selectedDayObj.value))

const prevMonth = () => { if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- } else currentMonth.value-- }
const nextMonth = () => { if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ } else currentMonth.value++ }
const goToToday = () => { currentYear.value = realJY; currentMonth.value = realJM; selectedDayNum.value = realJD }

const toggleTask = async (t) => {
  try {
    const newStatus = !t.is_completed
    await api.put(`/tasks/${t.id}`, { ...t, is_completed: newStatus, status: newStatus ? 'completed' : 'in_progress' })
    await fetchTasks()
  } catch (e) {}
}

onMounted(() => {
  fetchTasks()
  setTimeout(initCanvasWeather, 300)
})

onUnmounted(() => {
  if (canvasAnimId) cancelAnimationFrame(canvasAnimId)
  if (ambientAudio) { ambientAudio.pause(); ambientAudio = null }
})
</script>
<template>
  <div class="relative min-h-screen text-right p-6 md:p-10 overflow-hidden" dir="rtl">
    
    <!-- ۱. لایه تصویر پس‌زمینه زنده (عکس اختصاصی یا پیش‌فرض رودخانه کوهستانی) -->
    <div class="fixed inset-0 z-0 bg-cover bg-center transition-all duration-1000"
         :style="{ backgroundImage: `url(${activeBgUrl})` }">
      
      <div class="absolute inset-0 bg-black/35"></div>
    </div>

    <!-- ۲. لایه انیمیشن زنده باران/برف (Canvas) -->
    <canvas id="weatherCanvas" class="fixed inset-0 z-10 pointer-events-none"></canvas>

    <!-- ۳. محتوای اصلی تقویم (روی لایه شیشه‌ای) -->
    <div class="relative z-20 max-w-7xl mx-auto space-y-8">

      <!-- هدر اصلی -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-3xl bg-black/30 backdrop-blur-md border border-white/10 text-white shadow-2xl">
        <div>
          <h1 class="text-3xl font-black mb-1 drop-shadow-md">تقویم زنده طبیعت</h1>
          <p class="text-xs opacity-80">
            امروز: {{ weekDays[(new Date().getDay() + 1) % 7] }} {{ realJD }} {{ shamsiMonths[realJM - 1] }} {{ realJY }}
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <!-- دکمه صدای طبیعت -->
          <button @click="toggleAudio" 
                  class="px-4 py-2.5 rounded-2xl font-bold text-xs flex items-center gap-2 transition-all backdrop-blur-md border border-white/20 hover:scale-105 active:scale-95"
                  :class="isAudioPlaying ? 'bg-green-500/80 text-white animate-pulse' : 'bg-white/10 text-white'">
            <Volume2 v-if="isAudioPlaying" class="w-4 h-4" />
            <VolumeX v-else class="w-4 h-4" />
            <span>{{ isAudioPlaying ? 'صدای طبیعت (روشن)' : 'پخش صدای طبیعت' }}</span>
          </button>

          <!-- دکمه آپلود عکس شخصی -->
          <button @click="showUploadModal = true" 
                  class="px-4 py-2.5 rounded-2xl font-bold text-xs flex items-center gap-2 transition-all bg-purple-600/80 hover:bg-purple-600 text-white backdrop-blur-md shadow-lg hover:scale-105 active:scale-95">
            <ImageIcon class="w-4 h-4" />
            <span>تغییر پس‌زمینه تقویم</span>
          </button>

          <!-- دکمه بازگشت به امروز -->
          <button @click="goToToday" 
                  class="px-4 py-2.5 rounded-2xl font-bold text-xs bg-white/20 hover:bg-white/30 text-white backdrop-blur-md transition hover:scale-105 active:scale-95">
            امروز
          </button>
        </div>
      </div>

      <!-- بنر کارهای عقب‌افتاده -->
      <div v-if="overdueTasks.length > 0" class="p-5 rounded-3xl bg-red-900/40 backdrop-blur-md border border-red-500/50 flex flex-col md:flex-row md:items-center justify-between gap-4 text-white shadow-2xl animate-in fade-in duration-300">
        <div class="flex items-center gap-3">
          <AlertTriangle class="w-6 h-6 text-red-400 shrink-0 animate-bounce" />
          <div>
            <h3 class="font-black text-base">توجه: {{ overdueTasks.length }} تسک عقب‌افتاده دارید</h3>
            <p class="text-xs opacity-70">مهلت انجام این کارها به پایان رسیده است.</p>
          </div>
        </div>
        <div class="flex gap-2 overflow-x-auto pb-1">
          <div v-for="t in overdueTasks.slice(0, 3)" :key="t.id" class="px-3 py-1.5 rounded-xl bg-red-500/30 text-white text-xs font-bold truncate max-w-[180px]">
            {{ t.title }}
          </div>
        </div>
      </div>

      <!-- شبکه تقویم و پنل روز -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- ۱. جدول ماهانه شیشه‌ای (۸ ستون) -->
        <div class="lg:col-span-8 rounded-3xl border border-white/10 p-6 md:p-8 bg-black/30 backdrop-blur-xl shadow-2xl space-y-6 text-white">
          
          <!-- ناوبری ماه -->
          <div class="flex items-center justify-between mb-4">
            <button @click="prevMonth" class="p-3 rounded-2xl bg-white/10 hover:bg-white/20 transition flex items-center gap-1 text-xs font-bold">
              <ChevronRight class="w-5 h-5" /> ماه قبل
            </button>

            <h2 class="text-2xl font-black drop-shadow-md">
              {{ shamsiMonths[currentMonth - 1] }} {{ currentYear }}
            </h2>

            <button @click="nextMonth" class="p-3 rounded-2xl bg-white/10 hover:bg-white/20 transition flex items-center gap-1 text-xs font-bold">
              ماه بعد <ChevronLeft class="w-5 h-5" />
            </button>
          </div>

          <!-- روزهای هفته (شنبه تا جمعه) -->
          <div class="grid grid-cols-7 gap-2 text-center text-xs font-black opacity-80 pb-3 border-b border-white/10">
            <div v-for="w in weekDays" :key="w">{{ w }}</div>
          </div>

          <!-- خانه های تقویم (Grid زنده) -->
          <div class="grid grid-cols-7 gap-2 md:gap-3 text-center">
            <template v-for="(cell, index) in monthDaysGrid" :key="index">
              
              <div v-if="cell.isPadding" class="aspect-square rounded-2xl opacity-5 bg-white/5"></div>

              <button v-else
                      @click="selectedDayNum = cell.dayNum"
                      class="aspect-square rounded-2xl border p-1 md:p-2 relative flex flex-col justify-between transition-all duration-300 hover:scale-105 active:scale-95 group shadow-lg"
                      :class="selectedDayNum === cell.dayNum ? 
                        'bg-blue-600 border-blue-400 text-white ring-4 ring-blue-500/30 shadow-blue-500/40' : 
                        cell.isToday ? 
                        'bg-blue-500/30 border-blue-400 text-white' : 
                        'bg-white/10 border-white/10 text-white hover:bg-white/20'">
                
                <!-- عدد روز شمسی -->
                <div class="flex justify-between items-center w-full">
                  <span class="text-base md:text-lg font-black leading-none drop-shadow">{{ cell.dayNum }}</span>
                  <span v-if="cell.isToday" class="text-[9px] px-1 rounded bg-blue-500 text-white font-bold">امروز</span>
                </div>

                <!-- نقاط نشانگر تسک‌ها -->
                <div class="flex justify-center gap-1 my-0.5">
                  <span v-for="(t, idx) in getTasksForDayObj(cell).slice(0, 3)" :key="idx"
                        class="w-2 h-2 rounded-full shadow-sm"
                        :style="{ background: t.is_completed ? '#22c55e' : '#f97316' }">
                  </span>
                </div>

                <!-- معادل روز میلادی زیر خانه -->
                <div class="text-[9px] text-left opacity-60 font-mono leading-none" dir="ltr">
                  {{ cell.gregDay }} {{ cell.gregMonthName }}
                </div>
              </button>

            </template>
          </div>
        </div>

        <!-- ۲. پنل تسک‌های روز انتخابی (۴ ستون) -->
        <div class="lg:col-span-4 rounded-3xl border border-white/10 p-6 bg-black/30 backdrop-blur-xl shadow-2xl flex flex-col justify-between text-white">
          
          <div>
            <div class="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
              <div>
                <p class="text-xs opacity-60 font-bold">برنامه‌های روز انتخابی</p>
                <h3 class="text-xl font-black">
                  {{ selectedDayNum }} {{ shamsiMonths[currentMonth - 1] }} {{ currentYear }}
                </h3>
                <p v-if="selectedDayObj.gregISO" class="text-xs opacity-50 font-mono mt-0.5" dir="ltr">
                  {{ selectedDayObj.gregDay }} {{ selectedDayObj.gregMonthName }} ({{ selectedDayObj.gregISO }})
                </p>
              </div>
              <div class="p-3 rounded-2xl bg-blue-500/20 text-blue-400">
                <CalendarIcon class="w-6 h-6" />
              </div>
            </div>

            <!-- لیست تسک‌ها -->
            <div v-if="tasksForSelectedDay.length === 0" class="py-16 text-center opacity-50 space-y-2">
              <Clock class="w-12 h-12 mx-auto" />
              <p class="text-sm font-bold">هیچ برنامه‌ای برای این روز ثبت نشده</p>
            </div>

            <div v-else class="space-y-3 max-h-[450px] overflow-y-auto pr-1 custom-scrollbar">
              <div v-for="t in tasksForSelectedDay" :key="t.id" 
                   class="p-4 rounded-2xl border border-white/10 backdrop-blur-md transition-all flex items-center justify-between gap-3 bg-white/5 hover:bg-white/10">
                
                <div class="flex items-center gap-3">
                  <button @click="toggleTask(t)" 
                          class="w-6 h-6 rounded-lg border-2 flex items-center justify-center transition shrink-0"
                          :style="{ borderColor: t.is_completed ? '#22c55e' : 'rgba(255,255,255,0.3)', background: t.is_completed ? '#22c55e' : 'transparent' }">
                    <Check v-if="t.is_completed" class="w-4 h-4 text-white" />
                  </button>
                  <div>
                    <p class="font-bold text-sm" :class="t.is_completed ? 'line-through opacity-40' : ''">
                      {{ t.title }}
                    </p>
                    <p v-if="t.category" class="text-[10px] opacity-60 mt-0.5">{{ t.category }}</p>
                  </div>
                </div>

                <span v-if="t.priority > 0" class="text-[9px] font-black px-2 py-0.5 rounded-full text-white" :style="{ background: t.priority === 2 ? '#ef4444' : '#eab308' }">
                  {{ t.priority === 2 ? 'فوری' : 'مهم' }}
                </span>
              </div>
            </div>
          </div>

          <div class="pt-6 border-t border-white/10 mt-6 text-center opacity-60 text-xs">
            مجموع کارهای این روز: {{ tasksForSelectedDay.length }} مورد
          </div>

        </div>

      </div>

    </div>

    <!-- ========== ۴. مودال آپلود عکس اختصاصی با کادر مشخصات کامل ========== -->
    <div v-if="showUploadModal" class="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" @click.self="showUploadModal = false">
      <div class="w-full max-w-md rounded-3xl p-8 bg-gray-900 border border-white/10 shadow-2xl text-white space-y-6 animate-in zoom-in duration-200">
        
        <div class="flex justify-between items-center">
          <h3 class="text-xl font-black flex items-center gap-2">
            <ImageIcon class="w-5 h-5 text-purple-400" /> تنطیم پس‌زمینه تقویم
          </h3>
          <button @click="showUploadModal = false" class="p-1 hover:bg-white/10 rounded-full"><X /></button>
        </div>

        <!-- کادر مشخصات تصویر مناسب -->
        <div class="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-xs leading-relaxed space-y-1.5 text-blue-200">
          <p class="font-bold text-blue-400 flex items-center gap-1"><Sparkles class="w-4 h-4" /> مشخصات عکس پیشنهادی:</p>
          <p>• <b>ابعاد استاندارد:</b> ۱۹۲۰ در ۱۰۸۰ پیکسل (افقی Full HD)</p>
          <p>• <b>فرمت‌های مجاز:</b> JPG ، PNG یا WEBP</p>
          <p>• <b>حداکثر حجم:</b> ۵ مگابایت (جهت سرعت بالای اجرای برنامه)</p>
        </div>

        <!-- کادر آپلود -->
        <label class="border-2 border-dashed border-white/20 hover:border-purple-500 rounded-3xl p-8 flex flex-col items-center justify-center cursor-pointer transition bg-white/5 hover:bg-white/10 group">
          <Upload class="w-10 h-10 mb-2 text-purple-400 group-hover:scale-110 transition-transform" />
          <span class="text-sm font-bold mb-1">برای انتخاب عکس کلیک کنید</span>
          <span class="text-[10px] opacity-50">عکس انتخابی برای همیشه در مرروگرتان ذخیره می‌شود</span>
          <input type="file" @change="handleImageUpload" accept="image/*" class="hidden" />
        </label>

        <p v-if="uploadError" class="text-xs text-red-400 text-center font-bold">{{ uploadError }}</p>

        <!-- دکمه‌های عملیات -->
        <div class="flex gap-3 pt-2">
          <button v-if="customBgUrl" @click="resetDefaultBg" class="flex-1 py-3 rounded-2xl bg-red-500/20 text-red-300 border border-red-500/30 font-bold text-xs flex items-center justify-center gap-1 hover:bg-red-500/30 transition">
            <RotateCcw class="w-4 h-4" /> بازگشت به عکس رودخانه پیش‌فرض
          </button>
          <button @click="showUploadModal = false" class="px-6 py-3 rounded-2xl bg-white/10 hover:bg-white/20 font-bold text-xs">
            بستن
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 10px; }
.animate-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>