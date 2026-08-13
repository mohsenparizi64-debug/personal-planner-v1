<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { 
  Lightbulb, Plus, Search, Star, ExternalLink, Rocket, Zap, 
  Tag, Edit, Trash2, Shuffle, CheckCircle, Flame, Filter, Target, ListTodo, X
} from 'lucide-vue-next'

const router = useRouter()
const ideas = ref([])
const goals = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('all')
const activeTab = ref('all') // all, raw, in_review, ready, archived

const showModal = ref(false)
const isEditing = ref(false)
const currentIdeaId = ref(null)

// مدل فرم ایده
const form = ref({
  title: '',
  description: '',
  category: 'کسب‌وکار',
  status: 'raw',
  excitement_rating: 3,
  reference_links: '',
  tags: '',
  goal_id: null
})

const categories = ['کسب‌وکار', 'تکنولوژی', 'شخصی', 'مالی', 'تولید محتوا', 'سبک زندگی', 'عمومی']

const statusTabs = [
  { id: 'all', label: 'همه ایده‌ها', icon: Lightbulb },
  { id: 'raw', label: '💡 خام', icon: Flame },
  { id: 'in_review', label: '🔍 در حال بررسی', icon: Filter },
  { id: 'ready', label: '💎 آماده اجرا', icon: Rocket },
  { id: 'archived', label: '📁 بایگانی', icon: CheckCircle }
]

// بارگیری ایده‌ها و اهداف از API
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

onMounted(() => {
  fetchIdeas()
  fetchGoals()
})

// محاسبه آمار ایده‌ها
const stats = computed(() => {
  return {
    total: ideas.value.length,
    raw: ideas.value.filter(i => i.status === 'raw').length,
    inReview: ideas.value.filter(i => i.status === 'in_review').length,
    ready: ideas.value.filter(i => i.status === 'ready').length
  }
})

// فیلتر هوشمند ایده‌ها
const filteredIdeas = computed(() => {
  return ideas.value.filter(idea => {
    const matchesSearch = idea.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          (idea.description && idea.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
    const matchesCategory = selectedCategory.value === 'all' || idea.category === selectedCategory.value
    const matchesTab = activeTab.value === 'all' || idea.status === activeTab.value

    return matchesSearch && matchesCategory && matchesTab
  })
})

// پیشنهاددهنده تصادفی ایده
const randomIdea = ref(null)
const pickRandomIdea = () => {
  const readyIdeas = ideas.value.filter(i => i.status !== 'archived')
  if (readyIdeas.length > 0) {
    const index = Math.floor(Math.random() * readyIdeas.length)
    randomIdea.value = readyIdeas[index]
  }
}

// مدیریت ذخیره‌سازی فرم (ایجاد / ویرایش)
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
    goal_id: null
  }
  showModal.value = true
}

