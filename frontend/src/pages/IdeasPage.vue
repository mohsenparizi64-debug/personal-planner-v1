<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { toShamsiDisplay } from '@/utils/date'
import { 
  Lightbulb, Plus, Search, Star, ExternalLink, Rocket, Zap, 
  Tag, Edit, Trash2, Shuffle, CheckCircle, Flame, Filter, Target, ListTodo, X, Trophy, Sparkles, Layers
} from 'lucide-vue-next'

const router = useRouter()
const ideas = ref([])
const goals = ref([])
const roadmapSubGoals = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('all')
const activeTab = ref('all') // all, raw, in_review, ready, archived

const showModal = ref(false)
const isEditing = ref(false)
const currentIdeaId = ref(null)

// مدل فرم ایده با انتخاب هدف و گام عملیاتی
const form = ref({
  title: '',
  description: '',
  category: 'کسب‌وکار',
  status: 'raw',
  excitement_rating: 3,
  reference_links: '',
  tags: '',
  goal_id: null,
  sub_goal_id: null
})

const categories = ['کسب‌وکار', 'تکنولوژی', 'شخصی', 'مالی', 'تولید محتوا', 'سبک زندگی', 'عمومی']

const statusTabs = [
  { id: 'all', label: 'همه ایده‌ها', icon: Lightbulb },
  { id: 'raw', label: '💡 خام', icon: Flame },
  { id: 'in_review', label: '🔍 در حال بررسی', icon: Filter },
  { id: 'ready', label: '💎 آماده اجرا', icon: Rocket },
  { id: 'archived', label: '📁 بایگانی', icon: CheckCircle }
]

const fetchIdeas = async () => {
  try {
    isLoading.value = true
    const response = await api.get('/ideas')
    ideas.value = response.data
  } catch (error) {
    console.error('خطا در دریافت ایده‌ها:', error)
  } finally {
    isLoading.value = false
  }
}

const fetchGoals = async () => {
  try {
    const response = await api.get('/goals')
    goals.value = response.data
  } catch (error) {
    console.error('خطا در دریافت اهداف:', error)
  }
}

// بارگذاری گام‌های عملیاتی هدف انتخاب‌شده
const fetchSubGoalsForGoal = async (goalId) => {
  if (!goalId) {
    roadmapSubGoals.value = []
    return
  }
  try {
    const res = await api.get(`/roadmap?goal_id=${goalId}`)
    roadmapSubGoals.value = res.data
  } catch (e) {
    roadmapSubGoals.value = []
  }
}

const onGoalChange = () => {
  form.value.sub_goal_id = null
  if (form.value.goal_id) {
    fetchSubGoalsForGoal(form.value.goal_id)
  }
}

onMounted(() => {
  fetchIdeas()
  fetchGoals()
})

const stats = computed(() => {
  return {
    total: ideas.value.length,
    raw: ideas.value.filter(i => i.status === 'raw').length,
    inReview: ideas.value.filter(i => i.status === 'in_review').length,
    ready: ideas.value.filter(i => i.status === 'ready').length,
    completed: ideas.value.filter(i => i.live_status_info?.is_completed).length
  }
})

