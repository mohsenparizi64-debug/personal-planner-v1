<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { toShamsiDisplay } from '@/utils/date'
import { 
  HeartPulse, Dumbbell, Utensils, Moon, Sparkles, Scale, Plus, CheckCircle, Clock, Calendar, Edit3, Trash2, AlertCircle, Zap, Target, Flame, Info, Loader2, Footprints, Bike, Waves, Mountain, Shield
} from 'lucide-vue-next'

const authStore = useAuthStore()
const activeTab = ref('spiritual') // spiritual, workout, nutrition, health

const spiritualTrackers = ref([])
const workoutLogs = ref([])
const mealLogs = ref([])
const healthLogs = ref([])

const loading = ref(false)
const aiLoadingWorkout = ref(false)
const aiLoadingMeal = ref(false)
const aiError = ref('')
const notificationMsg = ref('')

const showNotification = (msg) => {
  notificationMsg.value = msg
  setTimeout(() => { notificationMsg.value = '' }, 3500)
}

const todayISO = new Date().toISOString().split('T')[0]

// متغیر ذخیره متن بنر سبز رنگ زمان‌دار برای کادر سمت چپ مشخصات فیزیکی
const lastBiometricsArchivedTime = ref('')

// مشخصات فیزیکی و بیومتریک کاربر
const biometricsForm = ref({
  log_date: todayISO,
  weight: authStore.user?.weight || '',
  target_weight: authStore.user?.target_weight || '',
  height: authStore.user?.height || '',
  birth_date: authStore.user?.birth_date || '',
  gender: authStore.user?.gender || 'مرد',
  activity_level: authStore.user?.activity_level || 'متوسط',
  health_notes: authStore.user?.health_notes || ''
})

// محاسبه زنده BMI همزمان با تایپ کاربر
const liveBMI = computed(() => {
  const w = Number(biometricsForm.value.weight)
  const h = Number(biometricsForm.value.height)
  if (w && h) {
    const hMeter = h / 100
    return (w / (hMeter * hMeter)).toFixed(1)
  }
  return null
})

// فرم ورزش
const showWorkoutModal = ref(false)
const isEditingWorkout = ref(false)
const editingWorkoutId = ref(null)

const workoutForm = ref({
  log_date: todayISO,
  log_time: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }),
  workout_type: '🏃‍♂️ دویدن (Running)',
  duration_minutes: 30,
  calories_burned: 0,
  notes: ''
})

const exerciseCategories = [
  '🏃‍♂️ دویدن (Running)',
  '🚶‍♂️ پیاده‌روی (Walking)',
  '🚴‍♂️ دوچرخه‌سواری (Outdoor/Indoor Cycling)',
  '🏋️‍♂️ تمرینات قدرتی و وزنه (Strength Training)',
  '🏊‍♂️ شنا (Swimming)',
  '🧘‍♂️ یوگا و حرکات اصلاحی (Yoga / Flexibility)',
  '⚽ ورزش‌های توپی و تیمی (HIIT / Team Sports)',
  '🧗‍♂️ کوهنوردی و پیاده‌روی طبیعت (Hiking)',
  '🥊 رزمی و هوازی سنگین (Cardio / Martial Arts)',
  '🚣‍♂️ قایقرانی و دستگاه پارویی (Rower / Water Sports)'
]

// استخراج استیکر/ایموجی اختصاصی ورزش برای نمایش بزرگ
const getExerciseEmoji = (type) => {
  if (!type) return '🏋️‍♂️'
  const match = type.match(/^[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}]/u)
  return match ? match[0] : '🏋️‍♂️'
}

// فرم تغذیه
const isEditingMeal = ref(false)
const editingMealId = ref(null)

const mealForm = ref({
  log_date: todayISO,
  log_time: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }),
  meal_type: 'ناهار',
  food_name: '',
  portion_unit: '',
  calories: 0,
  temperament: 'معتدل',
  notes: ''
})

// فرم هدف معنوی
const showSpiritualModal = ref(false)
const isEditingSpiritual = ref(false)
const editingTrackerId = ref(null)

const spiritualForm = ref({
  title: 'نماز قضا',
  tracker_type: 'prayer_qada',
  total_needed: 360,
  completed_count: 0,
  unit: 'روز',
  register_date: todayISO,
  last_action_date: todayISO
})

