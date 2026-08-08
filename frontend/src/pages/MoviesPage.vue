<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, X, Film, Star, Calendar, Eye, EyeOff, ChevronDown, ChevronUp, Search } from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const movies = ref([])
const categories = ref([])
const showForm = ref(false)
const editingMovie = ref(null)
const message = ref('')
const messageType = ref('success')
const showAll = ref(true)
const expandedMovies = ref({})
const searchQuery = ref('')
const filterCategory = ref('')
const filterWatched = ref(null)

const form = ref({
  title: '', category: '', register_date: new Date().toISOString().split('T')[0],
  watch_date: '', rating: 0, notes: '', is_watched: false
})

const categoryLabels = {
  'action': 'اکشن', 'comedy': 'کمدی', 'drama': 'درام', 'horror': 'ترسناک',
  'sci-fi': 'علمی تخیلی', 'animation': 'انیمیشن', 'documentary': 'مستند',
  'romance': 'عاشقانه', 'other': 'سایر'
}

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchMovies = async () => {
  try { const res = await api.get('/movies'); movies.value = res.data } catch (e) {}
}

const fetchCategories = async () => {
  try { const res = await api.get('/movies/categories'); categories.value = res.data } catch (e) {}
}

const filteredMovies = computed(() => {
  let result = movies.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(m => m.title.toLowerCase().includes(q))
  }
  if (filterCategory.value) result = result.filter(m => m.category === filterCategory.value)
  if (filterWatched.value === 'watched') result = result.filter(m => m.is_watched)
  if (filterWatched.value === 'unwatched') result = result.filter(m => !m.is_watched)
  return result
})

const resetFilters = () => {
  searchQuery.value = ''; filterCategory.value = ''; filterWatched.value = null
}

const openNewForm = () => {
  form.value = { title: '', category: '', register_date: new Date().toISOString().split('T')[0], watch_date: '', rating: 0, notes: '', is_watched: false }
  editingMovie.value = null; showForm.value = true
}

const openEditForm = (movie) => {
  form.value = { ...movie }
  editingMovie.value = movie; showForm.value = true
}

const saveMovie = async () => {
  if (!form.value.title.trim()) return
  try {
    const data = { ...form.value }
    if (!data.is_watched) {
      data.watch_date = null
      data.rating = 0
    }
    if (editingMovie.value) {
      await api.put(`/movies/${editingMovie.value.id}`, data)
      showToast('✅ فیلم بروزرسانی شد')
    } else {
      await api.post('/movies', data)
      showToast('✅ فیلم اضافه شد')
    }
    showForm.value = false; editingMovie.value = null; await fetchMovies()
  } catch (e) { showToast('❌ خطا', 'error') }
}

const toggleWatched = async (movie) => {
  await api.put(`/movies/${movie.id}`, { is_watched: !movie.is_watched, watch_date: !movie.is_watched ? new Date().toISOString().split('T')[0] : movie.watch_date })
  await fetchMovies()
}

const deleteMovie = async (id) => {
  if (!confirm('مطمئنی؟')) return
  try { await api.delete(`/movies/${id}`); showToast('🗑️ حذف شد'); await fetchMovies() } catch (e) {}
}

const toggleExpand = (id) => { expandedMovies.value[id] = !expandedMovies.value[id] }

const starRating = (rating) => {
  return '⭐'.repeat(Math.round(rating / 2)) + (rating === 0 ? '' : ` (${rating}/10)`)
}

