<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, Filter, Search, List, 
  Calendar, RefreshCw, AlertTriangle, Eye, ArrowRight, Sparkles, Tag, Target, Flag, Clock, Layers, CheckCircle2, BarChart2,
  Type, Sun, Moon, HelpCircle, BookOpen, Info, CheckSquare, X, Zap,
  RotateCw, Repeat, Circle
} from 'lucide-vue-next'
import api from '@/services/api'
import TaskFormModal from '@/components/TaskFormModal.vue'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate, toGregorianISO } from '@/utils/date'

const themeStore = useThemeStore()
const route = useRoute()

const tasks = ref([])
const goals = ref([])
const subGoals = ref([])
const categories = ref([])

// 📊 حالت نمودار تحلیلی
const showChart = ref(true)  // نمایش/مخفی‌سازی نمودار هفتگی
const chartRange = ref(7)   // 7 | 30 روز
const showTaskModal = ref(false)
const showHelpModal = ref(false)
const editingTask = ref(null)
const selectedTask = ref(null)
const isLoading = ref(false)
const message = ref('')
const messageType = ref('success')
const validationErrors = ref({})

// 🔤 کنترلر اندازه‌ فونت زنده (small | standard | large)
const fontSizeMode = ref('standard') 

// 🎨 کنترلر طیف رنگ فونت (bright = روشن درخشان | dark = تیره با کنتراست بالا)
const fontColorMode = ref('bright') 

const showAllTasks = ref(true)
const showFilters = ref(true)
const quickTab = ref('all') // all, today, overdue, extended, recurring, simple, completed

const filterSearch = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterPriority = ref(null)
const filterGoalId = ref(null)
const filterSubGoalId = ref(null)  // فیلتر گام - وابسته به goal انتخاب‌شده
const filterRecurrence = ref('')
const filterDueDateFrom = ref('')
const filterDueDateTo = ref('')

// 🆕 helper: تاریخ امروز به فرمت ISO میلادی بر اساس timezone محلی (نه UTC)
const getTodayISOLocal = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const form = ref({
  title: '', description: '', register_date: getTodayISOLocal(),
  duration_days: null, category: '', sub_goal_id: null, goal_id: null,
  last_action_date: getTodayISOLocal(), status: 'not_started',
  recurrence_type: 'none', recurrence_interval: 1, recurrence_end_date: '',
  is_infinite_recurrence: true, priority: 0, auto_reschedule: true,
  suggested_due_date: null  // 🆕 تاریخ پیشنهادی برای تمدید
})

const statusLabels = { 'not_started': 'شروع نشده', 'in_progress': 'در حال انجام', 'completed': 'تکمیل', 'on_hold': 'متوقف', 'cancelled': 'لغو شده' }
const priorityLabels = { 0: 'عادی', 1: 'مهم', 2: 'اضطراری' }

const showToast = (msg, type = 'success') => { message.value = msg; messageType.value = type; setTimeout(() => message.value = '', 3000) }