const fetchData = async () => {
  loading.value = true
  
  try {
    const spRes = await api.get('/bio/spiritual')
    spiritualTrackers.value = [...spRes.data]
  } catch (err) { console.error(err) }

  try {
    const woRes = await api.get('/bio/workout')
    workoutLogs.value = [...woRes.data]
  } catch (err) { console.error(err) }

  try {
    const meRes = await api.get('/bio/meal')
    mealLogs.value = [...meRes.data]
  } catch (err) { console.error(err) }

  try {
    const heRes = await api.get('/bio/health')
    healthLogs.value = [...heRes.data]
  } catch (err) { console.error(err) }

  loading.value = false
}

// خلاصه شاخص‌های هدر اصلی
const totalCaloriesIntakeToday = computed(() => {
  return mealLogs.value
    .filter(m => m.log_date === todayISO)
    .reduce((sum, m) => sum + (m.calories || 0), 0)
})

const totalCaloriesBurnedToday = computed(() => {
  return workoutLogs.value
    .filter(w => w.log_date === todayISO)
    .reduce((sum, w) => sum + (w.calories_burned || 0), 0)
})

const todayDominantTemperament = computed(() => {
  const todayMeals = mealLogs.value.filter(m => m.log_date === todayISO && m.temperament)
  if (!todayMeals.length) return 'ثبت‌نشده'
  const counts = {}
  todayMeals.forEach(m => { counts[m.temperament] = (counts[m.temperament] || 0) + 1 })
  let maxTemp = 'معتدل'
  let maxC = 0
  for (const [k, v] of Object.entries(counts)) {
    if (v > maxC) { maxC = v; maxTemp = k }
  }
  return maxTemp
})

const dailyTargetCalorieBudget = computed(() => {
  const weight = Number(biometricsForm.value.weight) || 70
  const height = Number(biometricsForm.value.height) || 175
  const isMale = biometricsForm.value.gender === 'مرد'
  
  let bmr = (10 * weight) + (6.25 * height) - (5 * 30) + (isMale ? 5 : -161)
  const mult = { 'نشسته': 1.2, 'سبک': 1.375, 'متوسط': 1.55, 'پرتحرک': 1.725 }[biometricsForm.value.activity_level] || 1.4
  return Math.round(bmr * mult)
})

const remainingCaloriesToday = computed(() => {
  return (dailyTargetCalorieBudget.value + totalCaloriesBurnedToday.value) - totalCaloriesIntakeToday.value
})

const targetWeightStatusText = computed(() => {
  const current = Number(biometricsForm.value.weight)
  const target = Number(biometricsForm.value.target_weight)
  if (!current || !target) return 'وزن هدف ثبت‌نشده'
  const diff = (current - target).toFixed(1)
  if (diff > 0) return `شما ${diff} کیلوگرم اضافه وزن دارید`
  if (diff < 0) return `شما ${Math.abs(diff)} کیلوگرم کمبود وزن دارید`
  return 'شما در وزن هدف قرار دارید 🎉'
})

// تخمین AI مربی ورزشی
const estimateWorkoutAI = async () => {
  if (!workoutForm.value.workout_type || !workoutForm.value.duration_minutes) return
  aiLoadingWorkout.value = true
  aiError.value = ''
  try {
    const res = await api.post('/bio/estimate-workout', {
      workout_type: workoutForm.value.workout_type,
      duration_minutes: Number(workoutForm.value.duration_minutes)
    })
    workoutForm.value.calories_burned = res.data.estimated_calories
  } catch (e) {
    aiError.value = e.response?.data?.detail || '⚠️ خطا در ارتباط با AI مربی ورزشی'
  } finally {
    aiLoadingWorkout.value = false
  }
}

// تخمین AI کارشناس تغذیه
const estimateMealAI = async () => {
  if (!mealForm.value.food_name || !mealForm.value.portion_unit) return
  aiLoadingMeal.value = true
  aiError.value = ''
  try {
    const res = await api.post('/bio/estimate-meal', {
      food_name: mealForm.value.food_name,
      portion_unit: mealForm.value.portion_unit,
      meal_type: mealForm.value.meal_type
    })
    mealForm.value.calories = res.data.estimated_calories
    mealForm.value.temperament = res.data.temperament
  } catch (e) {
    aiError.value = e.response?.data?.detail || '⚠️ خطا در ارتباط با AI کارشناس تغذیه'
  } finally {
    aiLoadingMeal.value = false
  }
}

// ذخیره / ویرایش ورزش
const saveWorkout = async () => {
  try {
    if (isEditingWorkout.value) {
      await api.put(`/bio/workout/${editingWorkoutId.value}`, workoutForm.value)
      showNotification('✅ فعالیت ورزشی با موفقیت بروزرسانی شد!')
    } else {
      await api.post('/bio/workout', workoutForm.value)
      showNotification('✅ فعالیت ورزشی شما ثبت شد!')
    }
    showWorkoutModal.value = false
    isEditingWorkout.value = false
    workoutForm.value = { log_date: todayISO, log_time: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }), workout_type: '🏃‍♂️ دویدن (Running)', duration_minutes: 30, calories_burned: 0, notes: '' }
    fetchData()
  } catch (e) { console.error(e) }
}