onMounted(() => { fetchMovies(); fetchCategories() })
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen">
    
    <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-extrabold mb-1" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">لیست فیلم‌ها</h1>
        <p :style="{ color: 'var(--text-secondary)' }">{{ filteredMovies.length }} فیلم</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button @click="showAll = !showAll" class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm"
                :style="showAll ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <Eye v-if="showAll" class="w-4 h-4" /> <EyeOff v-else class="w-4 h-4" />
          {{ showAll ? 'مخفی کردن' : 'نمایش همه' }}
        </button>
        <button @click="openNewForm" class="px-5 py-2 rounded-xl text-white font-semibold transition flex items-center gap-2" :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> فیلم جدید
        </button>
      </div>
    </div>

    <div class="mb-6 p-4 rounded-xl space-y-3" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      <div class="relative">
        <Search class="absolute right-3 top-2.5 w-5 h-5" :style="{ color: 'var(--text-secondary)' }" />
        <input v-model="searchQuery" placeholder="جستجوی فیلم..." class="w-full pr-10 pl-4 py-2.5 rounded-lg text-sm"
               :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
      </div>
      <div class="grid grid-cols-3 gap-2">
        <select v-model="filterCategory" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option value="">همه دسته‌بندی‌ها</option>
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <select v-model="filterWatched" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option :value="null">همه</option>
          <option value="watched">دیده شده</option>
          <option value="unwatched">دیده نشده</option>
        </select>
        <button @click="resetFilters" class="px-3 py-2 rounded-lg text-sm transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">حذف فیلترها</button>
      </div>
    </div>

    <div v-if="filteredMovies.length === 0" class="text-center py-20">
      <Film class="w-16 h-16 mx-auto mb-4" :style="{ color: 'var(--accent)' }" />
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">هنوز فیلمی ثبت نکردی!</p>
    </div>

    <div v-if="showAll" class="space-y-3">
      <div v-for="movie in filteredMovies" :key="movie.id"
           class="rounded-xl overflow-hidden transition-all duration-200 border"
           :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)', opacity: movie.is_watched ? 0.6 : 1 }">
        
        <div class="flex items-center gap-3 p-4 cursor-pointer" @click="toggleExpand(movie.id)">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
               :style="{ background: movie.is_watched ? 'rgba(34,197,94,0.15)' : 'var(--bg-hover)' }">
            {{ movie.is_watched ? '✅' : '🎬' }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-bold" :style="{ color: 'var(--text-primary)', textDecoration: movie.is_watched ? 'line-through' : 'none' }">{{ movie.title }}</h3>
            <div class="flex gap-2 text-xs mt-0.5" :style="{ color: 'var(--text-secondary)' }">
              <span v-if="movie.category">{{ categoryLabels[movie.category] || movie.category }}</span>
              <span v-if="movie.rating">{{ starRating(movie.rating) }}</span>
            </div>
          </div>
          <div class="flex gap-1 flex-shrink-0" @click.stop>
            <button @click="toggleWatched(movie)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: movie.is_watched ? '#22c55e' : 'var(--text-secondary)' }">
              <Eye v-if="!movie.is_watched" class="w-4 h-4" /><EyeOff v-else class="w-4 h-4" />
            </button>
            <button @click="openEditForm(movie)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-4 h-4" /></button>
            <button @click="deleteMovie(movie.id)" class="p-1.5 rounded-lg hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-4 h-4" /></button>
            <button class="p-1.5" :style="{ color: 'var(--text-secondary)' }">
              <ChevronDown v-if="!expandedMovies[movie.id]" class="w-4 h-4" /><ChevronUp v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div v-if="expandedMovies[movie.id]" class="px-4 pb-4 border-t" :style="{ borderColor: 'var(--border)' }">
          <div class="grid grid-cols-2 gap-3 mt-3 text-sm">
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت:</span> <span :style="{ color: 'var(--text-primary)' }">{{ formatDate(movie.register_date) || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ دیدن:</span> <span :style="{ color: 'var(--text-primary)' }">{{ formatDate(movie.watch_date) || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">دسته‌بندی:</span> <span :style="{ color: 'var(--text-primary)' }">{{ categoryLabels[movie.category] || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">امتیاز:</span> <span :style="{ color: 'var(--accent)' }">{{ movie.rating || '-' }}/10</span></div>
          </div>
          <div v-if="movie.notes" class="mt-3 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <p class="text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">یادداشت:</p>
            <p class="text-sm" :style="{ color: 'var(--text-primary)' }">{{ movie.notes }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== مودال ========== -->
    <div v-if="showForm" class="fixed inset-0 z-[100] flex items-start justify-center p-4 pt-20 pb-20 bg-black/60 backdrop-blur-sm overflow-y-auto" @click.self="showForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingMovie ? 'ویرایش فیلم' : 'فیلم جدید' }}</h3>
          <button @click="showForm = false" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۱- تاریخ ثبت</label>
            <DateInputPersian v-model="form.register_date" placeholder="تاریخ ثبت" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۲- نام فیلم *</label>
            <input v-model="form.title" placeholder="نام فیلم" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۳- دسته‌بندی</label>
            <select v-model="form.category" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="">انتخاب کنید...</option>
              <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
          </div>
          
          <!-- تاریخ دیدن - فقط اگر فیلم دیده شده -->
          <div v-if="form.is_watched">
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۴- تاریخ دیدن</label>
            <DateInputPersian v-model="form.watch_date" placeholder="تاریخ دیدن" />
          </div>
          
          <!-- امتیاز - فقط اگر فیلم دیده شده -->
          <div v-if="form.is_watched">
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۵- امتیاز (۱ تا ۱۰)</label>
            <div class="flex items-center gap-3">
              <input v-model.number="form.rating" type="range" min="0" max="10" step="1" class="flex-1" />
              <span class="text-lg font-bold" :style="{ color: 'var(--accent)' }">{{ form.rating }}/10</span>
            </div>
            <div class="flex gap-1 mt-1 text-lg">
              <span v-for="i in 10" :key="i" class="cursor-pointer" @click="form.rating = i">{{ i <= form.rating ? '⭐' : '☆' }}</span>
            </div>
          </div>
          
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۶- یادداشت</label>
            <textarea v-model="form.notes" rows="3" placeholder="نظرت درباره فیلم..." class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>
          
          <!-- وضعیت دیدن -->
          <div class="flex items-center gap-2 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <input v-model="form.is_watched" type="checkbox" class="w-5 h-5 rounded" />
            <label class="text-sm font-semibold" :style="{ color: form.is_watched ? '#22c55e' : '#f59e0b' }">
              {{ form.is_watched ? '✅ فیلم رو دیدم' : '📋 می‌خوام ببینم' }}
            </label>
          </div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="saveMovie" class="flex-1 py-2.5 rounded-xl text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showForm = false" class="px-4 py-2.5 rounded-xl" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>