<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { toGregorianISO, toShamsiDisplay } from '@/utils/date'
import * as jalaali from 'jalaali-js'
import {
  Award, Plus, BookOpen, CheckCircle2, Clock, Sparkles, Tag, ExternalLink,
  Target, Search, Filter, Edit2, Trash2, X, TrendingUp, Zap, Calendar,
  Flame, Trophy, BarChart3, Activity, Target as TargetIcon, Lightbulb
} from 'lucide-vue-next'

const skills = ref([])
const learningLogs = ref([])
const goals = ref([])
const stats = ref(null)
const loading = ref(false)

const showSkillModal = ref(false)
const showLogModal = ref(false)
const editingSkill = ref(null)  // null = ایجاد، object = ویرایش

// فیلترها
const searchQuery = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterGoal = ref('')  // '', 'independent' یا goal_id

const skillForm = ref({
  title: '',
  category: 'برنامه‌نویسی',
  status: 'in_progress',
  progress_percent: 10,
  goal_id: 'independent',  // 'independent' به جای null
  notes: '',
  level: 'beginner',
  start_date: new Date().toISOString().split('T')[0],
  source_url: '',
  target_hours: null
})

const logForm = ref({
  skill_id: null,
  title: '',
  content: '',
  log_date: new Date().toISOString().split('T')[0],
  resource_url: '',
  tags: '',
  duration_minutes: null
})

// دسته‌بندی‌های پیشنهادی
const suggestedCategories = [
  'برنامه‌نویسی', 'زبان', 'طراحی', 'هنر', 'موسیقی', 'ورزش',
  'مدیریت', 'بازاریابی', 'مالی', 'مهندسی', 'علوم', 'عمومی'
]

// محاسبه categories منحصر از مهارت‌ها
const availableCategories = computed(() => {
  const cats = new Set(suggestedCategories)
  skills.value.forEach(s => s.category && cats.add(s.category))
  return Array.from(cats)
})

// مهارت‌های فیلتر شده
const filteredSkills = computed(() => {
  let result = skills.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(s => s.title?.toLowerCase().includes(q))
  }
  if (filterCategory.value) {
    result = result.filter(s => (s.category || 'عمومی') === filterCategory.value)
  }
  if (filterStatus.value) {
    result = result.filter(s => s.status === filterStatus.value)
  }
  if (filterGoal.value === 'independent') {
    result = result.filter(s => !s.goal_id)
  } else if (filterGoal.value && filterGoal.value !== 'all') {
    result = result.filter(s => s.goal_id === parseInt(filterGoal.value))
  }
  return result
})

// گروه‌بندی log ها بر اساس ماه
const groupedLogs = computed(() => {
  const groups = {}
  learningLogs.value.forEach(log => {
    const monthKey = log.log_date.substring(0, 7)  // YYYY-MM
    if (!groups[monthKey]) groups[monthKey] = []
    groups[monthKey].push(log)
  })
  return Object.entries(groups).sort((a, b) => b[0].localeCompare(a[0]))
})

const fetchData = async () => {
  loading.value = true
  try {
    const [skRes, lgRes, goRes, stRes] = await Promise.all([
      api.get('/skills/'),
      api.get('/skills/_logs'),
      api.get('/goals/'),
      api.get('/skills/_stats/summary')
    ])
    console.log('[SkillsPage] API responses:', {
      skillsStatus: skRes.status,
      skillsCount: Array.isArray(skRes.data) ? skRes.data.length : 'NOT ARRAY',
      goalsStatus: goRes.status,
      goalsCount: Array.isArray(goRes.data) ? goRes.data.length : 'NOT ARRAY',
      goalsData: goRes.data,
    })
    skills.value = skRes.data || []
    learningLogs.value = lgRes.data || []
    goals.value = goRes.data || []
    stats.value = stRes.data
    console.log('[SkillsPage] After assign, goals.value:', goals.value.length, goals.value)
  } catch (e) {
    console.error('[SkillsPage] FETCH ERROR:', e.response?.status, e.response?.data || e.message)
  } finally {
    loading.value = false
  }
}