// 🔍 تبدیل تمام اعداد فارسی/عربی به انگلیسی و اسلش به خط تیره جهت مقایسه عددی دقیق
const toEngNums = (str) => {
  if (!str) return ''
  return String(str)
    .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧۸٩'.indexOf(d))
    .replace(/\//g, '-')
}

// 📊 آمار کلی کارها (برای نمودار)
const taskStats = computed(() => {
  const total = tasks.value.length
  const completed = tasks.value.filter(t => t.is_completed).length
  const overdue = tasks.value.filter(t => isTaskOverdue(t)).length
  const today = tasks.value.filter(t => isToday(t)).length
  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0
  return { total, completed, overdue, today, completionRate }
})

// 📊 خلاصه تفکیک بدون تکرار / دوره‌ای (کادر کنار نمودار هفتگی)
// کار دوره‌ای: تکمیل‌شده + در انتظار موعد = انجام‌شده؛ فقط عقب‌افتاده = انجام‌نشده
const taskTypeSummary = computed(() => {
  const fixed = tasks.value.filter(t => !isTaskRecurring(t))
  const rec = tasks.value.filter(t => isTaskRecurring(t))
  const fixedDone = fixed.filter(t => t.is_completed || t.status === 'completed').length
  const recDone = rec.filter(t => !isTaskOverdue(t)).length
  const pct = (d, t) => t > 0 ? Math.round((d / t) * 100) : 0
  return {
    fixedTotal: fixed.length, fixedDone, fixedPct: pct(fixedDone, fixed.length),
    recTotal: rec.length, recDone, recPct: pct(recDone, rec.length)
  }
})

// 📊 داده‌های نمودار میله‌ای (فیکس شده: شنبه در سمت راست، جمعه در سمت چپ)
const chartData = computed(() => {
  const days = chartRange.value
  const buckets = []
  const now = new Date()
  const persianWeekDays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']

  // محاسبه آخرین شنبه (شروع هفته جاری)
  const todayWd = now.getDay() // 0=Sun..6=Sat
  // فاصله روز جاری تا آخرین شنبه (Sat=6 → 0)
  const daysSinceSat = (todayWd + 1) % 7
  // برای days=7: شروع از شنبه همین هفته
  // برای days=30: 23 روز قبل‌تر (4 هفته + 2 روز)
  const startOffset = daysSinceSat + (days - 7)

  const startDate = new Date(now)
  startDate.setDate(startDate.getDate() - startOffset)
  const todayISO = getTodayISOLocal()

  for (let i = 0; i < days; i++) {
    const d = new Date(startDate)
    d.setDate(d.getDate() + i)
    // استفاده از تاریخ محلی (نه UTC) برای سازگاری با timezone
    const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    const wd = d.getDay()
    const persianDayIdx = (wd + 1) % 7
    const dayLabel = days === 7 ? persianWeekDays[persianDayIdx] : String(d.getDate())

    // برنامه‌ریزی‌شده روز: due_date همون روز (شامل تمدیدشده‌ها) یا تاریخ اقدام بعدی دوره‌ای همون روز
    // انجام‌شده روز: (تکمیل‌شده و due همون روز) یا last_action همون روز — هم‌منطق با نمودار داشبورد
    const isoOf = (v) => v ? String(v).split('T')[0] : ''
    let fixedPlanned = 0, recPlanned = 0, fixedDone = 0, recDone = 0
    for (const t of tasks.value) {
      const rec = isTaskRecurring(t)
      const due = isoOf(t.due_date)
      const last = isoOf(t.last_action_date)
      let plannedHere = due !== '' && due === iso
      if (rec && !plannedHere) {
        plannedHere = computeNextActionDateISO(t) === iso
      }
      if (plannedHere) { if (rec) recPlanned++; else fixedPlanned++ }
      const doneHere = (t.is_completed && due !== '' && due === iso) || (last !== '' && last === iso)
      if (doneHere) { if (rec) recDone++; else fixedDone++ }
    }

    const created = tasks.value.filter(t => {
      const rd = t.register_date ? String(t.register_date).split('T')[0] : ''
      return rd === iso
    }).length

    buckets.push({
      date: iso,
      dayLabel,
      isToday: iso === todayISO,
      planned_total: fixedPlanned + recPlanned,
      fixedPlanned,
      recPlanned,
      fixedDone,
      recDone,
      completed: fixedDone + recDone,
      created
    })
  }
  return buckets
})

const maxChartValue = computed(() => {
  const m = Math.max(1, ...chartData.value.map(d => Math.max(d.planned_total || 0, d.completed || 0)))
  return m
})

// پاپ‌آپ تفکیک ستون نمودار (با کلیک روی هر ستون)
const selectedBar = ref(null)
const openBarDetail = (b) => {
  selectedBar.value = (selectedBar.value && selectedBar.value.date === b.date) ? null : b
}

// ابعاد ستون هر روز: ارتفاع کل با برنامه‌ریزی‌شده متناسب، بخش سبز پایین = انجام‌شده
const taskBar = (b) => {
  const planned = b.planned_total || 0
  const done = b.completed || 0
  const total = Math.max(planned, done)
  const max = maxChartValue.value || 1
  return {
    planned,
    done,
    height: total > 0 ? Math.max(8, (total / max) * 100) : 0,
    doneH: total > 0 ? (Math.min(done, total) / total) * 100 : 0,
    restH: total > 0 && planned > done ? ((planned - done) / total) * 100 : 0
  }
}

// بررسی تعلق کار به کارهای امروز (شامل تاریخ پیشنهادی تمدید)
const isToday = (task) => {
  if (!task) return false
  const todayLocal = getTodayISOLocal()
  // پشتیبانی از هر دو فرمت: ISO با T (مثل 2026-09-04T00:00:00) و فرمت ساده
  const d = task.due_date ? String(task.due_date).split('T')[0] : ''
  const r = task.register_date ? String(task.register_date).split('T')[0] : ''
  const l = task.last_action_date ? String(task.last_action_date).split('T')[0] : ''
  const s = task.suggested_due_date ? String(task.suggested_due_date).split('T')[0] : ''

  return d === todayLocal || r === todayLocal || l === todayLocal || s === todayLocal
}

// بررسی کار دوره‌ای
const isTaskRecurring = (task) => {
  return Boolean(task.recurrence_type && task.recurrence_type !== 'none')
}

// 🏷️ برچسب فارسی نوع تکرار
const recurrenceLabel = (type) => {
  const map = { daily: 'روزانه', weekly: 'هفتگی', monthly: 'ماهانه', yearly: 'سالانه' }
  return map[type] || 'دوره‌ای'
}

// 🗓️ محاسبه تاریخ اقدام / مهلت بعدی کار
const getNextActionDate = (task) => {
  if (!task) return 'تعیین نشده'
  if (!task.due_date && !task.last_action_date && !task.register_date) return 'تعیین نشده'
  
  if (isTaskRecurring(task) && (task.is_completed || task.status === 'completed' || task.status === 'not_started')) {
    const baseDate = task.last_action_date ? new Date(task.last_action_date) : new Date()
    const interval = Number(task.recurrence_interval) || 1
    
    if (task.recurrence_type === 'daily') baseDate.setDate(baseDate.getDate() + interval)
    else if (task.recurrence_type === 'weekly') baseDate.setDate(baseDate.getDate() + (interval * 7))
    else if (task.recurrence_type === 'monthly') baseDate.setMonth(baseDate.getMonth() + interval)
    else if (task.recurrence_type === 'yearly') baseDate.setFullYear(baseDate.getFullYear() + interval)

    // استفاده از تاریخ محلی (نه UTC) برای سازگاری با timezone
    const localISO = `${baseDate.getFullYear()}-${String(baseDate.getMonth() + 1).padStart(2, '0')}-${String(baseDate.getDate()).padStart(2, '0')}`
    return formatDate(localISO)
  }

  return formatDate(task.due_date || task.register_date || task.last_action_date)
}

// 🚦 تشخیص وضعیت کار برای تعیین رنگ/برچسب (سلسله‌مراتبی)
// 1) completed | 2) today (اگر تاریخ پیشنهادی == امروز، اولویت با today دارد) | 3) extended | 4) overdue | 5) pending
const getTaskStatus = (task) => {
  if (!task) return 'pending'
  if (task.is_completed || task.status === 'completed') return 'completed'

  // تاریخ امروز به فرمت ISO محلی (نه UTC) - برای سازگاری با timezone کاربر
  const todayISO = getTodayISOLocal()

  // 🆕 اولویت ۱: اگر تاریخ پیشنهادی == امروز → امروز
  if (task.suggested_due_date) {
    const rawSug = String(task.suggested_due_date)
    const normSug = toGregorianISO ? toGregorianISO(rawSug) : (rawSug.includes('/') ? rawSug.replace(/\//g, '-') : rawSug)
    const sugISO = normSug ? String(normSug).split('T')[0] : String(rawSug).split('T')[0]
    if (sugISO === todayISO) return 'today'
  }

  // اولویت ۲: اگر تاریخ اقدام بعدی == امروز → امروز
  if (isToday(task)) return 'today'

  // محاسبه تاریخ اقدام بعدی
  const nextISO = computeNextActionDateISO(task)

  // اگر تاریخ اقدام بعدی قبل از امروز است → عقب‌افتاده
  if (nextISO && nextISO < todayISO) {
    // اگر تاریخ پیشنهادی تنظیم شده و هنوز نگذشته → تمدید شده
    if (task.suggested_due_date) {
      const rawSug = String(task.suggested_due_date)
      const normSug = toGregorianISO ? toGregorianISO(rawSug) : (rawSug.includes('/') ? rawSug.replace(/\//g, '-') : rawSug)
      const sugISO = normSug ? String(normSug).split('T')[0] : String(rawSug).split('T')[0]
      if (sugISO > todayISO) return 'extended'
    }
    return 'overdue'
  }
  return 'pending'
}

// 🚨 بررسی هوشمند و قطعی کار عقب‌افتاده (از تاریخ اقدام بعدی محاسبه‌شده)
const isTaskOverdue = (task) => {
  if (!task) return false
  if (task.is_completed || task.status === 'completed') return false
  if (isToday(task)) return false

  // تاریخ اقدام بعدی (همان منطق getNextActionDate)
  const nextDateStr = computeNextActionDateISO(task)
  if (!nextDateStr) return false

  const todayISO = getTodayISOLocal()
  return nextDateStr < todayISO
}

// 🗓️ محاسبه تاریخ اقدام بعدی به فرمت ISO (بدون تبدیل شمسی) - منبع مشترک
const computeNextActionDateISO = (task) => {
  if (!task) return ''
  // helper: تبدیل شیء Date به ISO محلی
  const toLocalISO = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  // اگر تاریخ پیشنهادی برای تمدید تنظیم شده باشد، از آن به‌عنوان مرجع استفاده شود
  // نرمال‌سازی تاریخ پیشنهادی به ISO میلادی (در صورت فرمت شمسی YYYY/MM/DD)
  if (task.suggested_due_date) {
    const raw = String(task.suggested_due_date)
    const iso = toGregorianISO ? toGregorianISO(raw) : (raw.includes('/') ? raw.replace(/\//g, '-') : raw)
    return iso ? String(iso).split('T')[0] : String(raw).split('T')[0]
  }
  // برای کار دوره‌ای: last_action_date + فاصله تکرار
  if (isTaskRecurring(task) && (task.is_completed || task.status === 'completed' || task.status === 'not_started')) {
    const baseDate = task.last_action_date ? new Date(task.last_action_date) : new Date()
    const interval = Number(task.recurrence_interval) || 1
    if (task.recurrence_type === 'daily') baseDate.setDate(baseDate.getDate() + interval)
    else if (task.recurrence_type === 'weekly') baseDate.setDate(baseDate.getDate() + (interval * 7))
    else if (task.recurrence_type === 'monthly') baseDate.setMonth(baseDate.getMonth() + interval)
    else if (task.recurrence_type === 'yearly') baseDate.setFullYear(baseDate.getFullYear() + interval)
    return toLocalISO(baseDate)
  }
  // برای همه کارها: اولویت due_date > register_date > last_action_date
  return (task.due_date || task.register_date || task.last_action_date || '').toString().split('T')[0]
}

// 🔤 محاسبه کلاس‌های اندازه فونت پویا
const fontSizeClasses = computed(() => {
  if (fontSizeMode.value === 'small') {
    return {
      title: 'text-xs sm:text-sm font-bold',
      desc: 'text-[10px] sm:text-xs',
      badge: 'text-[9px] sm:text-[10px] font-bold px-1.5 py-0.5',
      meta: 'text-[10px] sm:text-[11px] font-bold',
      tab: 'text-[11px] sm:text-xs font-bold px-2.5 py-1.5'
    }
  } else if (fontSizeMode.value === 'large') {
    return {
      title: 'text-sm sm:text-lg md:text-xl font-black',
      desc: 'text-xs sm:text-sm font-medium leading-relaxed',
      badge: 'text-[10px] sm:text-xs font-black px-2.5 py-1',
      meta: 'text-xs sm:text-sm font-black',
      tab: 'text-xs sm:text-sm font-black px-4 py-2'
    }
  } else { // standard
    return {
      title: 'text-xs sm:text-base md:text-lg font-black',
      desc: 'text-[11px] sm:text-xs font-normal leading-relaxed',
      badge: 'text-[9px] sm:text-xs font-black px-2 py-0.5 sm:px-2.5 sm:py-1',
      meta: 'text-[10px] sm:text-xs font-bold',
      tab: 'text-[11px] sm:text-xs font-black px-3 py-1.5 sm:px-4 sm:py-2'
    }
  }
})

// 🎨 محاسبه کلاس‌های طیف رنگ پویا
const fontColorClasses = computed(() => {
  if (fontColorMode.value === 'dark') {
    return {
      cardBg: 'bg-slate-100 text-slate-900 border-slate-300 shadow-xl',
      title: 'text-slate-950',
      desc: 'text-slate-800 font-semibold',
      meta: 'text-slate-700 font-bold',
      border: 'border-slate-300'
    }
  } else { // bright (default)
    return {
      cardBg: 'glass-card text-white border-white/10',
      title: 'text-white',
      desc: 'text-gray-200',
      meta: 'text-gray-300',
      border: 'border-white/10'
    }
  }
})

const selectTaskForFocus = (task) => { selectedTask.value = task }
const closeTaskFocus = () => { selectedTask.value = null; focusSuggestedDate.value = null }

// 🆕 تاریخ پیشنهادی برای تمدید (ویرایش از حالت تمرکز)
const focusSuggestedDate = ref(null)
const focusEditingSuggested = ref(false)

watch(selectedTask, (t) => {
  if (t) {
    focusSuggestedDate.value = t.suggested_due_date || null
    focusEditingSuggested.value = false
  }
})

// 🆕 ذخیره تاریخ پیشنهادی از داخل حالت تمرکز
const saveSuggestedFromFocus = async () => {
  if (!selectedTask.value) return

  // تبدیل تاریخ شمسی به میلادی در صورت نیاز
  let valueToSave = focusSuggestedDate.value
  if (valueToSave && typeof valueToSave === 'string') {
    // اگر شبیه تاریخ شمسی است (مثل "۱۴۰۵/۰۶/۱۴" یا "1405/06/14")
    if (/[۰-۹]/.test(valueToSave) || /^\d{4}\/\d{2}\/\d{2}$/.test(valueToSave)) {
      const iso = toGregorianISO(valueToSave)
      if (iso) valueToSave = iso
    }
  }
  // اگر خالی است، null ذخیره شود
  if (!valueToSave || (typeof valueToSave === 'string' && !valueToSave.trim())) {
    valueToSave = null
  }

  try {
    isLoading.value = true
    await api.put(`/tasks/${selectedTask.value.id}`, { suggested_due_date: valueToSave })

    // به‌روزرسانی selectedTask (با ایجاد شیء جدید برای اطمینان از reactivity)
    const updatedSelected = { ...selectedTask.value, suggested_due_date: valueToSave }
    selectedTask.value = updatedSelected

    // به‌روزرسانی لیست اصلی (با ایجاد آرایه جدید برای اطمینان از reactivity)
    const idx = tasks.value.findIndex(t => t.id === updatedSelected.id)
    if (idx !== -1) {
      const newTasks = [...tasks.value]
      newTasks[idx] = { ...newTasks[idx], suggested_due_date: valueToSave }
      tasks.value = newTasks
    }

    // هماهنگ‌سازی focusSuggestedDate
    focusSuggestedDate.value = valueToSave
    focusEditingSuggested.value = false

    // اجبار به re-render
    await nextTick()

    showToast('✅ تاریخ پیشنهادی ذخیره شد')
  } catch (e) {
    showToast('❌ خطا در ذخیره تاریخ پیشنهادی', 'error')
  } finally {
    isLoading.value = false
  }
}

const fetchTasks = async () => {
  try {
    const res = await api.get('/tasks')
    tasks.value = Array.isArray(res.data) ? res.data : []
    if (selectedTask.value) {
      const updated = tasks.value.find(t => t.id === selectedTask.value.id)
      if (updated) selectedTask.value = updated
    }
  } catch (e) {
    showToast('⚠️ خطا در بارگذاری کارها', 'error')
  }
}

const fetchGoals = async () => { try { const res = await api.get('/goals'); goals.value = Array.isArray(res.data) ? res.data : [] } catch (e) {} }
const fetchSubGoals = async (goalId) => { if (!goalId) { subGoals.value = []; return }; try { const res = await api.get(`/roadmap/goal/${goalId}/subgoals`); subGoals.value = Array.isArray(res.data) ? res.data : [] } catch (e) {} }
const fetchCategories = async () => { try { const res = await api.get('/tasks/categories'); categories.value = Array.isArray(res.data) ? res.data : [] } catch (e) {} }

// 🔍 کادر جستجوی دقیق و هوشمند همراه با کلیه فیلترهای پیشرفته
const filteredTasks = computed(() => {
  let result = tasks.value || []

  if (quickTab.value === 'today') {
    result = result.filter(t => isToday(t))
  } else if (quickTab.value === 'overdue') {
    result = result.filter(t => isTaskOverdue(t))
  } else if (quickTab.value === 'extended') {
    result = result.filter(t => getTaskStatus(t) === 'extended')
  } else if (quickTab.value === 'recurring') {
    result = result.filter(t => isTaskRecurring(t))
  } else if (quickTab.value === 'simple') {
    result = result.filter(t => !isTaskRecurring(t))
  } else if (quickTab.value === 'completed') {
    result = result.filter(t => t.is_completed || t.status === 'completed')
  }

  // ۱. کادر جستجوی دقیق عنوان و توضیحات
  if (filterSearch.value && filterSearch.value.trim()) {
    const q = filterSearch.value.toLowerCase()
    result = result.filter(t => 
      (t.title && t.title.toLowerCase().includes(q)) ||
      (t.description && t.description.toLowerCase().includes(q))
    )
  }

  // ۲. سایر فیلترهای پیشرفته
  if (filterCategory.value) result = result.filter(t => t.category === filterCategory.value)
  if (filterStatus.value) result = result.filter(t => t.status === filterStatus.value)
  if (filterPriority.value !== null && filterPriority.value !== '') result = result.filter(t => t.priority === Number(filterPriority.value))
  if (filterGoalId.value) result = result.filter(t => t.goal_id === filterGoalId.value)
  if (filterSubGoalId.value) result = result.filter(t => t.sub_goal_id === filterSubGoalId.value)
  if (filterRecurrence.value === 'has') result = result.filter(t => isTaskRecurring(t))
  if (filterRecurrence.value === 'none') result = result.filter(t => !isTaskRecurring(t))
  // فیلتر تاریخ: تاریخ اقدام بعدی (شامل تاریخ تمدیدشده) در بازه باشد
  if (filterDueDateFrom.value || filterDueDateTo.value) {
    result = result.filter(t => {
      const iso = computeNextActionDateISO(t)
      if (!iso) return false
      if (filterDueDateFrom.value && iso < filterDueDateFrom.value) return false
      if (filterDueDateTo.value && iso > filterDueDateTo.value) return false
      return true
    })
  }

  return result
})

const activeFilterCount = computed(() => {
  let c = 0
  if (filterSearch.value) c++
  if (filterCategory.value) c++
  if (filterStatus.value) c++
  if (filterPriority.value !== null && filterPriority.value !== '') c++
  if (filterGoalId.value) c++
  if (filterSubGoalId.value) c++
  if (filterRecurrence.value) c++
  if (filterDueDateFrom.value || filterDueDateTo.value) c++
  return c
})

const resetFilters = () => {
  filterSearch.value = ''; filterCategory.value = ''; filterStatus.value = ''
  filterPriority.value = null; filterGoalId.value = null; filterSubGoalId.value = null; filterRecurrence.value = ''
  filterDueDateFrom.value = ''; filterDueDateTo.value = ''; quickTab.value = 'all'
  // وقتی goal ریست می‌شه، لیست sub_goal ها هم پاک شه
  if (filterGoalId.value === null) subGoals.value = []
}

// وقتی goal عوض می‌شه، sub_goal های مربوطه fetch شن + فیلتر sub_goal ریست شه
watch(filterGoalId, (newGoalId) => {
  filterSubGoalId.value = null
  if (newGoalId) fetchSubGoals(newGoalId)
  else subGoals.value = []
})

const openNewForm = () => {
  form.value = { 
    title: '', description: '', register_date: getTodayISOLocal(), 
    duration_days: null, category: '', sub_goal_id: null, goal_id: null, 
    last_action_date: getTodayISOLocal(), status: 'not_started', recurrence_type: 'none', 
    recurrence_interval: 1, recurrence_end_date: '', is_infinite_recurrence: true, priority: 0, auto_reschedule: true 
  }
  editingTask.value = null; subGoals.value = []; validationErrors.value = {}; showTaskModal.value = true
}

const openEditForm = (task) => {
  form.value = {
    title: task.title, description: task.description || '',
    register_date: task.register_date || '', duration_days: task.duration_days || null,
    due_date: task.due_date || '',
    category: task.category || '', sub_goal_id: task.sub_goal_id || null,
    goal_id: task.goal_id || null, last_action_date: task.last_action_date || null,
    status: task.status || 'not_started', recurrence_type: task.recurrence_type || 'none',
    recurrence_interval: task.recurrence_interval || 1,
    recurrence_end_date: task.recurrence_end_date || '',
    is_infinite_recurrence: task.is_infinite_recurrence !== undefined ? task.is_infinite_recurrence : true,
    priority: task.priority ?? 0, auto_reschedule: task.auto_reschedule !== undefined ? task.auto_reschedule : true,
    suggested_due_date: task.suggested_due_date || null  // 🆕 تاریخ پیشنهادی
  }
  editingTask.value = task; fetchSubGoals(task.goal_id); validationErrors.value = {}; showTaskModal.value = true
}

const onGoalChange = () => { form.value.sub_goal_id = null; fetchSubGoals(form.value.goal_id) }

// ⚡ ذخیره آنی و بستن سریع مودال همراه با همگام‌سازی موازی داده‌ها
const saveTask = async () => {
  try {
    isLoading.value = true
    const data = { ...form.value }
    showTaskModal.value = false // بستن فوری مودال برای سرعت حداکثری

    if (editingTask.value) {
      await api.put(`/tasks/${editingTask.value.id}`, data)
      showToast('✅ کار بروزرسانی شد')
    } else {
      await api.post('/tasks', data)
      showToast('✅ کار جدید ساخته شد')
    }
    
    // واکشی موازی فوق‌العاده سریع
    await Promise.all([fetchTasks(), fetchGoals()])
  } catch (e) { 
    showToast('❌ خطا در ذخیره کار', 'error')
    showTaskModal.value = true
  } finally { 
    isLoading.value = false 
  }
}

const toggleTask = async (task) => {
  try {
    const today = getTodayISOLocal()
    const isCurrentlyCompleted = task.is_completed || task.status === 'completed'
    const newCompletedState = !isCurrentlyCompleted
    const newStatus = newCompletedState ? 'completed' : 'not_started'

    // به‌روزرسانی لوکال آنی قبل از بازگشت پاسخ سرور
    task.is_completed = newCompletedState
    task.status = newStatus
    task.last_action_date = today

    await api.put(`/tasks/${task.id}`, {
      status: newStatus,
      is_completed: newCompletedState,
      last_action_date: today
    })

    if (newCompletedState) {
      showToast(isTaskRecurring(task) ? '🔄 کار انجام شد و برای موعد بعدی فعال می‌ماند' : '🎉 کار با موفقیت تکمیل شد')
    } else {
      showToast('🔄 کار به حالت انجام‌نشده برگشت')
    }

    Promise.all([fetchTasks(), fetchGoals()])
  } catch (e) {
    showToast('❌ خطا در تغییر وضعیت کار', 'error')
    await fetchTasks()
  }
}

const deleteTask = async (id) => { 
  if (!confirm('مطمئنی می‌خوای این کار رو حذف کنی؟')) return
  try { 
    tasks.value = tasks.value.filter(t => t.id !== id)
    if (selectedTask.value && selectedTask.value.id === id) selectedTask.value = null
    showToast('🗑️ کار حذف شد')
    await api.delete(`/tasks/${id}`)
    Promise.all([fetchTasks(), fetchGoals()])
  } catch (e) {} 
}

const applyTabFilter = (tab) => {
  if (tab) {
    quickTab.value = tab
    filterSearch.value = ''
    filterCategory.value = ''
    filterStatus.value = ''
    filterPriority.value = null
    filterGoalId.value = null
    filterRecurrence.value = ''
    filterDueDateFrom.value = ''
    filterDueDateTo.value = ''
  }
}

watch(() => route.query.tab, (newTab) => {
  if (newTab) {
    applyTabFilter(newTab)
    fetchTasks()
  }
})

onMounted(async () => {
  if (route.query.tab) {
    applyTabFilter(route.query.tab)
  }
  await Promise.all([fetchTasks(), fetchGoals(), fetchCategories()])

  // 🔗 لینک از Roadmap یا Goals: خواندن ?goal=X و ?sub=Y از URL
  if (route.query.goal) {
    const gId = Number(route.query.goal)
    if (!isNaN(gId) && goals.value.find(g => g.id === gId)) {
      filterGoalId.value = gId
      await fetchSubGoals(gId)  // sub_goal ها رو fetch کن
      // حالا sub_goal فیلتر رو هم تنظیم کن (اگه پارامتر sub=Y وجود داشت)
      if (route.query.sub) {
        const sId = Number(route.query.sub)
        if (!isNaN(sId)) filterSubGoalId.value = sId
      }
      // 🚀 اگه add=1 بود، مودال افزودن کار رو خودکار باز کن
      if (route.query.add === '1') {
        setTimeout(() => openNewForm(), 100)  // کمی صبر تا filterGoalId اعمال شه
      }
    }
  }
})
</script>

<template>
  <div class="p-3 sm:p-5 md:p-8 max-w-7xl mx-auto relative min-h-screen text-right" dir="rtl" :class="themeStore.currentTheme === 'cyber-digital' ? 'page-bg-tasks' : ''">

    <!-- Toast Message -->
    <div v-if="message" class="fixed top-16 left-1/2 transform -translate-x-1/2 z-[300] px-5 py-2.5 rounded-xl shadow-2xl text-white text-xs md:text-sm font-semibold transition-all duration-300" :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
      <div>
        <h1 class="text-2xl md:text-3xl lg:text-4xl font-black mb-1 flex items-center gap-2.5" :style="{ color: 'var(--text-primary)' }" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''">
          <ListTodo class="w-7 h-7 md:w-8 md:h-8 text-purple-400" /> میز کار
        </h1>
        <p :style="{ color: 'var(--text-secondary)' }" class="text-xs md:text-sm font-bold">مدیریت، زمان‌بندی و پایش پیشرفت کارهای روزانه و دوره‌ای</p>
      </div>

      <!-- 🔤 و 🎨 و 📚 دکمه‌های ابزار سربرگ -->
      <div class="flex gap-2 flex-wrap items-center">
        
        <!-- 📚 کلید راهنمای فارسی -->
        <button @click="showHelpModal = true" class="px-3 py-2 rounded-xl border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 font-black text-xs flex items-center gap-1.5 transition shadow-lg shadow-amber-500/10">
          <HelpCircle class="w-4 h-4 text-amber-400 animate-pulse" />
          <span class="hidden sm:inline">راهنما و مثال‌ها</span>
          <span class="sm:hidden">راهنما</span>
        </button>

        <button @click="showAllTasks = !showAllTasks" class="px-3 py-2 rounded-xl transition flex items-center gap-1.5 text-xs font-bold" :style="showAllTasks ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <List class="w-4 h-4" /> <span class="hidden sm:inline">{{ showAllTasks ? 'کارتی' : 'فشرده' }}</span>
        </button>
        
        <button @click="showFilters = !showFilters" class="px-3 py-2 rounded-xl transition flex items-center gap-1.5 text-xs font-bold relative" :style="{ background: showFilters ? 'var(--accent)' : 'var(--bg-hover)', color: showFilters ? '#fff' : 'var(--text-secondary)' }">
          <Filter class="w-4 h-4" /> <span>فیلترها</span> <span v-if="activeFilterCount > 0" class="w-4 h-4 rounded-full text-white text-[9px] flex items-center justify-center font-bold bg-red-500">{{ activeFilterCount }}</span>
        </button>
        
        <button @click="openNewForm" class="px-3.5 py-2 rounded-xl text-white font-black text-xs md:text-sm transition flex items-center gap-1.5 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
          <Plus class="w-4 h-4" /> <span>کار جدید</span>
        </button>
      </div>
    </div>

    <!-- 🌟 تب‌های فیلتر سریع -->
    <div class="flex items-center gap-2 overflow-x-auto pb-3 mb-5 custom-scrollbar">
      <button @click="applyTabFilter('all')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'all' ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">همه کارها ({{ tasks.length }})</button>
      <button @click="applyTabFilter('today')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'today' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">☀️ کارهای امروز ({{ tasks.filter(t => isToday(t)).length }})</button>
      <button @click="applyTabFilter('overdue')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'overdue' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30 font-black' : 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20']">🚨 عقب‌افتاده‌ها ({{ tasks.filter(t => isTaskOverdue(t)).length }})</button>
      <button @click="applyTabFilter('extended')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'extended' ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/30 font-black' : 'bg-sky-500/10 text-sky-300 hover:bg-sky-500/20 border border-sky-500/30']">🕐 تمدید شده‌ها ({{ tasks.filter(t => getTaskStatus(t) === 'extended').length }})</button>
      <button @click="applyTabFilter('recurring')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'recurring' ? 'bg-amber-500 text-slate-950 font-black shadow-lg shadow-amber-500/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">🔄 کارهای دوره‌ای</button>
      <button @click="applyTabFilter('simple')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'simple' ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30' : 'bg-white/5 text-gray-300 hover:bg-white/10']">📌 کارهای بدون تکرار</button>
      <button @click="applyTabFilter('completed')" class="rounded-xl transition whitespace-nowrap" :class="[fontSizeClasses.tab, quickTab === 'completed' ? 'bg-gray-600 text-white shadow-lg' : 'bg-white/5 text-gray-300 hover:bg-white/10']">✅ تکمیل‌شده‌ها</button>
    </div>

    <!-- 📊 نمودار تحلیلی فعالیت + ۴ کارت KPI + خلاصه نوع کارها -->
    <div v-if="showChart" class="mb-5 grid grid-cols-1 lg:grid-cols-3 gap-4 animate-in fade-in duration-200">
    <div class="glass-card p-4 sm:p-5 rounded-2xl md:rounded-3xl border border-white/10 lg:col-span-2">
      <!-- ۴ کارت KPI -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3 mb-4">
        <div class="p-2.5 sm:p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center gap-2 sm:gap-3">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center flex-shrink-0">
            <ListTodo class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div class="min-w-0">
            <p class="text-[9px] sm:text-[10px] opacity-60 font-bold">کل کارها</p>
            <p class="text-sm sm:text-lg font-black text-blue-300 truncate">{{ taskStats.total }}</p>
          </div>
        </div>
        <div class="p-2.5 sm:p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 sm:gap-3">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div class="min-w-0">
            <p class="text-[9px] sm:text-[10px] opacity-60 font-bold">تکمیل‌شده</p>
            <p class="text-sm sm:text-lg font-black text-emerald-300 truncate">{{ taskStats.completed }}</p>
          </div>
        </div>
        <div class="p-2.5 sm:p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-2 sm:gap-3">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
            <Clock class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div class="min-w-0">
            <p class="text-[9px] sm:text-[10px] opacity-60 font-bold">امروز</p>
            <p class="text-sm sm:text-lg font-black text-amber-300 truncate">{{ taskStats.today }}</p>
          </div>
        </div>
        <div class="p-2.5 sm:p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-2 sm:gap-3">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center flex-shrink-0">
            <AlertTriangle class="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div class="min-w-0">
            <p class="text-[9px] sm:text-[10px] opacity-60 font-bold">عقب‌افتاده</p>
            <p class="text-sm sm:text-lg font-black text-red-300 truncate">{{ taskStats.overdue }}</p>
          </div>
        </div>
      </div>

      <!-- عنوان نمودار + سوییچر بازه -->
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-xs sm:text-sm font-black flex items-center gap-2">
          <BarChart2 class="w-4 h-4 text-purple-400" />
          <span>نمودار {{ chartRange === 7 ? 'هفتگی' : 'ماهانه' }} کارها</span>
        </h3>
        <div class="flex items-center gap-1 p-0.5 bg-black/40 rounded-lg border border-white/10">
          <button @click="chartRange = 7" class="px-2.5 py-1 rounded text-[10px] sm:text-xs font-bold transition"
                  :style="chartRange === 7 ? { background: '#9333ea', color: '#fff' } : { color: 'rgba(255,255,255,0.6)' }">۷ روز</button>
          <button @click="chartRange = 30" class="px-2.5 py-1 rounded text-[10px] sm:text-xs font-bold transition"
                  :style="chartRange === 30 ? { background: '#9333ea', color: '#fff' } : { color: 'rgba(255,255,255,0.6)' }">۳۰ روز</button>
        </div>
      </div>

      <!-- نمودار میله‌ای (شنبه در سمت راست، جمعه در سمت چپ، روز جاری طلایی) -->
      <div class="flex items-end gap-1 h-28 sm:h-32 relative" dir="rtl">
        <div v-for="(b, i) in chartData" :key="b.date" class="flex-1 h-full flex flex-col items-center justify-end gap-0.5 min-w-0 cursor-pointer"
             @click="openBarDetail(b)">
          <!-- تعداد بالای میله (انجام/برنامه) -->
          <span v-if="taskBar(b).planned > 0 || taskBar(b).done > 0" class="text-[8px] sm:text-[9px] font-bold shrink-0"
                :class="b.isToday ? 'text-amber-300' : 'text-blue-300'">{{ taskBar(b).done }}/{{ taskBar(b).planned }}</span>
          <span v-else class="text-[8px] sm:text-[9px] opacity-20 shrink-0">·</span>
          <!-- میله: کل ارتفاع = برنامه (آبی) + بخش سبز پایین = انجام‌شده -->
          <div class="w-full flex-1 flex flex-col items-stretch justify-end overflow-hidden rounded-t gap-px relative min-h-0"
               :style="{
                 boxShadow: b.isToday ? '0 0 12px rgba(251,191,36,0.5)' : 'none',
                 background: b.isToday ? 'linear-gradient(180deg, rgba(251,191,36,0.1), transparent)' : 'transparent'
               }">
            <div class="w-full flex flex-col items-stretch overflow-hidden rounded-t-md ring-1 transition-all"
                 :style="{ height: taskBar(b).height + '%', minHeight: (taskBar(b).height > 0 ? '8px' : '0') }">
              <div v-if="taskBar(b).restH > 0" class="w-full bg-gradient-to-t from-blue-700 to-blue-400"
                   :title="`${formatDate(b.date)} - برنامه: ${taskBar(b).planned}`"
                   :style="{ height: taskBar(b).restH + '%' }"></div>
              <div v-if="taskBar(b).doneH > 0" class="w-full bg-gradient-to-t from-emerald-700 to-emerald-400"
                   :title="`${formatDate(b.date)} - انجام: ${taskBar(b).done} از ${taskBar(b).planned}`"
                   :style="{ height: taskBar(b).doneH + '%' }"></div>
            </div>
          </div>
          <!-- برچسب روز -->
          <span class="text-[8px] sm:text-[9px] truncate w-full text-center shrink-0"
                :class="b.isToday ? 'text-amber-300 font-black' : 'opacity-50'">{{ b.dayLabel }}</span>
        </div>
        <!-- پاپ‌آپ تفکیک ستون: همیشه وسط نمودار (موقعیت ثابت) -->
        <Transition name="popup">
          <div v-if="selectedBar"
               class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 bg-slate-900/98 border border-white/30 backdrop-blur-xl rounded-2xl p-3 shadow-2xl min-w-[170px] text-right">
            <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-white/10">
              <span class="text-xs font-black text-white">{{ selectedBar.dayLabel }}</span>
              <button @click.stop="selectedBar = null" class="text-slate-400 hover:text-white text-xs leading-none">✕</button>
            </div>
            <div class="space-y-1.5 text-[11px]">
              <div class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-sky-400"></span><span class="font-bold text-gray-300">کار ثابت</span></span>
                <span class="font-black text-sky-300">{{ selectedBar.fixedPlanned || 0 }}</span>
              </div>
              <div class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-purple-500"></span><span class="font-bold text-gray-300">انجام ثابت</span></span>
                <span class="font-black text-purple-300">{{ selectedBar.fixedDone || 0 }}</span>
              </div>
              <div class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-amber-400"></span><span class="font-bold text-gray-300">کار دوره‌ای</span></span>
                <span class="font-black text-amber-300">{{ selectedBar.recPlanned || 0 }}</span>
              </div>
              <div class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span><span class="font-bold text-gray-300">انجام دوره‌ای</span></span>
                <span class="font-black text-emerald-300">{{ selectedBar.recDone || 0 }}</span>
              </div>
              <div class="flex items-center justify-between gap-3 pt-1.5 mt-1.5 border-t border-white/10">
                <span class="font-black text-white">مجموع کار</span>
                <span class="font-black text-base text-white">{{ selectedBar.planned_total || 0 }}</span>
              </div>
              <div class="flex items-center justify-between gap-3">
                <span class="font-black text-emerald-300">مجموع انجام</span>
                <span class="font-black text-base text-emerald-300">{{ selectedBar.completed || 0 }}</span>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- راهنما -->
      <div class="flex items-center justify-center gap-4 mt-3 pt-2 border-t border-white/5 text-[10px] opacity-70">
        <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-sm bg-blue-500"></span> برنامه روز</span>
        <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-sm bg-emerald-500"></span> انجام‌شده</span>
      </div>
    </div>

    <!-- 📊 خلاصه تفکیک بدون تکرار / دوره‌ای -->
    <div class="glass-card p-4 sm:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex flex-col gap-3">
      <h3 class="text-xs sm:text-sm font-black">خلاصه نوع کارها</h3>
      <div class="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20">
        <div class="flex items-center justify-between gap-2">
          <span class="text-xs font-black text-cyan-300">📌 بدون تکرار</span>
          <span class="text-xs font-black text-white">{{ taskTypeSummary.fixedDone }} از {{ taskTypeSummary.fixedTotal }}</span>
        </div>
        <div class="mt-2 h-2 rounded-full bg-white/10 overflow-hidden"><div class="h-full rounded-full bg-gradient-to-l from-cyan-600 to-cyan-300 transition-all" :style="{ width: taskTypeSummary.fixedPct + '%' }"></div></div>
        <p class="mt-1.5 text-[10px] font-bold text-cyan-200/80" :style="{ color: themeStore.currentTheme === 'light-2026' ? '#0e7490' : '' }">{{ taskTypeSummary.fixedPct }}٪ انجام شده</p>
      </div>
      <div class="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20">
        <div class="flex items-center justify-between gap-2">
          <span class="text-xs font-black text-amber-300">🔄 دوره‌ای</span>
          <span class="text-xs font-black text-white">{{ taskTypeSummary.recDone }} از {{ taskTypeSummary.recTotal }}</span>
        </div>
        <div class="mt-2 h-2 rounded-full bg-white/10 overflow-hidden"><div class="h-full rounded-full bg-gradient-to-l from-amber-600 to-amber-300 transition-all" :style="{ width: taskTypeSummary.recPct + '%' }"></div></div>
        <p class="mt-1.5 text-[10px] font-bold text-amber-200/80" :style="{ color: themeStore.currentTheme === 'light-2026' ? '#b45309' : '' }">{{ taskTypeSummary.recPct }}٪ انجام شده</p>
      </div>
      <p class="text-[10px] leading-5 text-gray-400 font-bold border-t border-white/5 pt-2">💡 در کارهای دوره‌ای، کارهای تکمیل‌شده و کارهای در انتظار موعد (که هنوز عقب نیفتاده‌اند) انجام‌شده حساب می‌شوند؛ فقط کارهای عقب‌افتاده انجام‌نشده‌اند.</p>
    </div>
    </div>

    <!-- 🔍 کادر فیلترهای پیشرفته با تمامی امکانات -->
    <div v-if="showFilters" class="mb-5 p-4 rounded-2xl space-y-3 glass-card border border-white/10 animate-in fade-in duration-200">
      <div class="relative">
        <Search class="absolute right-3 top-3 w-4 h-4 text-gray-400" />
        <input v-model="filterSearch" placeholder="جستجو در عنوان و توضیحات کارها..." class="w-full pr-10 pl-4 py-2.5 rounded-xl text-xs md:text-sm font-bold bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-purple-500" />
      </div>

      <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
        <select v-model="filterCategory" class="px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option value="">همه دسته‌بندی‌ها</option><option v-for="c in categories" :key="c.value || c" :value="c.value || c">{{ c.label || c }}</option></select>
        <select v-model="filterStatus" class="px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option value="">همه وضعیت‌ها</option><option v-for="(l,k) in statusLabels" :key="k" :value="k">{{ l }}</option></select>
        <select v-model="filterPriority" class="px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option :value="null">همه اولویت‌ها</option><option :value="0">عادی</option><option :value="1">مهم</option><option :value="2">اضطراری</option></select>
        <select v-model="filterGoalId" @change="filterSubGoalId = null; if (filterGoalId) fetchSubGoals(filterGoalId); else subGoals = []"
                class="px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none"><option :value="null">همه اهداف</option><option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option></select>
        <select v-model="filterSubGoalId" :disabled="!filterGoalId || subGoals.length === 0"
                class="px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none disabled:opacity-40 disabled:cursor-not-allowed">
          <option :value="null">{{ filterGoalId ? (subGoals.length ? 'همه گام‌ها' : 'گامی ندارد') : 'ابتدا هدف انتخاب کنید' }}</option>
          <option v-for="sg in subGoals" :key="sg.id" :value="sg.id">{{ sg.title }}</option>
        </select>
      </div>

      <!-- فیلترهای بازه تاریخ و تکرار -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-2 pt-2 border-t border-white/5">
        <select v-model="filterRecurrence" class="px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 border border-white/10 text-white outline-none">
          <option value="">همه کارها (بدون تکرار و دوره‌ای)</option>
          <option value="has">فقط کارهای دوره‌ای</option>
          <option value="none">فقط کارهای بدون تکرار</option>
        </select>

        <div class="space-y-1">
          <DateInputPersian v-model="filterDueDateFrom" placeholder="مهلت از تاریخ..." />
        </div>

        <div class="space-y-1">
          <DateInputPersian v-model="filterDueDateTo" placeholder="مهلت تا تاریخ..." />
        </div>
      </div>

      <div class="flex justify-end pt-1">
        <button @click="resetFilters" class="px-4 py-1.5 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-gray-300 transition">پاکسازی کلیه فیلترها</button>
      </div>
    </div>

    <!-- حالت بدون کار -->
    <div v-if="filteredTasks.length === 0" class="text-center py-16 glass-card rounded-3xl border border-white/10">
      <div class="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-3 text-purple-400">
        <Search class="w-7 h-7" />
      </div>
      <p class="text-lg font-black text-white mb-1">{{ tasks.length === 0 ? 'هنوز کاری ثبت نکرده‌اید!' : 'کاری با این فیلترها پیدا نشد' }}</p>
      <p class="text-xs text-gray-400 mb-4">می‌توانید کار جدیدی برای امروز ایجاد کنید.</p>
      <button @click="openNewForm" class="px-5 py-2.5 bg-purple-600 text-white font-black rounded-xl text-xs hover:bg-purple-500 transition shadow-lg">ساخت کار جدید</button>
    </div>

    <!-- 🌟 شبکه ۲ ستونه هوشمند در موبایل (Grid 2 Columns on Mobile) + ۳ ستونه در دسکتاپ -->
    <div v-else-if="showAllTasks" class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-2.5 sm:gap-4 md:gap-5">
      <div 
        v-for="task in filteredTasks" 
        :key="task.id" 
        @click="selectTaskForFocus(task)"
        class="p-3 sm:p-5 rounded-2xl md:rounded-3xl border-2 transition-all duration-200 hover:shadow-2xl hover:-translate-y-0.5 cursor-pointer flex flex-col justify-between relative group"
        :class="[
          // پس‌زمینه کارت بر اساس وضعیت (سلسله‌مراتبی)
          (task.is_completed || task.status === 'completed') ? 'border-emerald-500/40 bg-emerald-500/12 shadow-[0_0_18px_rgba(16,185,129,0.18)]' :  // یشمی: انجام‌شده
          getTaskStatus(task) === 'extended' ? 'border-sky-500/50 bg-sky-500/12 shadow-[0_0_15px_rgba(56,189,248,0.18)]' :                            // آسمانی: تمدید شده
          isTaskOverdue(task) ? 'border-red-500/70 bg-red-500/12 shadow-[0_0_18px_rgba(239,68,68,0.2)]' :                                            // قرمز: عقب‌افتاده
          isToday(task) ? 'border-amber-500/50 bg-amber-500/12 shadow-[0_0_15px_rgba(245,158,11,0.15)]' :                                             // آفتابی: امروز
          isTaskRecurring(task) ? 'border-purple-500/40 bg-purple-500/10 shadow-[0_0_15px_rgba(168,85,247,0.1)]' :                                   // بنفش: دوره‌ای
          'border-slate-500/30 bg-slate-500/8',                                                                                                    // خاکستری: بدون موعد
        ]"
      >
        <div>
          <!-- 🌟 المان اختصاصی نوع کار (بدون تکرار / دوره‌ای) - پررنگ و بزرگ -->
          <div v-if="isTaskRecurring(task)" class="mb-2.5 -mt-1">
            <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] sm:text-[11px] font-black shadow-md"
                 :style="{
                   background: themeStore.currentTheme === 'light-2026' ? 'linear-gradient(135deg, #ede9fe, #ddd6fe)' : 'linear-gradient(135deg, rgba(168,85,247,0.25), rgba(99,102,241,0.2))',
                   color: themeStore.currentTheme === 'light-2026' ? '#5b21b6' : '#e9d5ff',
                   border: themeStore.currentTheme === 'light-2026' ? '1px solid #7c3aed' : '1px solid rgba(168,85,247,0.5)',
                   boxShadow: '0 0 12px rgba(168,85,247,0.2)'
                 }">
              <RotateCw class="w-3 h-3 sm:w-3.5 sm:h-3.5 animate-spin" style="animation-duration: 6s;" />
              <span>کار دوره‌ای</span>
              <span class="opacity-60 text-[9px] sm:text-[10px]">•</span>
              <span class="opacity-90">{{ recurrenceLabel(task.recurrence_type) }}</span>
            </div>
          </div>
          <div v-else class="mb-2 -mt-1">
            <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] sm:text-[11px] font-black shadow-sm"
                 :style="{
                   background: themeStore.currentTheme === 'light-2026' ? 'linear-gradient(135deg, #cffafe, #a5f3fc)' : 'linear-gradient(135deg, rgba(34,211,238,0.2), rgba(14,165,233,0.15))',
                   color: themeStore.currentTheme === 'light-2026' ? '#0e7490' : '#67e8f9',
                   border: themeStore.currentTheme === 'light-2026' ? '1px solid #0891b2' : '1px solid rgba(34,211,238,0.5)'
                 }">
              <Circle class="w-2.5 h-2.5 sm:w-3 sm:h-3 fill-current" />
              <span>کار بدون تکرار</span>
            </div>
          </div>

          <!-- ۵ لیبل بصری رنگی شفاف بالای کارت (با رنگ‌بندی بهبودیافته برای خوانایی در همه تم‌ها) -->
          <div class="flex items-center justify-between gap-1 mb-2">
            <div class="flex items-center gap-1 flex-wrap">
              <!-- ۱. قرمز: عقب‌افتاده - متن سفید خوانا روی پس‌زمینه قرمز -->
              <span v-if="getTaskStatus(task) === 'overdue'" class="rounded-lg bg-red-500/40 text-white border border-red-300/60 flex items-center gap-0.5 font-black shadow-sm" :class="fontSizeClasses.badge">
                <AlertTriangle class="w-2.5 h-2.5 sm:w-3 sm:h-3 animate-bounce" /> <span>عقب‌افتاده</span>
              </span>

              <!-- ۲. سبز: انجام‌شده - متن سفید خوانا روی پس‌زمینه یشمی -->
              <span v-else-if="task.is_completed || task.status === 'completed'" class="rounded-lg bg-emerald-500/40 text-white border border-emerald-300/60 flex items-center gap-0.5 font-black shadow-sm" :class="fontSizeClasses.badge">
                <CheckCircle2 class="w-2.5 h-2.5 sm:w-3 sm:h-3" /> <span>انجام شد</span>
              </span>

              <!-- ۳. زرد: کارهای امروز - متن تیره روی پس‌زمینه زرد روشن -->
              <span v-else-if="isToday(task)" class="rounded-lg bg-amber-300/50 text-amber-950 border border-amber-400/70 flex items-center gap-0.5 font-black shadow-sm" :class="fontSizeClasses.badge">
                <Zap class="w-2.5 h-2.5 sm:w-3 sm:h-3 text-amber-700" /> <span>امروز</span>
              </span>

              <!-- ۴. آسمانی: تمدید شده - متن سفید روی پس‌زمینه sky -->
              <span v-else-if="getTaskStatus(task) === 'extended'" class="rounded-lg bg-sky-500/40 text-white border border-sky-300/60 flex items-center gap-0.5 font-black shadow-sm" :class="fontSizeClasses.badge">
                <Clock class="w-2.5 h-2.5 sm:w-3 sm:h-3" /> <span>تمدید شده</span>
              </span>

              <!-- ۵. آبی: در انتظار موعد - متن سفید روی پس‌زمینه آبی -->
              <span v-else class="rounded-lg bg-blue-500/40 text-white border border-blue-300/60 flex items-center gap-0.5 font-black shadow-sm" :class="fontSizeClasses.badge">
                <Clock class="w-2.5 h-2.5 sm:w-3 sm:h-3" /> <span>موعد</span>
              </span>
            </div>

            <div class="flex items-center gap-0.5" @click.stop>
              <button @click="openEditForm(task)" title="ویرایش" class="p-1.5 rounded-lg transition" style="background: rgba(255,255,255,0.08); color: #e5e7eb; border: 1px solid rgba(255,255,255,0.1);" onmouseover="this.style.background='rgba(255,255,255,0.18)';this.style.color='#ffffff'" onmouseout="this.style.background='rgba(255,255,255,0.08)';this.style.color='#e5e7eb'"><Edit3 class="w-3.5 h-3.5" /></button>
              <button @click="deleteTask(task.id)" title="حذف" class="p-1.5 rounded-lg transition" style="background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3);" onmouseover="this.style.background='rgba(239,68,68,0.3)';this.style.color='#ffffff'" onmouseout="this.style.background='rgba(239,68,68,0.15)';this.style.color='#fca5a5'"><Trash2 class="w-3.5 h-3.5" /></button>
            </div>
          </div>

          <!-- عنوان کارت (بدون چک‌باکس) -->
          <div class="mb-2.5">
            <h3 class="leading-snug transition line-clamp-2"
                :style="{ fontFamily: 'BNazanin, Vazirmatn, serif', fontWeight: 'bold', fontSize: '1.15em', letterSpacing: '-0.01em', color: themeStore.currentTheme === 'light-2026' ? ((task.is_completed || task.status === 'completed') ? '#94a3b8' : isTaskOverdue(task) ? '#b91c1c' : '#0f172a') : ((task.is_completed || task.status === 'completed') ? 'rgba(255,255,255,0.45)' : isTaskOverdue(task) ? '#ffffff' : (fontColorMode === 'dark' ? '#0f172a' : '#ffffff')) }">
              {{ task.title }}
            </h3>
            <!-- خط تزئینی زیر عنوان -->
            <div class="mt-1.5 h-px bg-gradient-to-r from-purple-500/40 via-purple-400/20 to-transparent"></div>
          </div>

          <!-- توضیحات -->
          <p v-if="task.description" class="line-clamp-1 mb-2 text-[10px] sm:text-xs" :style="{ color: themeStore.currentTheme === 'light-2026' ? '#475569' : (fontColorMode === 'dark' ? '#475569' : 'rgba(255,255,255,0.75)') }">{{ task.description }}</p>
        </div>

        <div class="-mx-3 sm:-mx-5 -mb-3 sm:-mb-5 mt-2 px-3 sm:px-5 py-2.5 rounded-b-2xl md:rounded-b-3xl space-y-1.5" style="background: #000000; border-top: 1px solid rgba(255,255,255,0.08);">
          <!-- ردیف اول: تاریخ اقدام بعدی + دکمه تمرکز -->
          <div class="flex items-center justify-between text-[10px] sm:text-xs font-bold gap-2">
            <div class="flex items-center gap-1.5 min-w-0 flex-1">
              <Calendar class="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" style="color: #a78bfa;" />
              <div class="flex flex-col min-w-0">
                <span class="text-[9px] opacity-60 leading-none mb-0.5" style="color: #d4d4d8;">تاریخ اقدام بعدی</span>
                <span class="truncate leading-none font-mono"
                      :class="isTaskOverdue(task) ? 'text-red-400 animate-pulse' : 'text-amber-300'">{{ getNextActionDate(task) }}</span>
              </div>
            </div>

            <button @click.stop="selectTaskForFocus(task)" class="px-2.5 py-1 rounded-lg text-[9px] sm:text-[10px] font-black flex items-center gap-1 transition shrink-0" style="background: rgba(255,255,255,0.08); color: #ffffff; border: 1px solid rgba(255,255,255,0.1);">
              <Eye class="w-3 h-3 sm:w-3.5 sm:h-3.5" style="color: #fbbf24;" />
              <span class="hidden sm:inline">تمرکز</span>
            </button>
          </div>

          <!-- ردیف دوم: تاریخ آخرین اقدام (اگر وجود داشته باشد) -->
          <div v-if="task.last_action_date" class="flex items-center gap-1.5 text-[9px] sm:text-[10px]">
            <CheckCircle2 class="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" style="color: #34d399;" />
            <div class="flex flex-col min-w-0 flex-1">
              <span class="text-[9px] opacity-60 leading-none mb-0.5" style="color: #d4d4d8;">تاریخ آخرین اقدام</span>
              <span class="truncate leading-none font-mono" style="color: #f3f4f6;">{{ formatDate(task.last_action_date) }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- نمای فشرده/لیستی -->
    <div v-else class="space-y-2.5">
      <div 
        v-for="task in filteredTasks" 
        :key="task.id" 
        @click="selectTaskForFocus(task)"
        class="flex items-center justify-between gap-3 px-4 py-3 rounded-2xl transition cursor-pointer border text-xs sm:text-sm"
        :class="[
          fontColorClasses.cardBg,
          isTaskOverdue(task) ? 'bg-red-500/20 border-red-500/50' :
          isTaskRecurring(task) ? 'bg-purple-500/10 border-purple-500/20' :
          fontColorClasses.border
        ]"
      >
        <div class="flex items-center gap-2.5 flex-1 min-w-0">
          <!-- آیکون اختصاصی نوع کار در نمای فشرده -->
          <span v-if="isTaskRecurring(task)"
                :title="`کار دوره‌ای (${recurrenceLabel(task.recurrence_type)})`"
                class="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                :style="{
                  background: themeStore.currentTheme === 'light-2026' ? '#ede9fe' : 'linear-gradient(135deg, rgba(168,85,247,0.3), rgba(99,102,241,0.25))',
                  border: themeStore.currentTheme === 'light-2026' ? '1px solid #7c3aed' : '1px solid rgba(168,85,247,0.5)',
                  boxShadow: '0 0 8px rgba(168,85,247,0.2)'
                }">
            <RotateCw class="w-3 h-3 animate-spin" :style="{ animationDuration: '8s', color: themeStore.currentTheme === 'light-2026' ? '#5b21b6' : '#c4b5fd' }" />
          </span>
          <span v-else title="کار بدون تکرار"
                class="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                :style="{
                  background: themeStore.currentTheme === 'light-2026' ? '#cffafe' : 'rgba(34,211,238,0.15)',
                  border: themeStore.currentTheme === 'light-2026' ? '1px solid #0891b2' : '1px solid rgba(34,211,238,0.5)'
                }">
            <Circle class="w-2.5 h-2.5 fill-current" :style="{ color: themeStore.currentTheme === 'light-2026' ? '#0e7490' : '#67e8f9' }" />
          </span>
          <span class="truncate font-black"
                :style="{ fontFamily: 'BNazanin, Vazirmatn, serif', fontSize: '1.1em', color: themeStore.currentTheme === 'light-2026' ? ((task.is_completed || task.status === 'completed') ? '#94a3b8' : isTaskOverdue(task) ? '#b91c1c' : '#0f172a') : ((task.is_completed || task.status === 'completed') ? 'rgba(255,255,255,0.45)' : isTaskOverdue(task) ? '#ffffff' : (fontColorMode === 'dark' ? '#0f172a' : '#ffffff')) }">{{ task.title }}</span>
        </div>

        <div class="flex items-center gap-2 shrink-0" @click.stop>
          <span class="text-[10px] sm:text-xs font-bold" :style="{ color: themeStore.currentTheme === 'light-2026' ? (isTaskOverdue(task) ? '#b91c1c' : '#475569') : (isTaskOverdue(task) ? '#fca5a5' : (fontColorMode === 'dark' ? '#475569' : 'rgba(255,255,255,0.75)')) }">{{ getNextActionDate(task) }}</span>
          <button @click="openEditForm(task)" class="p-1.5 rounded-lg transition" style="background: rgba(255,255,255,0.08); color: #e5e7eb; border: 1px solid rgba(255,255,255,0.1);" onmouseover="this.style.background='rgba(255,255,255,0.18)';this.style.color='#ffffff'" onmouseout="this.style.background='rgba(255,255,255,0.08)';this.style.color='#e5e7eb'"><Edit3 class="w-3.5 h-3.5" /></button>
          <button @click="deleteTask(task.id)" class="p-1.5 rounded-lg transition" style="background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3);" onmouseover="this.style.background='rgba(239,68,68,0.3)';this.style.color='#ffffff'" onmouseout="this.style.background='rgba(239,68,68,0.15)';this.style.color='#fca5a5'"><Trash2 class="w-3.5 h-3.5" /></button>
        </div>
      </div>
    </div>

    <!-- 🚀 Teleport برای مودال راهنما (کامل و ۱۰۰٪ بدون حذف) -->
    <Teleport to="body">
      <div v-if="showHelpModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-300" @click.self="showHelpModal = false">
        <div class="w-full max-w-4xl max-h-[85vh] overflow-y-auto rounded-3xl p-6 md:p-8 border-2 border-amber-500/40 shadow-[0_0_60px_rgba(245,158,11,0.2)] bg-slate-900 text-white relative">
          <div class="flex items-center justify-between pb-4 mb-6 border-b border-white/10">
            <div class="flex items-center gap-3">
              <div class="p-3 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <BookOpen class="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h3 class="text-xl md:text-2xl font-black text-white">راهنمای جامع تعریف کارها و منطق برنامه</h3>
                <p class="text-xs text-gray-400 mt-1">آموزش گام‌به‌گام تعریف کارهای بدون تکرار و دوره‌ای با مثال‌های عملی</p>
              </div>
            </div>
            <button @click="showHelpModal = false" class="p-2 text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
          </div>

          <div class="space-y-6 text-right">
            <div class="p-5 rounded-2xl bg-white/5 border border-white/10 space-y-3">
              <h4 class="text-base font-black text-amber-400 flex items-center gap-2">
                <Info class="w-5 h-5" /> منطق محاسباتی تاریخ‌ها و تکرار کارها
              </h4>
              <ul class="text-xs md:text-sm text-gray-300 space-y-2 leading-relaxed list-disc list-inside">
                <li><strong class="text-white">کارهای بدون تکرار (یک‌باره):</strong> یک تاریخ ثبت و مدت زمان دارند. پس از تیک خوردن، وضعیت به «تکمیل‌شده» تغییر کرده و تاریخ انجام در «آخرین اقدام» ثبت می‌شود.</li>
                <li><strong class="text-white">کارهای دوره‌ای (تکرارشونده):</strong> بازه تکرار دارند. با تیک زدن هر دوره، تاریخ امروز در «آخرین اقدام» ثبت شده و تاریخ مهلت بعدی خودکار برای دوره آینده تنظیم می‌شود.</li>
                <li><strong class="text-white">کارهای عقب‌افتاده:</strong> هر کاری که تاریخ مهلت آن قبل از امروز باشد و تیک نخورده باشد، قرمز و در تب «عقب‌افتاده‌ها» قرار می‌گیرد.</li>
                <li><strong class="text-white">کارهای تمدید شده:</strong> اگر کار عقب‌افتاده باشد و برای آن «تاریخ پیشنهادی» (تمدید) در حالت تمرکز یا ویرایش تنظیم شود، به رنگ آسمانی نمایش داده می‌شود. وقتی به تاریخ پیشنهادی برسیم، کارت به رنگ «امروز» تغییر می‌کند.</li>
              </ul>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-white/10 flex justify-end">
            <button @click="showHelpModal = false" class="px-6 py-2.5 bg-amber-500 text-slate-950 font-black rounded-xl text-xs shadow-lg">متوجه شدم</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 🚀 Teleport برای کارت تمرکز سه‌بعدی (کامل و ۱۰۰٪ بدون حذف) -->
    <Teleport to="body">
      <div v-if="selectedTask" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-300" @click.self="closeTaskFocus">
        <div class="w-full max-w-3xl rounded-3xl p-6 md:p-8 max-h-[85vh] overflow-y-auto border-2 border-purple-500/50 shadow-[0_0_60px_rgba(168,85,247,0.3)] bg-slate-900 text-white relative animate-in zoom-in-95 duration-300">
          <div class="flex items-center justify-between mb-5 pb-4 border-b border-white/10">
            <button @click="closeTaskFocus" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-black rounded-xl shadow-xl transition flex items-center gap-1.5 text-xs">
              <ArrowRight class="w-4 h-4" />
              <span>بازگشت به لیست کارها</span>
            </button>
            <div class="flex items-center gap-2">
              <button @click="openEditForm(selectedTask)" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition flex items-center gap-1"><Edit3 class="w-3.5 h-3.5 text-purple-400" /> ویرایش</button>
              <button @click="deleteTask(selectedTask.id)" class="px-3 py-1.5 bg-red-500/20 text-red-400 font-bold rounded-xl text-xs transition flex items-center gap-1"><Trash2 class="w-3.5 h-3.5" /> حذف</button>
            </div>
          </div>

          <div class="flex items-center gap-2 mb-3 flex-wrap">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-300 font-black text-xs"><Sparkles class="w-3.5 h-3.5 text-amber-400 animate-spin" /> شناسنامه کامل کار</span>
            <span v-if="isTaskOverdue(selectedTask)" class="px-3 py-1 rounded-full bg-red-500/30 text-red-300 font-black text-xs border border-red-500/50">🚨 عقب‌افتاده</span>
            <span v-if="isTaskRecurring(selectedTask)" class="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 font-black text-xs border border-amber-500/30">🔄 تکرارشونده</span>
          </div>

          <div class="flex items-start gap-3 mb-5 pb-5 border-b border-white/10">
            <button @click="toggleTask(selectedTask)" class="w-8 h-8 rounded-xl border-2 flex items-center justify-center transition-all mt-1 shrink-0" :class="(selectedTask.is_completed || selectedTask.status === 'completed') ? 'bg-purple-600 border-purple-600 text-white' : 'border-white/30 text-transparent'"><Check class="w-5 h-5" /></button>
            <div>
              <h2 class="text-xl md:text-2xl font-black text-white mb-1.5" :class="(selectedTask.is_completed || selectedTask.status === 'completed') ? 'line-through opacity-40' : ''">{{ selectedTask.title }}</h2>
              <p v-if="selectedTask.description" class="text-xs md:text-sm text-gray-200 leading-relaxed whitespace-pre-line">{{ selectedTask.description }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2 bg-blue-500/20 text-blue-400 rounded-xl"><Flag class="w-4 h-4" /></div><div><p class="text-[10px] text-gray-400 font-bold">درجه اولویت</p><p class="text-xs font-black text-white">{{ priorityLabels[selectedTask.priority] || 'عادی' }}</p></div></div>
            <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2 bg-purple-500/20 text-purple-400 rounded-xl"><Tag class="w-4 h-4" /></div><div><p class="text-[10px] text-gray-400 font-bold">دسته‌بندی</p><p class="text-xs font-black text-white">{{ selectedTask.category || 'عمومی' }}</p></div></div>
            <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2 bg-amber-500/20 text-amber-400 rounded-xl"><Clock class="w-4 h-4" /></div><div><p class="text-[10px] text-gray-400 font-bold">تاریخ اقدام / مهلت بعدی</p><p class="text-xs font-black text-amber-300">{{ getNextActionDate(selectedTask) }}</p></div></div>
            <div v-if="selectedTask.last_action_date" class="p-3.5 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-3"><div class="p-2 bg-emerald-500/20 text-emerald-400 rounded-xl"><CheckCircle2 class="w-4 h-4" /></div><div><p class="text-[10px] text-gray-400 font-bold">تاریخ آخرین اقدام</p><p class="text-xs font-bold text-white">{{ formatDate(selectedTask.last_action_date) }}</p></div></div>

            <!-- 🆕 تاریخ پیشنهادی (تمدید) - قابل تنظیم فقط وقتی کار عقب‌افتاده باشد -->
            <div v-if="!selectedTask.is_completed && getTaskStatus(selectedTask) === 'overdue'" class="sm:col-span-2 p-4 rounded-2xl border-2 border-sky-500/40 flex flex-col gap-2" style="background: rgba(14,165,233,0.1);">
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <div class="p-2 bg-sky-500/30 text-sky-300 rounded-xl flex-shrink-0">
                    <Clock class="w-4 h-4" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="text-[10px] text-sky-200/80 font-bold">تاریخ پیشنهادی برای تمدید</p>
                    <p v-if="!focusEditingSuggested && selectedTask.suggested_due_date" class="text-xs font-black text-sky-200 truncate">{{ formatDate(selectedTask.suggested_due_date) }}</p>
                    <p v-else-if="!focusEditingSuggested" class="text-xs font-bold text-sky-200/60 italic">تنظیم نشده - برای تمدید کلیک کنید</p>
                  </div>
                </div>
                <button v-if="!focusEditingSuggested" @click="focusEditingSuggested = true; focusSuggestedDate = selectedTask.suggested_due_date || ''" class="px-3 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-1 flex-shrink-0" style="background: #0ea5e9; color: #fff;">
                  <Edit3 class="w-3 h-3" /> تنظیم
                </button>
              </div>
              <div v-if="focusEditingSuggested" class="flex items-center gap-2 flex-wrap">
                <div class="flex-1 min-w-[150px]">
                  <DateInputPersian v-model="focusSuggestedDate" />
                </div>
                <button @click="saveSuggestedFromFocus" :disabled="isLoading" class="px-3 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-1" style="background: #10b981; color: #fff;">
                  <Check class="w-3 h-3" /> ذخیره
                </button>
                <button @click="focusEditingSuggested = false; focusSuggestedDate = selectedTask.suggested_due_date || null" class="px-3 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-1" style="background: rgba(255,255,255,0.1); color: #fff;">
                  <X class="w-3 h-3" /> لغو
                </button>
              </div>
              <p class="text-[10px] text-sky-200/70 font-bold leading-relaxed">اگر کار انجام نشد، تاریخ پیشنهادی تعیین کنید تا کارت به رنگ «تمدید شده» درآید و تا آن تاریخ فرصت داشته باشید.</p>
            </div>
            <div v-else-if="!selectedTask.is_completed && selectedTask.suggested_due_date && getTaskStatus(selectedTask) === 'extended'" class="sm:col-span-2 p-4 rounded-2xl border-2 border-sky-500/40 flex items-center gap-3" style="background: rgba(14,165,233,0.1);">
              <div class="p-2 bg-sky-500/30 text-sky-300 rounded-xl flex-shrink-0">
                <Clock class="w-4 h-4" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] text-sky-200/80 font-bold">تمدید شده تا</p>
                <p class="text-xs font-black text-sky-200">{{ formatDate(selectedTask.suggested_due_date) }}</p>
              </div>
              <span class="text-[9px] px-2 py-0.5 rounded-full font-black" style="background: #0ea5e9; color: #fff;">تمدید</span>
            </div>
          </div>

          <div class="flex justify-end pt-3 border-t border-white/10">
            <button @click="closeTaskFocus" class="px-5 py-2 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-xs transition">بستن حالت تمرکز</button>
          </div>
        </div>
      </div>
    </Teleport>

    <TaskFormModal
      v-model="showTaskModal"
      :form="form"
      :validation-errors="validationErrors"
      :categories="categories"
      :goals="goals"
      :sub-goals="subGoals"
      :editing-task="editingTask"
      :is-loading="isLoading"
      @update:form="(value) => form = value"
      @goal-change="onGoalChange"
      @save="saveTask"
    />
  </div>
</template>