const filteredIdeas = computed(() => {
  return ideas.value.filter(idea => {
    const matchesSearch = idea.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          (idea.description && idea.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
    const matchesCategory = selectedCategory.value === 'all' || idea.category === selectedCategory.value
    const matchesTab = activeTab.value === 'all' || idea.status === activeTab.value

    return matchesSearch && matchesCategory && matchesTab
  })
})

const randomIdea = ref(null)
const pickRandomIdea = () => {
  const readyIdeas = ideas.value.filter(i => i.status !== 'archived')
  if (readyIdeas.length > 0) {
    const index = Math.floor(Math.random() * readyIdeas.length)
    randomIdea.value = readyIdeas[index]
  }
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = {
    title: '',
    description: '',
    category: 'کسب‌وکار',
    status: 'raw',
    excitement_rating: 3,
    reference_links: '',
    tags: '',
    goal_id: null,
    sub_goal_id: null
  }
  showModal.value = true
}

const openEditModal = (idea) => {
  isEditing.value = true
  currentIdeaId.value = idea.id
  form.value = { ...idea }
  if (idea.goal_id) fetchSubGoalsForGoal(idea.goal_id)
  showModal.value = true
}

const saveIdea = async () => {
  try {
    if (!form.value.title.trim()) return

    if (isEditing.value) {
      await api.put(`/ideas/${currentIdeaId.value}`, form.value)
    } else {
      await api.post('/ideas', form.value)
    }
    showModal.value = false
    fetchIdeas()
  } catch (error) {
    alert('خطا در ذخیره‌سازی ایده')
  }
}

const deleteIdea = async (id) => {
  if (confirm('آیا از حذف این ایده مطمئن هستید؟')) {
    try {
      await api.delete(`/ideas/${id}`)
      fetchIdeas()
    } catch (error) {
      alert('خطا در حذف ایده')
    }
  }
}

const convertToGoal = async (idea) => {
  try {
    await api.post(`/ideas/${idea.id}/convert-to-goal`)
    alert('✨ ایده با موفقیت به هدف کلان تبدیل شد!')
    fetchIdeas()
    router.push('/goals')
  } catch (error) {
    alert('خطا در تبدیل ایده به هدف')
  }
}

const convertToTask = async (idea) => {
  try {
    await api.post(`/ideas/${idea.id}/convert-to-task`)
    alert('⚡ ایده با موفقیت به تسک اجرایی منتقل شد!')
    fetchIdeas()
    router.push('/tasks')
  } catch (error) {
    alert('خطا در تبدیل ایده به تسک')
  }
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'raw': return { label: '💡 خام', bg: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' }
    case 'in_review': return { label: '🔍 در حال بررسی', bg: 'bg-blue-500/10 text-blue-400 border-blue-500/30' }
    case 'ready': return { label: '💎 آماده اجرا', bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' }
    case 'archived': return { label: '📁 بایگانی', bg: 'bg-gray-500/10 text-gray-400 border-gray-500/30' }
    default: return { label: status, bg: 'bg-white/10 text-white' }
  }
}
</script>

<template>
  <div class="space-y-8 max-w-7xl mx-auto pb-12">
    
    <!-- هدر صفحه -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 rounded-3xl border border-white/10 shadow-2xl">
      <div>
        <h1 class="text-3xl font-black text-white flex items-center gap-3">
          <div class="p-3 bg-gradient-to-br from-amber-500 to-yellow-500 rounded-2xl shadow-lg shadow-amber-500/30 text-white">
            <Lightbulb class="w-8 h-8 animate-pulse" />
          </div>
          بانک ایده‌ها و جرقه‌های ذهنی
        </h1>
        <p class="text-sm text-gray-400 mt-2">ثبت سریع ایده‌ها، پرورش، و تبدیل هوشمندانه به اهداف و تسک‌های اجرایی</p>
      </div>

      <div class="flex items-center gap-3">
        <button @click="pickRandomIdea" class="px-4 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-2xl border border-white/10 backdrop-blur-md transition flex items-center gap-2 shadow-lg">
          <Shuffle class="w-5 h-5 text-amber-400" />
          <span>🎲 پیشنهاد تصادفی ایده</span>
        </button>

        <button @click="openCreateModal" class="px-6 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-slate-950 font-black rounded-2xl shadow-xl shadow-amber-500/20 transition flex items-center gap-2">
          <Plus class="w-5 h-5" />
          <span>ثبت ایده جدید</span>
        </button>
      </div>
    </div>

    <!-- آمار سریع -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-amber-500/20 text-amber-400 rounded-xl"><Lightbulb class="w-6 h-6" /></div>
        <div><p class="text-2xl font-black text-white">{{ stats.total }}</p><p class="text-xs text-gray-400 font-bold">کل ایده‌ها</p></div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-yellow-500/20 text-yellow-400 rounded-xl"><Flame class="w-6 h-6" /></div>
        <div><p class="text-2xl font-black text-white">{{ stats.raw }}</p><p class="text-xs text-gray-400 font-bold">جرقه‌های خام</p></div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-blue-500/20 text-blue-400 rounded-xl"><Filter class="w-6 h-6" /></div>
        <div><p class="text-2xl font-black text-white">{{ stats.inReview }}</p><p class="text-xs text-gray-400 font-bold">در حال بررسی</p></div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl"><Rocket class="w-6 h-6" /></div>
        <div><p class="text-2xl font-black text-white">{{ stats.ready }}</p><p class="text-xs text-gray-400 font-bold">آماده اجرا</p></div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-yellow-500/40 bg-yellow-500/10 flex items-center gap-4 col-span-2 md:col-span-1">
        <div class="p-3 bg-yellow-400 text-slate-950 rounded-xl shadow-lg shadow-yellow-400/30"><Trophy class="w-6 h-6" /></div>
        <div><p class="text-2xl font-black text-yellow-300">{{ stats.completed }}</p><p class="text-xs text-yellow-200 font-bold">ایده‌های محقق‌شده 🏆</p></div>
      </div>
    </div>

    <!-- لیست کارت‌های ایده (با افکت گلدن لاتاری) -->
    <div v-if="isLoading" class="text-center py-12 text-gray-400">در حال بارگیری ایده‌ها...</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="idea in filteredIdeas" 
        :key="idea.id"
        class="glass-card p-6 rounded-3xl transition-all duration-500 flex flex-col justify-between group relative overflow-hidden"
        :class="[
          idea.live_status_info?.is_completed 
            ? 'bg-gradient-to-br from-amber-950/40 via-yellow-900/30 to-amber-900/40 border-2 border-yellow-400/80 shadow-[0_0_30px_rgba(251,191,36,0.4)] animate-pulse' 
            : (idea.live_status_info?.is_converted ? 'bg-emerald-950/30 border-2 border-emerald-500/50 shadow-lg shadow-emerald-500/10' : 'border border-white/10 hover:border-amber-500/40')
        ]"
      >
        <!-- افکت نورانی گلدن کارت شانس و لاتاری -->
        <div v-if="idea.live_status_info?.is_completed" class="absolute -top-12 -right-12 w-32 h-32 bg-yellow-400/20 rounded-full blur-2xl pointer-events-none"></div>

        <div>
          <!-- هدر کارت -->
          <div class="flex items-center justify-between mb-3">
            <span class="px-2.5 py-1 rounded-lg border text-[10px] font-bold" :class="getStatusBadge(idea.status).bg">
              {{ getStatusBadge(idea.status).label }}
            </span>

            <div class="flex items-center gap-0.5 text-amber-400">
              <Star v-for="i in 5" :key="i" class="w-3.5 h-3.5" :class="i <= idea.excitement_rating ? 'fill-amber-400' : 'opacity-20'" />
            </div>
          </div>

          <!-- عنوان و متن ایده -->
          <h3 class="text-lg font-bold text-white mb-2 flex items-center gap-2">
            <span>{{ idea.title }}</span>
            <Trophy v-if="idea.live_status_info?.is_completed" class="w-5 h-5 text-yellow-400 animate-bounce" />
          </h3>
          <p class="text-xs text-gray-300 leading-relaxed mb-4 whitespace-pre-line line-clamp-4">{{ idea.description || 'بدون توضیحات' }}</p>
        </div>

        <div>
          <!-- کارت سبز یا گلدن لاتاری نشان‌دهنده آخرین وضعیت زنده -->
          <div v-if="idea.live_status_info?.is_converted" class="p-3 rounded-2xl mb-4 border transition-all"
               :class="idea.live_status_info?.is_completed ? 'bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border-yellow-400/60 text-yellow-200' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'">
            
            <div v-if="idea.live_status_info?.is_completed" class="flex items-center gap-2 font-black text-xs text-yellow-300">
              <Trophy class="w-4 h-4 fill-yellow-400" />
              <span>🏆 ایده جامه عمل پوشید و محقق شد!</span>
            </div>

            <div v-else class="flex items-center gap-2 font-bold text-xs">
              <Rocket class="w-4 h-4 text-emerald-400 animate-pulse" />
              <span>🚀 در حال اجرا | وضعیت زنده: {{ idea.live_status_info?.status_text }}</span>
            </div>

            <p class="text-[10px] text-gray-400 mt-1" v-if="idea.conversion_date">
              تاریخ تبدیل ایده: {{ toShamsiDisplay(idea.conversion_date) }}
            </p>
          </div>

          <!-- لینک مرجع و دسته‌بندی -->
          <div class="flex items-center justify-between text-[11px] text-gray-400 border-t border-white/5 pt-3 mb-4">
            <span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 font-bold">{{ idea.category }}</span>
            <a v-if="idea.reference_links" :href="idea.reference_links" target="_blank" class="text-blue-400 hover:underline flex items-center gap-1">
              <ExternalLink class="w-3 h-3" /> منبع الگو
            </a>
          </div>

          <!-- اکشن‌های کارت -->
          <div class="flex items-center justify-between pt-2">
            <div class="flex items-center gap-2">
              <button @click="convertToGoal(idea)" title="تبدیل به هدف کلان" class="p-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 rounded-xl transition"><Target class="w-4 h-4" /></button>
              <button @click="convertToTask(idea)" title="تبدیل به تسک اجرایی" class="p-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-xl transition"><ListTodo class="w-4 h-4" /></button>
            </div>

            <div class="flex items-center gap-1">
              <button @click="openEditModal(idea)" class="p-2 text-gray-400 hover:text-white transition"><Edit class="w-4 h-4" /></button>
              <button @click="deleteIdea(idea.id)" class="p-2 text-gray-400 hover:text-red-400 transition"><Trash2 class="w-4 h-4" /></button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- مودال ساخت/ویرایش ایده با انتخاب هدف و گام عملیاتی -->
    <div v-if="showModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div class="w-full max-w-lg rounded-3xl p-6 glass-card border border-white/20 shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            <Lightbulb class="w-6 h-6 text-amber-400" />
            {{ isEditing ? 'ویرایش ایده' : 'ثبت جرقه‌ی ذهنی جدید' }}
          </h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
        </div>

        <form @submit.prevent="saveIdea" class="space-y-4 text-right">
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">عنوان ایده *</label>
            <input v-model="form.title" type="text" required placeholder="مثلاً: راه‌اندازی کانال آموزش پایتون" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none" />
          </div>

          <!-- انتخاب ۳ لایه‌ای: هدف کلان مرتبط + گام عملیاتی مرتبط -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-gray-300 mb-1">اتصال به هدف کلان</label>
              <select v-model="form.goal_id" @change="onGoalChange" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none">
                <option :value="null">ایده مستقل / هدف جدید</option>
                <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-300 mb-1">اتصال به گام عملیاتی (SubGoal)</label>
              <select v-model="form.sub_goal_id" :disabled="!form.goal_id" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none disabled:opacity-40">
                <option :value="null">بدون گام مشخص</option>
                <option v-for="sg in roadmapSubGoals" :key="sg.id" :value="sg.id">{{ sg.title }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-gray-300 mb-1">دسته‌بندی</label>
              <select v-model="form.category" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-300 mb-1">وضعیت پختگی</label>
              <select v-model="form.status" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs outline-none">
                <option value="raw">💡 خام (جرقه اولیه)</option>
                <option value="in_review">🔍 در حال بررسی</option>
                <option value="ready">💎 آماده اجرا</option>
                <option value="archived">📁 بایگانی</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">درجه هیجان و ارزش (۱ تا ۵ ستاره)</label>
            <div class="flex items-center gap-2 bg-white/5 p-3 rounded-xl border border-white/10">
              <Star v-for="star in 5" :key="star" @click="form.excitement_rating = star" class="w-6 h-6 cursor-pointer transition" :class="star <= form.excitement_rating ? 'text-amber-400 fill-amber-400 scale-110' : 'text-gray-600'" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">شرح و جزئیات ایده</label>
            <textarea v-model="form.description" rows="3" placeholder="جزئیات ایده را اینجا بنویسید..." class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none"></textarea>
          </div>

          <div class="flex items-center gap-3 pt-4">
            <button type="submit" class="flex-1 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-slate-950 font-black rounded-xl shadow-lg transition">
              {{ isEditing ? 'بروزرسانی ایده' : 'ثبت ایده' }}
            </button>
            <button type="button" @click="showModal = false" class="px-5 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl transition">انصراف</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>