const openCreateSkill = () => {
  editingSkill.value = null
  skillForm.value = {
    title: '',
    category: 'برنامه‌نویسی',
    status: 'in_progress',
    progress_percent: 10,
    goal_id: 'independent',
    notes: '',
    level: 'beginner',
    start_date: new Date().toISOString().split('T')[0],
    source_url: '',
    target_hours: null
  }
  showSkillModal.value = true
}

const openEditSkill = (skill) => {
  editingSkill.value = skill
  skillForm.value = {
    title: skill.title,
    category: skill.category || 'عمومی',
    status: skill.status,
    progress_percent: skill.progress_percent,
    goal_id: skill.goal_id || 'independent',
    notes: skill.notes || '',
    level: skill.level || 'beginner',
    start_date: skill.start_date || new Date().toISOString().split('T')[0],
    source_url: skill.source_url || '',
    target_hours: skill.target_hours
  }
  showSkillModal.value = true
}

const saveSkill = async () => {
  try {
    const payload = { ...skillForm.value }
    if (payload.goal_id === 'independent' || payload.goal_id === '') payload.goal_id = null
    // تبدیل تاریخ شمسی به میلادی برای backend
    if (payload.start_date) {
      const greg = toGregorianISO(payload.start_date)
      if (greg) payload.start_date = greg
      else delete payload.start_date  // اگه invalid، ارسال نکن
    }
    if (editingSkill.value) {
      await api.put(`/skills/by_id/${editingSkill.value.id}`, payload)
    } else {
      await api.post('/skills/', payload)
    }
    showSkillModal.value = false
    fetchData()
  } catch (e) {
    console.error(e)
    alert('خطا در ذخیره مهارت')
  }
}

const deleteSkill = async (skill) => {
  if (!confirm(`آیا از حذف «${skill.title}» مطمئنید؟`)) return
  try {
    await api.delete(`/skills/by_id/${skill.id}`)
    fetchData()
  } catch (e) {
    console.error(e)
  }
}

const openLogModal = (skillId = null) => {
  logForm.value = {
    skill_id: skillId,
    title: '',
    content: '',
    log_date: new Date().toISOString().split('T')[0],
    resource_url: '',
    tags: '',
    duration_minutes: null
  }
  showLogModal.value = true
}

const saveLog = async () => {
  try {
    const payload = { ...logForm.value }
    // تبدیل تاریخ شمسی به میلادی برای backend
    if (payload.log_date) {
      const greg = toGregorianISO(payload.log_date)
      if (greg) payload.log_date = greg
      else {
        alert('تاریخ یادداشت نامعتبر است')
        return
      }
    }
    await api.post('/skills/_logs', payload)
    showLogModal.value = false
    fetchData()
  } catch (e) {
    console.error(e)
    alert('خطا در ثبت یادگیری')
  }
}

const deleteLog = async (logId) => {
  if (!confirm('آیا از حذف این یادداشت مطمئنید؟')) return
  try {
    await api.delete(`/skills/_logs/${logId}`)
    fetchData()
  } catch (e) {
    console.error(e)
  }
}

const getLevelLabel = (lvl) => {
  return { beginner: 'مبتدی', intermediate: 'متوسط', advanced: 'پیشرفته' }[lvl] || lvl
}

const getLevelColor = (lvl) => {
  return {
    beginner: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    intermediate: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    advanced: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
  }[lvl] || ''
}

const getStatusLabel = (s) => {
  return { in_progress: 'در حال یادگیری', mastered: 'تسلط یافته', on_hold: 'متوقف' }[s] || s
}

const getStatusColor = (s) => {
  return {
    in_progress: 'bg-blue-500/20 text-blue-300',
    mastered: 'bg-emerald-500/20 text-emerald-300',
    on_hold: 'bg-slate-500/20 text-slate-300'
  }[s] || ''
}

const getMonthLabel = (gregKey) => {
  // gregKey = "YYYY-MM" (میلادی). تبدیل به شمسی
  const [gy, gm] = gregKey.split('-').map(Number)
  if (!gy || !gm) return gregKey
  // تبدیل میلادی به شمسی
  const g = new Date(gy, gm - 1, 15)  // وسط ماه
  const j = jalaali.toJalaali(g.getFullYear(), g.getMonth() + 1, g.getDate())
  const months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
  return `${months[j.jm - 1]} ${j.jy}`
}