const openEditModal = (idea) => {
  isEditing.value = true
  currentIdeaId.value = idea.id
  form.value = { ...idea }
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

// 🚀 اکشن جادویی ۱: تبدیل ایده به هدف کلان
const convertToGoal = async (idea) => {
  try {
    const response = await api.post(`/ideas/${idea.id}/convert-to-goal`)
    alert('✨ ایده با موفقیت به هدف کلان تبدیل شد!')
    fetchIdeas()
    router.push('/goals')
  } catch (error) {
    alert('خطا در تبدیل ایده به هدف')
  }
}

// ⚡ اکشن جادویی ۲: تبدیل ایده به تسک اجرایی
const convertToTask = async (idea) => {
  try {
    const response = await api.post(`/ideas/${idea.id}/convert-to-task`)
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
        <button 
          @click="pickRandomIdea" 
          class="px-4 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-2xl border border-white/10 backdrop-blur-md transition flex items-center gap-2 shadow-lg"
        >
          <Shuffle class="w-5 h-5 text-amber-400" />
          <span>🎲 چی ایده بدم؟</span>
        </button>

        <button 
          @click="openCreateModal" 
          class="px-6 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-slate-950 font-black rounded-2xl shadow-xl shadow-amber-500/20 transition flex items-center gap-2"
        >
          <Plus class="w-5 h-5" />
          <span>ثبت ایده جدید</span>
        </button>
      </div>
    </div>

    <!-- باکس پیشنهاد ایده تصادفی -->
    <div v-if="randomIdea" class="glass-card p-6 rounded-3xl border border-amber-500/40 bg-amber-500/5 relative overflow-hidden animate-in fade-in zoom-in duration-300">
      <button @click="randomIdea = null" class="absolute top-4 left-4 text-gray-400 hover:text-white">
        <X class="w-5 h-5" />
      </button>
      <div class="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">
        <Flame class="w-4 h-4" /> ایده تصادفی پیشنهادی
      </div>
      <h3 class="text-xl font-bold text-white mb-2">{{ randomIdea.title }}</h3>
      <p class="text-sm text-gray-300 mb-4 line-clamp-2">{{ randomIdea.description || 'بدون توضیحات' }}</p>
      <div class="flex items-center gap-3">
        <button @click="convertToGoal(randomIdea)" class="px-3 py-1.5 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-xl text-xs font-bold hover:bg-purple-500/30 transition flex items-center gap-1">
          <Target class="w-4 h-4" /> تبدیل به هدف
        </button>
        <button @click="convertToTask(randomIdea)" class="px-3 py-1.5 bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-xl text-xs font-bold hover:bg-blue-500/30 transition flex items-center gap-1">
          <ListTodo class="w-4 h-4" /> تبدیل به تسک
        </button>
      </div>
    </div>

    <!-- کارت‌های آمار سریع -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-amber-500/20 text-amber-400 rounded-xl"><Lightbulb class="w-6 h-6" /></div>
        <div>
          <p class="text-2xl font-black text-white">{{ stats.total }}</p>
          <p class="text-xs text-gray-400 font-bold">کل ایده‌ها</p>
        </div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-yellow-500/20 text-yellow-400 rounded-xl"><Flame class="w-6 h-6" /></div>
        <div>
          <p class="text-2xl font-black text-white">{{ stats.raw }}</p>
          <p class="text-xs text-gray-400 font-bold">جرقه‌های خام</p>
        </div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-blue-500/20 text-blue-400 rounded-xl"><Filter class="w-6 h-6" /></div>
        <div>
          <p class="text-2xl font-black text-white">{{ stats.inReview }}</p>
          <p class="text-xs text-gray-400 font-bold">در حال بررسی</p>
        </div>
      </div>
      <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center gap-4">
        <div class="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl"><Rocket class="w-6 h-6" /></div>
        <div>
          <p class="text-2xl font-black text-white">{{ stats.ready }}</p>
          <p class="text-xs text-gray-400 font-bold">آماده اجرای عملیاتی</p>
        </div>
      </div>
    </div>

    <!-- فیلترها و تب‌های وضعیت -->
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 glass-card p-4 rounded-2xl border border-white/10">
      
      <!-- تب‌ها -->
      <div class="flex items-center gap-1 overflow-x-auto w-full md:w-auto pb-2 md:pb-0">
        <button 
          v-for="tab in statusTabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 whitespace-nowrap"
          :class="activeTab === tab.id ? 'bg-amber-500 text-slate-950 font-black shadow-lg shadow-amber-500/20' : 'text-gray-400 hover:bg-white/5'"
        >
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- جستجو و دسته‌بندی -->
      <div class="flex items-center gap-3 w-full md:w-auto">
        <div class="relative flex-1 md:w-64">
          <Search class="w-4 h-4 text-gray-400 absolute right-3 top-3" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="جستجوی ایده..." 
            class="w-full pr-9 pl-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>

        <select 
          v-model="selectedCategory" 
          class="px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <option value="all" class="bg-slate-900 text-white">همه دسته‌ها</option>
          <option v-for="cat in categories" :key="cat" :value="cat" class="bg-slate-900 text-white">{{ cat }}</option>
        </select>
      </div>

    </div>

    <!-- لیست کارت‌های ایده (Notion/Google Keep Style) -->
    <div v-if="isLoading" class="text-center py-12 text-gray-400">
      در حال بارگیری ایده‌ها...
    </div>

    <div v-else-if="filteredIdeas.length === 0" class="text-center py-16 glass-card rounded-3xl border border-white/10">
      <Lightbulb class="w-16 h-16 text-gray-600 mx-auto mb-4" />
      <h3 class="text-lg font-bold text-gray-300">هیچ ایده‌ای یافت نشد</h3>
      <p class="text-xs text-gray-500 mt-1">اولین جرقه‌ی ذهنی خود را ثبت کنید!</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="idea in filteredIdeas" 
        :key="idea.id"
        class="glass-card p-6 rounded-3xl border border-white/10 hover:border-amber-500/40 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden"
      >
        <div>
          <!-- هدر کارت -->
          <div class="flex items-center justify-between mb-3">
            <span class="px-2.5 py-1 rounded-lg border text-[10px] font-bold" :class="getStatusBadge(idea.status).bg">
              {{ getStatusBadge(idea.status).label }}
            </span>

            <!-- ستاره‌های هیجان -->
            <div class="flex items-center gap-0.5 text-amber-400">
              <Star v-for="i in 5" :key="i" class="w-3.5 h-3.5" :class="i <= idea.excitement_rating ? 'fill-amber-400' : 'opacity-20'" />
            </div>
          </div>

          <!-- عنوان و متن -->
          <h3 class="text-lg font-bold text-white mb-2 group-hover:text-amber-400 transition">{{ idea.title }}</h3>
          <p class="text-xs text-gray-300 leading-relaxed mb-4 whitespace-pre-line line-clamp-4">{{ idea.description || 'بدون توضیحات' }}</p>
        </div>

        <div>
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
              <button 
                @click="convertToGoal(idea)" 
                title="تبدیل به هدف کلان" 
                class="p-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 rounded-xl transition"
              >
                <Target class="w-4 h-4" />
              </button>
              <button 
                @click="convertToTask(idea)" 
                title="تبدیل به تسک اجرایی" 
                class="p-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-xl transition"
              >
                <ListTodo class="w-4 h-4" />
              </button>
            </div>

            <div class="flex items-center gap-1">
              <button @click="openEditModal(idea)" class="p-2 text-gray-400 hover:text-white transition"><Edit class="w-4 h-4" /></button>
              <button @click="deleteIdea(idea.id)" class="p-2 text-gray-400 hover:text-red-400 transition"><Trash2 class="w-4 h-4" /></button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- مودال ایجاد و ویرایش ایده -->
    <div v-if="showModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div class="w-full max-w-lg rounded-3xl p-6 glass-card border border-white/20 shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            <Lightbulb class="w-6 h-6 text-amber-400" />
            {{ isEditing ? 'ویرایش ایده' : 'ثبت جرقه‌ی ذهنی جدید' }}
          </h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
        </div>

        <form @submit.prevent="saveIdea" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">عنوان ایده *</label>
            <input v-model="form.title" type="text" required placeholder="مثلاً: راه‌اندازی کانال آموزش پایتون" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-gray-300 mb-1">دسته‌بندی</label>
              <select v-model="form.category" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs focus:ring-2 focus:ring-amber-500 outline-none">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-300 mb-1">وضعیت پختگی</label>
              <select v-model="form.status" class="w-full px-3 py-2.5 bg-slate-900 border border-white/10 rounded-xl text-white text-xs focus:ring-2 focus:ring-amber-500 outline-none">
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
              <Star 
                v-for="star in 5" 
                :key="star" 
                @click="form.excitement_rating = star"
                class="w-6 h-6 cursor-pointer transition"
                :class="star <= form.excitement_rating ? 'text-amber-400 fill-amber-400 scale-110' : 'text-gray-600'"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">شرح و جزئیات ایده</label>
            <textarea v-model="form.description" rows="3" placeholder="جزئیات، نکات و سوالات ایده را اینجا بنویسید..." class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none"></textarea>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">لینک مرجع / الگو (اختیاری)</label>
            <input v-model="form.reference_links" type="url" placeholder="https://example.com" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-xs focus:ring-2 focus:ring-amber-500 outline-none" />
          </div>

          <div class="flex items-center gap-3 pt-4">
            <button type="submit" class="flex-1 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-slate-950 font-black rounded-xl shadow-lg transition">
              {{ isEditing ? 'بروزرسانی ایده' : 'ثبت ایده' }}
            </button>
            <button type="button" @click="showModal = false" class="px-5 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl transition">
              انصراف
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>