const editWorkout = (w) => {
  isEditingWorkout.value = true
  editingWorkoutId.value = w.id
  workoutForm.value = { log_date: w.log_date, log_time: w.log_time, workout_type: w.workout_type, duration_minutes: w.duration_minutes, calories_burned: w.calories_burned, notes: w.notes || '' }
  showWorkoutModal.value = true
}

const deleteWorkout = async (wId) => {
  if (confirm('آیا از حذف این فعالیت ورزشی اطمینان دارید؟')) {
    try {
      await api.delete(`/bio/workout/${wId}`)
      showNotification('🗑️ فعالیت ورزشی حذف شد.')
      fetchData()
    } catch (e) { console.error(e) }
  }
}

// ذخیره / ویرایش وعده غذایی
const saveMeal = async () => {
  try {
    if (isEditingMeal.value) {
      await api.put(`/bio/meal/${editingMealId.value}`, mealForm.value)
      showNotification('✅ وعده غذایی با موفقیت بروزرسانی شد!')
    } else {
      await api.post('/bio/meal', mealForm.value)
      showNotification('✅ وعده غذایی ثبت شد!')
    }
    isEditingMeal.value = false
    mealForm.value = { log_date: todayISO, log_time: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }), meal_type: 'ناهار', food_name: '', portion_unit: '', calories: 0, temperament: 'معتدل', notes: '' }
    fetchData()
  } catch (e) { console.error(e) }
}

const editMeal = (m) => {
  isEditingMeal.value = true
  editingMealId.value = m.id
  mealForm.value = { log_date: m.log_date, log_time: m.log_time, meal_type: m.meal_type, food_name: m.food_name, portion_unit: m.portion_unit, calories: m.calories, temperament: m.temperament || 'معتدل', notes: m.notes || '' }
}

const deleteMeal = async (mId) => {
  if (confirm('آیا از حذف این وعده غذایی اطمینان دارید؟')) {
    try {
      await api.delete(`/bio/meal/${mId}`)
      showNotification('🗑️ وعده غذایی حذف گردید.')
      fetchData()
    } catch (e) { console.error(e) }
  }
}

// ذخیره مشخصات فیزیکی با ایجاد پیام بنری دقیق شامل تاریخ و ساعت در کادر سمت چپ
const saveBiometrics = async () => {
  try {
    const nowTimeStr = new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    const shamsiDateStr = toShamsiDisplay(biometricsForm.value.log_date || todayISO)
    
    await api.put('/bio/biometrics', biometricsForm.value)
    await api.post('/bio/health', {
      log_date: biometricsForm.value.log_date || todayISO,
      weight: Number(biometricsForm.value.weight),
      height: Number(biometricsForm.value.height)
    })
    if (authStore.fetchUser) await authStore.fetchUser()
    
    // تنظیم بنر صریح در کادر سمت چپ
    lastBiometricsArchivedTime.value = `مشخصات فیزیکی و وزن هدف شما در تاریخ ${shamsiDateStr} و ساعت ${nowTimeStr} ثبت شد و مبنای محاسبات قرار گرفته است.`
    showNotification('✅ مشخصات فیزیکی امروز با موفقیت آرشیو شد!')
    await fetchData()
  } catch (e) { 
    console.error(e) 
    alert('⚠️ خطا در ذخیره مشخصات فیزیکی: ' + (e.response?.data?.detail || e.message))
  }
}

// ذخیره هدف معنوی با بستن قطعی مودال و بروزرسانی آنی آرایه DOM
const saveSpiritualTracker = async () => {
  try {
    if (isEditingSpiritual.value) {
      await api.put(`/bio/spiritual/${editingTrackerId.value}`, spiritualForm.value)
      showNotification('✅ هدف معنوی با موفقیت بروزرسانی شد!')
    } else {
      await api.post('/bio/spiritual', spiritualForm.value)
      showNotification('✅ هدف معنوی شما با موفقیت ساخته شد!')
    }
    showSpiritualModal.value = false
    isEditingSpiritual.value = false
    
    const spRes = await api.get('/bio/spiritual')
    spiritualTrackers.value = [...spRes.data]
  } catch (e) { 
    console.error('Save Spiritual Error:', e)
    alert('⚠️ خطا در ذخیره هدف معنوی: ' + (e.response?.data?.detail || e.message))
  }
}