const getShamsiDate = (gregDate) => {
  if (!gregDate) return ''
  try {
    return toShamsiDisplay(gregDate)
  } catch {
    return gregDate
  }
}

onMounted(() => {
  fetchData()
})

// Debug: log وقتی goals تغییر می‌کنه
watch(goals, (newVal) => {
  console.log('[SkillsPage] goals updated, count:', newVal?.length, 'data:', newVal)
}, { deep: true })
</script>

<template>
  <div class="space-y-4 sm:space-y-6 max-w-7xl mx-auto p-3 sm:p-4 md:p-6">

    <!-- هدر -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10">
      <div class="flex items-center gap-3 sm:gap-4">
        <div class="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg shadow-amber-500/20 shrink-0">
          <Award class="w-6 h-6 sm:w-8 sm:h-8 text-white" />
        </div>
        <div>
          <h2 class="text-lg sm:text-2xl font-black text-white">بانک مهارت‌ها و دفترچه آموزه‌ها</h2>
          <p class="text-[11px] sm:text-xs text-gray-400 mt-0.5 sm:mt-1">مدیریت درخت دانش، درصد تسلط و ثبت روزنوشت یادگیری‌ها</p>
        </div>
      </div>
      <div class="flex gap-2 sm:gap-3">
        <button @click="openCreateSkill"
          class="px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white text-xs sm:text-xs font-black rounded-lg sm:rounded-xl shadow-lg flex items-center gap-1.5 sm:gap-2 transition">
          <Plus class="w-4 h-4" /> <span class="hidden sm:inline">افزودن مهارت</span><span class="sm:hidden">مهارت</span>
        </button>
        <button @click="openLogModal()"
          class="px-3 sm:px-4 py-2 sm:py-2.5 bg-white/10 hover:bg-white/20 text-white text-xs font-bold rounded-lg sm:rounded-xl flex items-center gap-1.5 sm:gap-2 transition border border-white/10">
          <BookOpen class="w-4 h-4 text-amber-400" /> <span class="hidden sm:inline">ثبت نکته آموزه</span><span class="sm:hidden">آموزه</span>
        </button>
      </div>
    </div>

    <!-- KPI Stats - سطح ۱ -->
    <div v-if="stats" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
      <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-white/10">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] sm:text-xs text-gray-400 font-bold">کل مهارت‌ها</p>
            <p class="text-xl sm:text-2xl font-black text-white mt-0.5">{{ stats.total_skills }}</p>
          </div>
          <Award class="w-5 h-5 sm:w-6 sm:h-6 text-amber-400" />
        </div>
      </div>
      <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-emerald-500/30 bg-emerald-500/5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] sm:text-xs text-emerald-400 font-bold">تسلط یافته</p>
            <p class="text-xl sm:text-2xl font-black text-emerald-300 mt-0.5">{{ stats.mastered }}</p>
          </div>
          <Trophy class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-400" />
        </div>
      </div>
      <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-blue-500/30 bg-blue-500/5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] sm:text-xs text-blue-400 font-bold">در حال یادگیری</p>
            <p class="text-xl sm:text-2xl font-black text-blue-300 mt-0.5">{{ stats.in_progress }}</p>
          </div>
          <Activity class="w-5 h-5 sm:w-6 sm:h-6 text-blue-400" />
        </div>
      </div>
      <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-orange-500/30 bg-orange-500/5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] sm:text-xs text-orange-400 font-bold">🔥 Streak</p>
            <p class="text-xl sm:text-2xl font-black text-orange-300 mt-0.5">{{ stats.current_streak }} روز</p>
          </div>
          <Flame class="w-5 h-5 sm:w-6 sm:h-6 text-orange-400" />
        </div>
      </div>
      <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-white/10">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] sm:text-xs text-gray-400 font-bold">مستقل</p>
            <p class="text-xl sm:text-2xl font-black text-white mt-0.5">{{ stats.independent_skills }}</p>
          </div>
          <Lightbulb class="w-5 h-5 sm:w-6 sm:h-6 text-amber-400" />
        </div>
      </div>
      <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-white/10">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] sm:text-xs text-gray-400 font-bold">میانگین پیشرفت</p>
            <p class="text-xl sm:text-2xl font-black text-white mt-0.5">{{ stats.overall_progress_avg }}٪</p>
          </div>
          <BarChart3 class="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" />
        </div>
      </div>
    </div>

    <!-- فیلترها و جستجو - سطح ۱ -->
    <div class="glass-card p-3 sm:p-4 rounded-xl sm:rounded-2xl border border-white/10 space-y-2 sm:space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">
        <div class="relative">
          <Search class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="searchQuery" type="text" placeholder="جستجو در مهارت‌ها..."
            class="w-full pr-9 pl-3 py-2 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-amber-500" />
        </div>
        <select v-model="filterCategory"
          class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-amber-500">
          <option value="">همه دسته‌ها</option>
          <option v-for="c in availableCategories" :key="c" :value="c">{{ c }}</option>
        </select>
        <select v-model="filterStatus"
          class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-amber-500">
          <option value="">همه وضعیت‌ها</option>
          <option value="in_progress">در حال یادگیری</option>
          <option value="mastered">تسلط یافته</option>
          <option value="on_hold">متوقف</option>
        </select>
        <select v-model="filterGoal"
          class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-amber-500">
          <option value="">همه اهداف</option>
          <option value="independent">🎯 مستقل (بدون هدف)</option>
          <option v-for="g in goals" :key="g.id" :value="g.id">🎯 {{ g.title }}</option>
        </select>
      </div>
      <div class="flex items-center justify-between text-[10px] sm:text-xs text-gray-400">
        <span>{{ filteredSkills.length }} مهارت یافت شد</span>
        <button v-if="searchQuery || filterCategory || filterStatus || filterGoal"
          @click="searchQuery = ''; filterCategory = ''; filterStatus = ''; filterGoal = ''"
          class="text-amber-400 hover:text-amber-300">پاک کردن فیلترها</button>
      </div>
    </div>

    <!-- Skill Tree / لیست مهارت‌ها - سطح ۳ -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
      <div v-for="skill in filteredSkills" :key="skill.id"
        class="glass-card p-4 sm:p-5 rounded-2xl sm:rounded-3xl border border-white/10 space-y-3 hover:border-amber-500/50 transition-all duration-300 group">

        <!-- هدر کارت -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-1.5 mb-1.5">
              <span class="text-[9px] sm:text-[10px] px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 font-bold border border-amber-500/20">
                {{ skill.category || 'عمومی' }}
              </span>
              <span class="text-[9px] sm:text-[10px] px-2 py-0.5 rounded-md border font-bold" :class="getLevelColor(skill.level)">
                {{ getLevelLabel(skill.level) }}
              </span>
            </div>
            <h3 class="font-black text-white text-sm sm:text-base truncate">{{ skill.title }}</h3>
            <p v-if="skill.goal_title" class="text-[10px] sm:text-xs text-amber-400 mt-0.5 flex items-center gap-1 truncate">
              <Target class="w-3 h-3 shrink-0" /> {{ skill.goal_title }}
            </p>
            <p v-else class="text-[10px] sm:text-xs text-gray-500 mt-0.5 flex items-center gap-1">
              <Lightbulb class="w-3 h-3" /> مستقل
            </p>
          </div>
          <span class="text-[10px] sm:text-xs px-2 py-0.5 rounded-full font-bold shrink-0" :class="getStatusColor(skill.status)">
            {{ getStatusLabel(skill.status) }}
          </span>
        </div>

        <!-- نوار پیشرفت -->
        <div class="space-y-1">
          <div class="flex justify-between text-[10px] sm:text-xs text-gray-400 font-bold">
            <span>پیشرفت</span>
            <span>{{ skill.progress_percent }}٪</span>
          </div>
          <div class="w-full h-2 bg-white/10 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-500 shadow-md"
              :style="{ width: skill.progress_percent + '%' }"></div>
          </div>
        </div>

        <!-- ساعت‌های تمرین -->
        <div v-if="skill.target_hours" class="flex items-center justify-between text-[10px] sm:text-xs text-gray-400">
          <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {{ skill.practiced_hours || 0 }} / {{ skill.target_hours }} ساعت</span>
          <span class="font-bold text-amber-400">{{ Math.round(((skill.practiced_hours || 0) / skill.target_hours) * 100) }}٪</span>
        </div>

        <!-- یادداشت -->
        <p v-if="skill.notes" class="text-[10px] sm:text-xs text-gray-400 line-clamp-2 leading-relaxed">{{ skill.notes }}</p>

        <!-- تاریخ شروع -->
        <div v-if="skill.start_date" class="text-[10px] text-gray-500 flex items-center gap-1">
          <Calendar class="w-3 h-3" />
          شروع: {{ getShamsiDate(skill.start_date) }}
        </div>

        <!-- آمار سریع -->
        <div class="flex items-center justify-between pt-2 border-t border-white/5 text-[10px] sm:text-xs">
          <span class="text-gray-500 flex items-center gap-1">
            <BookOpen class="w-3 h-3" /> {{ skill.learning_logs?.length || 0 }} یادداشت
          </span>
          <div class="flex items-center gap-1">
            <button @click="openLogModal(skill.id)" class="w-7 h-7 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 flex items-center justify-center transition" title="افزودن یادداشت">
              <Plus class="w-3.5 h-3.5" />
            </button>
            <button @click="openEditSkill(skill)" class="w-7 h-7 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 flex items-center justify-center transition" title="ویرایش">
              <Edit2 class="w-3.5 h-3.5" />
            </button>
            <button @click="deleteSkill(skill)" class="w-7 h-7 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 flex items-center justify-center transition" title="حذف">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- پیام خالی -->
      <div v-if="!loading && filteredSkills.length === 0"
        class="col-span-full text-center py-10 sm:py-16 glass-card rounded-2xl sm:rounded-3xl border border-dashed border-white/10">
        <Award class="w-12 h-12 sm:w-16 sm:h-16 text-gray-600 mx-auto mb-3" />
        <p class="text-sm sm:text-base text-gray-400 font-bold mb-1">مهارتی یافت نشد</p>
        <p class="text-xs text-gray-500">اولین مهارت خودت رو اضافه کن</p>
        <button @click="openCreateSkill" class="mt-3 sm:mt-4 px-4 py-2 bg-amber-600 hover:bg-amber-500 rounded-lg sm:rounded-xl text-white text-xs font-bold transition">
          + افزودن مهارت
        </button>
      </div>
    </div>

    <!-- دفترچه آموزه‌ها با Timeline - سطح ۲ -->
    <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 space-y-3 sm:space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm sm:text-base md:text-lg font-black text-white flex items-center gap-2">
          <BookOpen class="w-4 h-4 sm:w-5 sm:h-5 text-amber-400" />
          دفترچه آموزه‌ها
        </h3>
        <span class="text-[10px] sm:text-xs text-gray-400 font-bold">{{ learningLogs.length }} یادداشت</span>
      </div>

      <div v-if="groupedLogs.length === 0" class="text-center py-8 text-gray-500 text-xs">
        هنوز یادداشتی ثبت نشده
      </div>

      <div v-for="[month, logs] in groupedLogs" :key="month" class="space-y-2">
        <div class="flex items-center gap-2 text-[10px] sm:text-xs text-amber-400 font-black">
          <Calendar class="w-3 h-3 sm:w-4 sm:h-4" />
          {{ getMonthLabel(month) }}
          <span class="text-gray-500 font-normal">({{ logs.length }})</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 sm:gap-3 mr-4 sm:mr-6 border-r-2 border-amber-500/20 pr-3 sm:pr-4">
          <div v-for="log in logs" :key="log.id" class="p-2.5 sm:p-3 rounded-lg sm:rounded-xl bg-white/5 border border-white/10 hover:border-amber-500/30 transition space-y-1.5 group">
            <div class="flex items-start justify-between gap-2">
              <h4 class="font-bold text-white text-xs sm:text-sm flex-1">{{ log.title }}</h4>
              <button @click="deleteLog(log.id)" class="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition">
                <X class="w-3 h-3 sm:w-3.5 sm:h-3.5" />
              </button>
            </div>
            <p v-if="log.content" class="text-[10px] sm:text-xs text-gray-300 leading-relaxed">{{ log.content }}</p>
            <div class="flex items-center justify-between text-[10px] sm:text-[11px] text-gray-400 pt-1 border-t border-white/5">
              <span>{{ getShamsiDate(log.log_date) }}</span>
              <div class="flex items-center gap-2">
                <span v-if="log.duration_minutes" class="flex items-center gap-1 text-amber-400">
                  <Clock class="w-2.5 h-2.5 sm:w-3 sm:h-3" /> {{ log.duration_minutes }}د
                </span>
                <span v-if="log.tags" class="flex items-center gap-1 text-amber-300 truncate max-w-[100px]">
                  <Tag class="w-2.5 h-2.5 sm:w-3 sm:h-3" /> {{ log.tags }}
                </span>
                <a v-if="log.resource_url" :href="log.resource_url" target="_blank" class="text-blue-400 hover:underline flex items-center gap-0.5">
                  <ExternalLink class="w-2.5 h-2.5 sm:w-3 sm:h-3" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal افزودن/ویرایش مهارت - سطح ۱ (با فیلدهای جدید) -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showSkillModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md" @click.self="showSkillModal = false">
          <div class="w-full max-w-lg glass-card p-4 sm:p-5 md:p-6 rounded-2xl sm:rounded-3xl border border-white/20 shadow-2xl space-y-3 sm:space-y-4 max-h-[90vh] overflow-y-auto custom-scrollbar">
            <div class="flex items-center justify-between pb-2 sm:pb-3 border-b border-white/10">
              <h3 class="text-base sm:text-lg font-bold text-white">
                {{ editingSkill ? 'ویرایش مهارت' : 'افزودن مهارت جدید' }}
              </h3>
              <button @click="showSkillModal = false" class="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center">
                <X class="w-4 h-4 text-white" />
              </button>
            </div>

            <form @submit.prevent="saveSkill" class="space-y-3 text-right">
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">عنوان مهارت *</label>
                <input v-model="skillForm.title" type="text" required
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none focus:ring-2 focus:ring-amber-500" />
              </div>

              <div class="grid grid-cols-2 gap-2 sm:gap-3">
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">دسته‌بندی</label>
                  <select v-model="skillForm.category"
                    class="w-full px-3 py-2 bg-slate-900 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none focus:ring-2 focus:ring-amber-500">
                    <option v-for="c in suggestedCategories" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">سطح فعلی</label>
                  <select v-model="skillForm.level" class="w-full px-3 py-2 bg-slate-900 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none">
                    <option value="beginner">مبتدی</option>
                    <option value="intermediate">متوسط</option>
                    <option value="advanced">پیشرفته</option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2 sm:gap-3">
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">وضعیت</label>
                  <select v-model="skillForm.status" class="w-full px-3 py-2 bg-slate-900 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none">
                    <option value="in_progress">در حال یادگیری</option>
                    <option value="mastered">تسلط یافته</option>
                    <option value="on_hold">متوقف</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ شروع</label>
                  <DateInputPersian v-model="skillForm.start_date" placeholder="تاریخ شروع یادگیری" />
                </div>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">
                  درصد تسلط: <span class="text-amber-400 font-black">{{ skillForm.progress_percent }}٪</span>
                </label>
                <input v-model.number="skillForm.progress_percent" type="range" min="0" max="100" step="5"
                  class="w-full accent-amber-500" />
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">
                  اتصال به هدف کلان *
                  <span class="text-[10px] text-amber-400 font-normal">(انتخاب «مستقل» برای مهارت بدون هدف)</span>
                </label>
                <select v-model="skillForm.goal_id" required
                  class="w-full px-3 py-2 bg-slate-900 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none focus:ring-2 focus:ring-amber-500">
                  <option value="independent">💡 مستقل (بدون هدف)</option>
                  <option v-if="goals.length === 0" disabled>⏳ در حال بارگذاری اهداف...</option>
                  <option v-for="g in goals" :key="g.id" :value="g.id">🎯 {{ g.title }}</option>
                </select>
                <p v-if="goals.length === 0" class="text-[10px] text-gray-500 mt-1">
                  ابتدا در سربرگ «اهداف» حداقل یک هدف تعریف کنید
                </p>
              </div>

              <div class="grid grid-cols-2 gap-2 sm:gap-3">
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">هدف ساعتی (اختیاری)</label>
                  <input v-model.number="skillForm.target_hours" type="number" min="0" placeholder="مثلاً 100"
                    class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">منبع اصلی (URL)</label>
                  <input v-model="skillForm.source_url" type="url" dir="ltr"
                    class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none" />
                </div>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">یادداشت</label>
                <textarea v-model="skillForm.notes" rows="2"
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none"></textarea>
              </div>

              <div class="flex gap-2 sm:gap-3 pt-2">
                <button type="submit" class="flex-1 py-2.5 sm:py-3 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-lg sm:rounded-xl shadow-lg transition">
                  {{ editingSkill ? 'ذخیره تغییرات' : 'ایجاد مهارت' }}
                </button>
                <button type="button" @click="showSkillModal = false" class="flex-1 py-2.5 sm:py-3 bg-white/10 hover:bg-white/20 text-gray-300 font-bold text-xs rounded-lg sm:rounded-xl transition">
                  انصراف
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Modal ثبت یادداشت -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showLogModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md" @click.self="showLogModal = false">
          <div class="w-full max-w-md glass-card p-4 sm:p-5 md:p-6 rounded-2xl sm:rounded-3xl border border-white/20 shadow-2xl space-y-3 sm:space-y-4 max-h-[90vh] overflow-y-auto custom-scrollbar">
            <div class="flex items-center justify-between pb-2 sm:pb-3 border-b border-white/10">
              <h3 class="text-base sm:text-lg font-bold text-white">ثبت نکته / آموزه جدید</h3>
              <button @click="showLogModal = false" class="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center">
                <X class="w-4 h-4 text-white" />
              </button>
            </div>

            <form @submit.prevent="saveLog" class="space-y-3 text-right">
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">مرتبط با مهارت</label>
                <select v-model="logForm.skill_id" class="w-full px-3 py-2 bg-slate-900 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none">
                  <option :value="null">بدون مهارت خاص</option>
                  <option v-for="s in skills" :key="s.id" :value="s.id">{{ s.title }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">عنوان موضوع یا نکته *</label>
                <input v-model="logForm.title" type="text" required
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none" />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">توضیحات و خلاصه آموخته</label>
                <textarea v-model="logForm.content" rows="3"
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none"></textarea>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">تاریخ</label>
                  <DateInputPersian v-model="logForm.log_date" placeholder="تاریخ یادگیری" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-400 mb-1">مدت (دقیقه)</label>
                  <input v-model.number="logForm.duration_minutes" type="number" min="0" placeholder="30"
                    class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">تگ‌ها (با کاما)</label>
                <input v-model="logForm.tags" type="text" placeholder="پایتون, async, ..."
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none" />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-1">لینک منبع (اختیاری)</label>
                <input v-model="logForm.resource_url" type="url" dir="ltr" placeholder="https://..."
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg sm:rounded-xl text-white text-xs outline-none" />
              </div>
              <div class="flex gap-2 sm:gap-3 pt-2">
                <button type="submit" class="flex-1 py-2.5 sm:py-3 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-lg sm:rounded-xl shadow-lg transition">
                  ثبت نکته
                </button>
                <button type="button" @click="showLogModal = false" class="flex-1 py-2.5 sm:py-3 bg-white/10 hover:bg-white/20 text-gray-300 font-bold text-xs rounded-lg sm:rounded-xl transition">
                  انصراف
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
.modal-enter-from > div, .modal-leave-to > div {
  transform: scale(0.9) translateY(20px);
}
</style>