const incrementSpiritual = async (trackerId) => {
  try {
    await api.post('/bio/spiritual/log', { tracker_id: trackerId, log_date: todayISO, count_change: 1 })
    showNotification('✅ ۱ واحد روزانه ثبت گردید!')
    const spRes = await api.get('/bio/spiritual')
    spiritualTrackers.value = [...spRes.data]
  } catch (e) { console.error(e) }
}

const editSpiritualTracker = (t) => {
  isEditingSpiritual.value = true
  editingTrackerId.value = t.id
  spiritualForm.value = { title: t.title, tracker_type: t.tracker_type, total_needed: t.total_needed, completed_count: t.completed_count, unit: t.unit || 'روز', register_date: t.register_date || todayISO, last_action_date: t.last_action_date || todayISO }
  showSpiritualModal.value = true
}

const deleteSpiritualTracker = async (tId) => {
  if (confirm('آیا از حذف این هدف معنوی اطمینان دارید؟')) {
    try {
      await api.delete(`/bio/spiritual/${tId}`)
      showNotification('🗑️ هدف معنوی حذف شد.')
      const spRes = await api.get('/bio/spiritual')
      spiritualTrackers.value = [...spRes.data]
    } catch (e) { console.error(e) }
  }
}

onMounted(() => { fetchData() })
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    
    <!-- پیام اعلان سیستم -->
    <div v-if="notificationMsg" class="fixed top-20 left-1/2 -translate-x-1/2 z-[10000] px-6 py-3.5 rounded-2xl bg-emerald-600 text-white font-black shadow-2xl animate-bounce flex items-center gap-2 border border-emerald-400">
      <CheckCircle class="w-5 h-5 text-yellow-300" />
      <span>{{ notificationMsg }}</span>
    </div>

    <!-- هدر اصلی شاخص‌های سلامت (Health Pulse Summary Bar) -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
      <div class="glass-card p-4 rounded-2xl border border-white/10 text-center space-y-1">
        <span class="text-[11px] font-bold text-gray-400 block">🟢 کالری دریافتی امروز</span>
        <span class="text-2xl font-black text-emerald-400 dir-ltr block">{{ totalCaloriesIntakeToday }} kcal</span>
      </div>

      <div class="glass-card p-4 rounded-2xl border border-white/10 text-center space-y-1">
        <span class="text-[11px] font-bold text-gray-400 block">🔴 کالری سوزانده شده امروز</span>
        <span class="text-2xl font-black text-rose-400 dir-ltr block">{{ totalCaloriesBurnedToday }} kcal</span>
      </div>

      <div class="glass-card p-4 rounded-2xl border border-white/10 text-center space-y-1">
        <span class="text-[11px] font-bold text-gray-400 block">⚡ کالری مجاز باقی‌مانده</span>
        <span class="text-2xl font-black text-amber-400 dir-ltr block">{{ remainingCaloriesToday }} kcal</span>
      </div>

      <div class="glass-card p-4 rounded-2xl border border-white/10 text-center space-y-1">
        <span class="text-[11px] font-bold text-gray-400 block">🌱 طبع غالب غذایی امروز</span>
        <span class="text-base font-black text-teal-300 block">{{ todayDominantTemperament }}</span>
      </div>

      <div class="glass-card p-4 rounded-2xl border border-white/10 text-center space-y-1 col-span-2 md:col-span-1">
        <span class="text-[11px] font-bold text-gray-400 block">⚖️ وضعیت وزن نسبت به هدف</span>
        <span class="text-xs font-black text-blue-300 block leading-snug">
          {{ targetWeightStatusText }}
        </span>
      </div>
    </div>

    <!-- هدر ناوبری تب‌ها -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 rounded-3xl border border-white/10">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-gradient-to-br from-rose-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-rose-500/20">
          <HeartPulse class="w-8 h-8 text-white animate-pulse" />
        </div>
        <div>
          <h2 class="text-2xl font-black text-white">پایش زیست، سلامت و امور معنوی</h2>
          <p class="text-xs text-gray-400 mt-1">مدیریت زیست، ورزش، تغذیه و روتین‌های معنوی با پشتیبانی AI</p>
        </div>
      </div>

      <div class="flex items-center gap-2 p-1.5 bg-white/5 rounded-2xl border border-white/10 overflow-x-auto">
        <button @click="activeTab = 'spiritual'" :class="activeTab === 'spiritual' ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'" class="px-4 py-2.5 rounded-xl text-xs font-black transition flex items-center gap-2 whitespace-nowrap"><Moon class="w-4 h-4" /> امور معنوی</button>
        <button @click="activeTab = 'workout'" :class="activeTab === 'workout' ? 'bg-gradient-to-r from-rose-600 to-orange-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'" class="px-4 py-2.5 rounded-xl text-xs font-black transition flex items-center gap-2 whitespace-nowrap"><Dumbbell class="w-4 h-4" /> ورزش و فعالیت</button>
        <button @click="activeTab = 'nutrition'" :class="activeTab === 'nutrition' ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'" class="px-4 py-2.5 rounded-xl text-xs font-black transition flex items-center gap-2 whitespace-nowrap"><Utensils class="w-4 h-4" /> تغذیه و وعده‌ها</button>
        <button @click="activeTab = 'health'" :class="activeTab === 'health' ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'" class="px-4 py-2.5 rounded-xl text-xs font-black transition flex items-center gap-2 whitespace-nowrap"><Scale class="w-4 h-4" /> مشخصات فیزیکی و وزن</button>
      </div>
    </div>

    <!-- ۱. امور معنوی -->
    <div v-if="activeTab === 'spiritual'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-bold text-white flex items-center gap-2"><Moon class="w-5 h-5 text-purple-400" /> پیگیری اهداف معنوی</h3>
        <button @click="isEditingSpiritual = false; spiritualForm = { title: 'نماز قضا', tracker_type: 'prayer_qada', total_needed: 360, completed_count: 0, unit: 'روز', register_date: todayISO, last_action_date: todayISO }; showSpiritualModal = true" class="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl flex items-center gap-2 transition shadow-lg shadow-purple-600/30"><Plus class="w-4 h-4" /> افزودن هدف معنوی</button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="tracker in spiritualTrackers" :key="tracker.id" class="glass-card p-6 rounded-3xl border border-white/10 space-y-4 hover:border-purple-500/50 transition duration-300 relative">
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-black text-white text-lg">{{ tracker.title }}</h4>
              <p class="text-xs text-purple-300 font-bold mt-0.5">واحد: {{ tracker.unit || 'روز' }}</p>
            </div>
            <div class="flex items-center gap-1.5">
              <button @click="editSpiritualTracker(tracker)" class="p-1.5 hover:bg-white/10 text-gray-300 hover:text-white rounded-lg transition" title="ویرایش"><Edit3 class="w-4 h-4" /></button>
              <button @click="deleteSpiritualTracker(tracker.id)" class="p-1.5 hover:bg-red-500/20 text-red-400 rounded-lg transition" title="حذف"><Trash2 class="w-4 h-4" /></button>
            </div>
          </div>

          <div class="space-y-1.5">
            <div class="flex justify-between text-xs text-gray-400 font-bold">
              <span>اداشده: {{ tracker.completed_count }} {{ tracker.unit || 'روز' }}</span>
              <span>از کل: {{ tracker.total_needed }} {{ tracker.unit || 'روز' }}</span>
            </div>
            <div class="w-full h-3 bg-white/10 rounded-full overflow-hidden p-0.5">
              <div class="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-500 shadow-md" :style="{ width: Math.min(100, (tracker.completed_count / (tracker.total_needed || 1)) * 100) + '%' }"></div>
            </div>
          </div>

          <div class="pt-2 border-t border-white/5 grid grid-cols-2 gap-2 text-[11px] text-gray-400">
            <div><span class="block text-[10px] text-gray-500">تاریخ ثبت:</span><span class="font-bold text-gray-300">{{ toShamsiDisplay(tracker.register_date) || '--' }}</span></div>
            <div class="text-left"><span class="block text-[10px] text-gray-500">آخرین اقدام:</span><span class="font-bold text-purple-300">{{ toShamsiDisplay(tracker.last_action_date) || '--' }}</span></div>
          </div>

          <button @click="incrementSpiritual(tracker.id)" class="w-full py-2.5 bg-purple-600/30 hover:bg-purple-600 text-purple-200 hover:text-white font-bold text-xs rounded-xl border border-purple-500/30 transition flex items-center justify-center gap-1.5 shadow-md"><Plus class="w-4 h-4" /> ثبت روزانه (+۱ {{ tracker.unit || 'روز' }})</button>
        </div>
      </div>
    </div>

    <!-- ۲. ورزش و فعالیت بدنی -->
    <div v-if="activeTab === 'workout'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 glass-card p-6 rounded-3xl border border-white/10 space-y-4">
        <h3 class="text-lg font-bold text-white flex items-center gap-2"><Dumbbell class="w-5 h-5 text-rose-400" /> {{ isEditingWorkout ? 'ویرایش ورزش' : 'ثبت ورزش جدید' }}</h3>

        <form @submit.prevent="saveWorkout" class="space-y-4 text-right">
          <div class="space-y-1">
            <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ ثبت سیستم</label>
            <DateInputPersian v-model="workoutForm.log_date" placeholder="تاریخ ورزش" />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">نوع ورزش (دسته‌بندی گجت‌ها)</label>
            <select v-model="workoutForm.workout_type" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none">
              <option v-for="cat in exerciseCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">مدت زمان (دقیقه)</label>
            <input v-model="workoutForm.duration_minutes" type="number" min="1" class="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs outline-none" />
          </div>

          <!-- اکشن متحرک AI مربی ورزشی -->
          <div class="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold text-rose-300">کالری تخمینی:</span>
              <span class="text-lg font-black text-white dir-ltr">{{ workoutForm.calories_burned }} kcal</span>
            </div>
            <div v-if="aiError" class="p-2 rounded-xl bg-red-500/20 text-red-300 text-xs font-bold flex items-center gap-1"><AlertCircle class="w-4 h-4 shrink-0" /> {{ aiError }}</div>
            
            <button type="button" @click="estimateWorkoutAI" :disabled="aiLoadingWorkout" class="w-full py-2.5 bg-gradient-to-r from-rose-600 to-orange-600 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-lg disabled:opacity-50">
              <Loader2 class="w-4 h-4 animate-spin text-yellow-300" v-if="aiLoadingWorkout" />
              <Sparkles class="w-4 h-4 text-yellow-300" v-else />
              <span>{{ aiLoadingWorkout ? 'در حال تحلیل هوشمند و استخراج کالری...' : '✨ AI مربی ورزشی' }}</span>
            </button>
          </div>

          <button type="submit" class="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-black text-xs rounded-xl shadow-lg transition">ذخیره فعالیت ورزشی</button>
        </form>
      </div>

      <div class="lg:col-span-2 glass-card p-6 rounded-3xl border border-white/10">
        <h3 class="text-lg font-bold text-white mb-4">تاریخچه تمرینات و فعالیت بدنی</h3>
        <div class="space-y-3 max-h-[500px] overflow-y-auto custom-scrollbar">
          <div v-for="log in workoutLogs" :key="log.id" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="text-3xl p-1 bg-white/5 rounded-2xl border border-white/10 flex items-center justify-center w-12 h-12">
                {{ getExerciseEmoji(log.workout_type) }}
              </div>
              <div>
                <h4 class="font-bold text-white text-sm">{{ log.workout_type }}</h4>
                <p class="text-xs text-gray-400 flex items-center gap-2 mt-0.5"><Calendar class="w-3 h-3 text-rose-300" /> {{ toShamsiDisplay(log.log_date) }} | {{ log.log_time }}</p>
              </div>
            </div>

            <div class="flex items-center gap-4">
              <div class="text-left">
                <span class="text-sm font-black text-rose-400 block">{{ log.calories_burned }} کالری</span>
                <span class="text-xs text-gray-400 font-bold">{{ log.duration_minutes }} دقیقه</span>
              </div>
              <div class="flex items-center gap-1">
                <button @click="editWorkout(log)" class="p-1.5 hover:bg-white/10 text-gray-300 rounded-lg" title="ویرایش"><Edit3 class="w-4 h-4" /></button>
                <button @click="deleteWorkout(log.id)" class="p-1.5 hover:bg-red-500/20 text-red-400 rounded-lg" title="حذف"><Trash2 class="w-4 h-4" /></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ۳. تغذیه و وعده‌ها -->
    <div v-if="activeTab === 'nutrition'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 glass-card p-6 rounded-3xl border border-white/10 space-y-4">
        <h3 class="text-lg font-bold text-white flex items-center gap-2 mb-4"><Utensils class="w-5 h-5 text-emerald-400" /> {{ isEditingMeal ? 'ویرایش وعده غذایی' : 'ثبت وعده غذایی' }}</h3>

        <form @submit.prevent="saveMeal" class="space-y-4 text-right">
          <div class="space-y-1">
            <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ وعده</label>
            <DateInputPersian v-model="mealForm.log_date" placeholder="تاریخ وعده" />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">وعده غذایی</label>
            <select v-model="mealForm.meal_type" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none"><option value="صبحانه">🌅 صبحانه</option><option value="ناهار">☀️ ناهار</option><option value="شام">🌙 شام</option><option value="میان‌وعده">🍎 میان‌وعده</option></select>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">نام غذا</label>
            <input v-model="mealForm.food_name" type="text" placeholder="مثلاً: قورمه سبزی با برنج" class="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs outline-none" />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">مقدار و واحد مصرفی</label>
            <input v-model="mealForm.portion_unit" type="text" placeholder="مثلاً: ۱۰ قاشق غذاخوری" class="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs outline-none" />
          </div>

          <!-- اکشن متحرک AI کارشناس تغذیه -->
          <div class="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 space-y-2">
            <div class="flex justify-between items-center text-xs"><span class="font-bold text-emerald-300">کالری:</span><span class="font-black text-white text-base dir-ltr">{{ mealForm.calories }} kcal</span></div>
            <div class="flex justify-between items-center text-xs"><span class="font-bold text-emerald-300">طبع تخمینی:</span><span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-200 font-bold">🌱 {{ mealForm.temperament }}</span></div>
            <div v-if="aiError" class="p-2 rounded-xl bg-red-500/20 text-red-300 text-xs font-bold flex items-center gap-1"><AlertCircle class="w-4 h-4 shrink-0" /> {{ aiError }}</div>
            
            <button type="button" @click="estimateMealAI" :disabled="aiLoadingMeal" class="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-lg disabled:opacity-50">
              <Loader2 class="w-4 h-4 animate-spin text-yellow-300" v-if="aiLoadingMeal" />
              <Sparkles class="w-4 h-4 text-yellow-300" v-else />
              <span>{{ aiLoadingMeal ? 'در حال تحلیل هوشمند غذا و طبع...' : '✨ AI کارشناس تغذیه' }}</span>
            </button>
          </div>

          <button type="submit" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs rounded-xl shadow-lg transition">ذخیره وعده غذایی</button>
        </form>
      </div>

      <div class="lg:col-span-2 glass-card p-6 rounded-3xl border border-white/10">
        <h3 class="text-lg font-bold text-white mb-4">دفترچه تغذیه و وعده‌ها</h3>
        <div class="space-y-3 max-h-[500px] overflow-y-auto custom-scrollbar">
          <div v-for="log in mealLogs" :key="log.id" class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold"><Utensils class="w-5 h-5" /></div>
              <div>
                <h4 class="font-bold text-white text-sm">{{ log.food_name }} ({{ log.meal_type }})</h4>
                <p class="text-xs text-gray-400 flex items-center gap-2 mt-0.5">مقدار: {{ log.portion_unit }} | {{ toShamsiDisplay(log.log_date) }}</p>
              </div>
            </div>

            <div class="flex items-center gap-4">
              <div class="text-left">
                <span class="text-xs px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 font-bold block mb-1">طبع: {{ log.temperament || 'معتدل' }}</span>
                <span class="text-sm font-black text-emerald-400 block dir-ltr">{{ log.calories }} kcal</span>
              </div>
              <div class="flex items-center gap-1">
                <button @click="editMeal(log)" class="p-1.5 hover:bg-white/10 text-gray-300 rounded-lg" title="ویرایش"><Edit3 class="w-4 h-4" /></button>
                <button @click="deleteMeal(log.id)" class="p-1.5 hover:bg-red-500/20 text-red-400 rounded-lg" title="حذف"><Trash2 class="w-4 h-4" /></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ۴. مشخصات فیزیکی و وزن هدف -->
    <div v-if="activeTab === 'health'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6 rounded-3xl border border-white/10 space-y-4">
        <h3 class="text-lg font-bold text-white flex items-center gap-2"><Scale class="w-5 h-5 text-blue-400" /> مشخصات فیزیکی و وزن هدف</h3>

        <div class="p-3.5 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-200 text-xs leading-relaxed flex items-start gap-2.5">
          <Info class="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <strong>💡 نکته راهنما:</strong> این اطلاعات مبنای تحلیل هوش مصنوعی برای BMR، TDEE و تخمین‌های کالری است. شما می‌توانید روزانه مشخصات جدید وارد کنید؛ برای هر روز تنها **آخرین رکورد ثبت‌شده آن روز** آرشیو گردیده و مبنا قرار می‌گیرد.
          </div>
        </div>

        <form @submit.prevent="saveBiometrics" class="space-y-4 text-right">
          <div class="space-y-1">
            <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ ثبت شاخص امروز</label>
            <DateInputPersian v-model="biometricsForm.log_date" placeholder="تاریخ ثبت شاخص" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">وزن فعلی (کیلوگرم)</label>
              <input v-model="biometricsForm.weight" type="number" step="0.1" required class="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs outline-none" />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">وزن هدف (کیلوگرم)</label>
              <input v-model="biometricsForm.target_weight" type="number" step="0.1" required class="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">قد (سانتی‌متر)</label>
              <input v-model="biometricsForm.height" type="number" required class="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs outline-none" />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">جنسیت</label>
              <select v-model="biometricsForm.gender" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none"><option value="مرد">مرد</option><option value="زن">زن</option></select>
            </div>
          </div>

          <div class="space-y-1">
            <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ تولد (برای سن دقیق AI)</label>
            <DateInputPersian v-model="biometricsForm.birth_date" placeholder="تاریخ تولد" />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">سطح فعالیت روزانه</label>
            <select v-model="biometricsForm.activity_level" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none">
              <option value="نشسته">نشسته (کمترین تحرک)</option>
              <option value="سبک">سبک (۱ تا ۳ روز ورزش)</option>
              <option value="متوسط">متوسط (۳ تا ۵ روز ورزش)</option>
              <option value="پرتحرک">پرتحرک (ورزش حرفه‌ای روزانه)</option>
            </select>
          </div>

          <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-black text-xs rounded-xl shadow-lg transition">آرشیو روزانه مشخصات فیزیکی و بروزرسانی AI</button>
        </form>
      </div>

      <div class="glass-card p-6 rounded-3xl border border-white/10 flex flex-col justify-between space-y-4">
        <div>
          <h3 class="text-lg font-bold text-white mb-2">محاسبات هم‌زمان و زنده فیزیکی</h3>
          <p class="text-xs text-gray-400 mb-4">این محاسبات مبنای تحلیل‌های AI مربی ورزشی و AI کارشناس تغذیه هستند.</p>

          <!-- بنر سبز رنگ تاییدیه ثبت مشخصات فیزیکی با تاریخ و ساعت -->
          <div v-if="lastBiometricsArchivedTime" class="p-3.5 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-200 text-xs leading-relaxed flex items-start gap-2.5 mb-4 animate-in fade-in zoom-in duration-300">
            <CheckCircle class="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div class="font-bold">{{ lastBiometricsArchivedTime }}</div>
          </div>

          <div class="space-y-4">
            <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex justify-between items-center">
              <span class="text-xs font-bold text-gray-300">شاخص توده بدنی (BMI زنده):</span>
              <span class="text-xl font-black text-blue-400 block dir-ltr">{{ liveBMI !== null ? liveBMI : '--' }}</span>
            </div>

            <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex justify-between items-center">
              <span class="text-xs font-bold text-gray-300">نرخ سوخت‌وساز پایه (BMR):</span>
              <span class="text-lg font-black text-purple-400 dir-ltr">{{ Math.round(dailyTargetCalorieBudget / 1.4) }} kcal</span>
            </div>

            <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex justify-between items-center">
              <span class="text-xs font-bold text-gray-300">بودجه کالری مجاز روزانه (TDEE):</span>
              <span class="text-lg font-black text-amber-400 dir-ltr">{{ dailyTargetCalorieBudget }} kcal</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- مودال ساخت / ویرایش هدف معنوی -->
    <Teleport to="body">
      <div v-if="showSpiritualModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="w-full max-w-md glass-card p-6 rounded-3xl border border-white/20 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto custom-scrollbar">
          <h3 class="text-lg font-bold text-white">{{ isEditingSpiritual ? 'ویرایش هدف معنوی' : 'افزودن هدف معنوی جدید' }}</h3>

          <form @submit.prevent="saveSpiritualTracker" class="space-y-4 text-right">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">عنوان (مثلاً: نماز قضا)</label>
              <input v-model="spiritualForm.title" type="text" required class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">واحد اندازه‌گیری</label>
              <input v-model="spiritualForm.unit" type="text" required placeholder="مثلاً: روز، رکعت، مرتبه" class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">کل تعداد مورد نیاز (هدف)</label>
              <input v-model="spiritualForm.total_needed" type="number" required class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div v-if="isEditingSpiritual">
              <label class="block text-xs font-bold text-gray-400 mb-1">تعداد تاکنون ادا شده</label>
              <input v-model="spiritualForm.completed_count" type="number" required class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ ثبت هدف</label>
              <DateInputPersian v-model="spiritualForm.register_date" placeholder="تاریخ ثبت" />
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ آخرین اقدام</label>
              <DateInputPersian v-model="spiritualForm.last_action_date" placeholder="تاریخ آخرین اقدام" />
            </div>

            <div class="flex gap-3 pt-2">
              <button type="submit" class="flex-1 py-3 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-xl shadow-lg">ذخیره هدف معنوی</button>
              <button type="button" @click="showSpiritualModal = false" class="flex-1 py-3 bg-white/10 hover:bg-white/20 text-gray-300 font-bold text-xs rounded-xl">انصراف</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>