<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, Star, Search, Film, Tv, Video, 
  ExternalLink, Sparkles, X, Eye, Filter, Globe, Flag
} from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const movies = ref([])
const message = ref('')
const messageType = ref('success')
const isLoadingImdb = ref(false)

// فیلترهای پیشرفته
const filterSearch = ref('')
const filterGenre = ref('')
const filterType = ref('all')     // all, movie, series, documentary
const filterOrigin = ref('all')   // all, iranian, foreign
const filterRating = ref('all')   // all, 5, 4, 3
const filterStatus = ref('all')   // all, watched, unwatched

// فرم ثبت فیلم
const showModal = ref(false)
const editingMovie = ref(null)
const form = ref({
  title: '',
  movie_type: 'movie',
  origin: 'foreign', // iranian, foreign
  category: 'درام',
  rating: 0,
  notes: '',
  poster_url: '',
  imdb_url: '',
  is_watched: false,
  watch_date: new Date().toISOString().split('T')[0]
})

const randomMovie = ref(null)
const showRandomModal = ref(false)

const genres = ['اکشن', 'درام', 'کمدی', 'علمی‌تخیلی', 'روانشناختی', 'انگیزشی', 'ترسناک', 'مستند', 'انیمیشن', 'عاشقانه', 'سایر']

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchMovies = async () => {
  try {
    const res = await api.get('/movies')
    movies.value = res.data
  } catch (e) { showToast('⚠️ خطا در دریافت لیست فیلم‌ها', 'error') }
}

// جستجوی هوشمند در IMDb همراه با تشخیص نوع اثر و ژانر خودکار
const searchOmdb = async () => {
  if (!form.value.title.trim()) {
    showToast('لطفاً نام انگلیسی فیلم را وارد کنید', 'error')
    return
  }
  isLoadingImdb.value = true
  try {
    const query = encodeURIComponent(form.value.title.trim())
    const res = await fetch(`https://www.omdbapi.com/?t=${query}&apikey=trilogy`)
    const data = await res.json()

    if (data.Response === 'True') {
      form.value.title = data.Title
      
      // ۱. پوستر
      if (data.Poster && data.Poster !== 'N/A') form.value.poster_url = data.Poster
      
      // ۲. لینک IMDb
      if (data.imdbID) form.value.imdb_url = `https://www.imdb.com/title/${data.imdbID}/`

      // ۳. تشخیص نوع اثر (سینمایی / سریال)
      if (data.Type === 'series') form.value.movie_type = 'series'
      else form.value.movie_type = 'movie'

      // ۴. تشخیص خودکار ژانر به فارسی
      if (data.Genre) {
        const gLower = data.Genre.toLowerCase()
        if (gLower.includes('action')) form.value.category = 'اکشن'
        else if (gLower.includes('comedy')) form.value.category = 'کمدی'
        else if (gLower.includes('drama')) form.value.category = 'درام'
        else if (gLower.includes('horror')) form.value.category = 'ترسناک'
        else if (gLower.includes('sci-fi') || gLower.includes('fantasy')) form.value.category = 'علمی‌تخیلی'
        else if (gLower.includes('animation')) form.value.category = 'انیمیشن'
        else if (gLower.includes('documentary')) form.value.category = 'مستند'
        else if (gLower.includes('romance')) form.value.category = 'عاشقانه'
      }

      showToast('✅ پوستر، نوع اثر و ژانر با موفقیت از IMDb دریافت شد!')
    } else {
      showToast('⚠️ فیلمی با این عنوان انگلیسی پیدا نشد', 'error')
    }
  } catch (e) {
    showToast('❌ خطا در ارتباط با سرویس IMDb', 'error')
  } finally {
    isLoadingImdb.value = false
  }
}

// محاسبات فیلتر پیشرفته
const filteredMovies = computed(() => {
  return movies.value.filter(m => {
    const matchSearch = !filterSearch.value || m.title.toLowerCase().includes(filterSearch.value.toLowerCase())
    const matchGenre = !filterGenre.value || m.category === filterGenre.value
    const matchType = filterType.value === 'all' || m.movie_type === filterType.value
    const matchOrigin = filterOrigin.value === 'all' || m.origin === filterOrigin.value
    const matchRating = filterRating.value === 'all' || (m.rating >= Number(filterRating.value))
    const matchStatus = filterStatus.value === 'all' || 
                        (filterStatus.value === 'watched' && m.is_watched) || 
                        (filterStatus.value === 'unwatched' && !m.is_watched)
    return matchSearch && matchGenre && matchType && matchOrigin && matchRating && matchStatus
  })
})

// آمارها
const watchedCount = computed(() => movies.value.filter(m => m.is_watched).length)
const iranianCount = computed(() => movies.value.filter(m => m.origin === 'iranian').length)
const avgRating = computed(() => {
  const watched = movies.value.filter(m => m.is_watched && m.rating > 0)
  if (!watched.length) return 0
  return (watched.reduce((sum, m) => sum + m.rating, 0) / watched.length).toFixed(1)
})

// چی ببینم؟ (Random Picker)
const pickRandomMovie = () => {
  const unwatched = movies.value.filter(m => !m.is_watched)
  if (!unwatched.length) {
    showToast('همه فیلم‌های لیستتان را دیده‌اید!', 'error')
    return
  }
  const randomIndex = Math.floor(Math.random() * unwatched.length)
  randomMovie.value = unwatched[randomIndex]
  showRandomModal.value = true
}

const openNewModal = () => {
  form.value = {
    title: '', movie_type: 'movie', origin: 'foreign', category: 'درام',
    rating: 0, notes: '', poster_url: '', imdb_url: '',
    is_watched: false, watch_date: new Date().toISOString().split('T')[0]
  }
  editingMovie.value = null
  showModal.value = true
}

const openEditModal = (movie) => {
  form.value = { ...movie, origin: movie.origin || 'foreign' }
  editingMovie.value = movie
  showModal.value = true
}

const saveMovie = async () => {
  if (!form.value.title.trim()) return
  try {
    if (editingMovie.value) {
      await api.put(`/movies/${editingMovie.value.id}`, form.value)
      showToast('✅ اطلاعات فیلم بروزرسانی شد')
    } else {
      await api.post('/movies', form.value)
      showToast('✅ فیلم جدید به آرشیو اضافه شد')
    }
    showModal.value = false
    await fetchMovies()
  } catch (e) { showToast('❌ خطا در ذخیره‌سازی', 'error') }
}

const toggleWatched = async (movie) => {
  try {
    const newStatus = !movie.is_watched
    const today = new Date().toISOString().split('T')[0]
    const payload = {
      ...movie,
      is_watched: newStatus,
      watch_date: newStatus ? today : movie.watch_date
    }
    await api.put(`/movies/${movie.id}`, payload)
    await fetchMovies()
    showToast(newStatus ? '🎬 به دیده‌شده‌ها اضافه شد' : '🔄 به دیده‌نشده‌ها برگشت')
  } catch (e) {}
}

const deleteMovie = async (id) => {
  if (!confirm('از حذف این فیلم مطمئن هستید؟')) return
  try { await api.delete(`/movies/${id}`); showToast('🗑️ فیلم حذف شد'); await fetchMovies() } catch (e) {}
}

onMounted(fetchMovies)
</script>

<template>
  <div class="relative min-h-screen text-right p-6 md:p-10 overflow-hidden" dir="rtl">
    
    <!-- پس‌زمینه سالن سینما -->
    <div class="fixed inset-0 z-0 bg-cover bg-center" style="background-image: url('/cinema-bg.jpg');">
      <div class="absolute inset-0 bg-black/35"></div>
    </div>

    <!-- محتوای اصلی -->
    <div class="relative z-10 max-w-7xl mx-auto space-y-8 text-white">

      <!-- Toast -->
      <div v-if="message" class="fixed top-24 left-1/2 -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl font-semibold"
           :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
        {{ message }}
      </div>

      <!-- هدر -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-3xl bg-black/40 backdrop-blur-md border border-white/10 shadow-2xl">
        <div>
          <h1 class="text-3xl font-black mb-1 drop-shadow-md">آرشیو سینمایی من</h1>
          <p class="text-xs opacity-70">کالکشن هوشمند فیلم‌ها، سریال‌ها و آثار سینمایی</p>
        </div>
        <div class="flex gap-3">
          <button @click="pickRandomMovie" class="px-5 py-3 rounded-2xl font-bold text-white transition flex items-center gap-2 shadow-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:scale-105 active:scale-95">
            <Sparkles class="w-5 h-5 text-yellow-300" /> چی ببینم؟
          </button>
          <button @click="openNewModal" class="px-5 py-3 rounded-2xl font-bold text-white transition flex items-center gap-2 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
            <Plus class="w-5 h-5" /> افزودن فیلم
          </button>
        </div>
      </div>

      <!-- داشبورد آمار -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center"><Film class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">کل عناوین</p>
            <p class="text-2xl font-black">{{ movies.length }} عنوان</p>
          </div>
        </div>

        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-green-500/20 text-green-400 flex items-center justify-center"><Eye class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">دیده‌شده‌ها</p>
            <p class="text-2xl font-black text-green-400">{{ watchedCount }} عنوان</p>
          </div>
        </div>

        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center"><Flag class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">آثار ایرانی</p>
            <p class="text-2xl font-black text-amber-400">{{ iranianCount }} عنوان</p>
          </div>
        </div>

        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-yellow-500/20 text-yellow-400 flex items-center justify-center"><Star class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">میانگین امتیاز</p>
            <p class="text-2xl font-black text-yellow-400">{{ avgRating }} / ۵</p>
          </div>
        </div>
      </div>

      <!-- ابزارهای فیلتر پیشرفته (Filter Bar) -->
      <div class="p-5 rounded-3xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl space-y-4">
        <div class="flex items-center gap-3 border-b border-white/10 pb-3">
          <Search class="w-5 h-5 opacity-40" />
          <input v-model="filterSearch" placeholder="جستجوی نام فیلم..." class="w-full bg-transparent outline-none text-sm placeholder-white/40" />
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          <!-- ایرانی / خارجی -->
          <select v-model="filterOrigin" class="px-3 py-2 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option value="all">همه کشورها (ایرانی/خارجی)</option>
            <option value="iranian">فقط فیلم‌های ایرانی 🇮🇷</option>
            <option value="foreign">فقط فیلم‌های خارجی 🌐</option>
          </select>

          <!-- سینمایی / سریال / مستند -->
          <select v-model="filterType" class="px-3 py-2 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option value="all">همه انواع اثر</option>
            <option value="movie">فقط سینمایی</option>
            <option value="series">فقط سریال</option>
            <option value="documentary">فقط مستند</option>
          </select>

          <!-- ژانر -->
          <select v-model="filterGenre" class="px-3 py-2 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option value="">همه ژانرها</option>
            <option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
          </select>

          <!-- امتیاز -->
          <select v-model="filterRating" class="px-3 py-2 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option value="all">همه امتیازها</option>
            <option value="5">فقط ۵ ستاره‌ها ⭐⭐⭐⭐⭐</option>
            <option value="4">۴ ستاره به بالا ⭐⭐⭐⭐</option>
            <option value="3">۳ ستاره به بالا ⭐⭐⭐</option>
          </select>

          <!-- وضعیت -->
          <select v-model="filterStatus" class="px-3 py-2 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option value="all">همه وضعیت‌ها</option>
            <option value="watched">دیده‌شده‌ها</option>
            <option value="unwatched">لیست انتظار (دیده‌نشده)</option>
          </select>
        </div>
      </div>

      <!-- گالری پوستر فیلم‌ها -->
      <div v-if="filteredMovies.length === 0" class="text-center py-20 opacity-40">
        <Film class="w-16 h-16 mx-auto mb-4" />
        <p class="text-lg font-bold">فیلمی با این فیلترها یافت نشد</p>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
        <div v-for="m in filteredMovies" :key="m.id" 
             class="group relative rounded-3xl overflow-hidden border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl flex flex-col justify-between">
          
          <!-- پوستر فیلم -->
          <div class="relative aspect-[2/3] w-full bg-black/60 overflow-hidden">
            <img v-if="m.poster_url" :src="m.poster_url" :alt="m.title" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
            <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 text-center opacity-30">
              <Film class="w-12 h-12 mb-2" />
              <span class="text-xs">بدون پوستر</span>
            </div>

            <!-- بج وضعیت دیده‌شده -->
            <button @click="toggleWatched(m)" class="absolute top-3 right-3 p-2 rounded-2xl backdrop-blur-md transition-all shadow-md"
                    :class="m.is_watched ? 'bg-green-500 text-white' : 'bg-black/60 text-white/70 hover:bg-black/80'">
              <Check class="w-4 h-4" />
            </button>

            <!-- بج ایرانی / خارجی -->
            <span class="absolute top-3 left-3 px-2 py-1 rounded-xl text-[10px] font-bold bg-black/60 backdrop-blur-md text-white border border-white/10">
              {{ m.origin === 'iranian' ? '🇮🇷 ایرانی' : '🌐 خارجی' }}
            </span>

            <!-- اوورلی هاور -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-4 flex flex-col justify-end gap-2">
              <a v-if="m.imdb_url" :href="m.imdb_url" target="_blank" class="px-3 py-2 rounded-xl bg-yellow-500 text-black font-black text-xs flex items-center justify-center gap-1 shadow-md hover:scale-105 transition">
                مشاهده در IMDb <ExternalLink class="w-3.5 h-3.5" />
              </a>
              <div class="flex gap-2">
                <button @click="openEditModal(m)" class="flex-1 py-2 rounded-xl bg-white/20 text-white text-xs font-bold hover:bg-white/30 backdrop-blur-sm"><Edit3 class="w-4 h-4 mx-auto" /></button>
                <button @click="deleteMovie(m.id)" class="py-2 px-3 rounded-xl bg-red-500/80 text-white text-xs font-bold hover:bg-red-500 backdrop-blur-sm"><Trash2 class="w-4 h-4" /></button>
              </div>
            </div>
          </div>

          <!-- اطلاعات پایین کارت -->
          <div class="p-4 space-y-2">
            <h3 class="font-bold text-base truncate">{{ m.title }}</h3>
            
            <div class="flex items-center justify-between text-xs opacity-70">
              <span>{{ m.category }}</span>
              <span v-if="m.is_watched && m.watch_date">{{ formatDate(m.watch_date) }}</span>
            </div>

            <!-- امتیاز ستاره‌ای -->
            <div v-if="m.is_watched" class="flex gap-1 text-yellow-400 pt-1">
              <Star v-for="i in 5" :key="i" class="w-3.5 h-3.5" :class="i <= m.rating ? 'fill-yellow-400' : 'opacity-20'" />
            </div>
          </div>
        </div>
      </div>

      <!-- ========== مودال افزودن/ویرایش فیلم ========== -->
      <div v-if="showModal" class="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" @click.self="showModal = false">
        <div class="w-full max-w-lg rounded-3xl p-8 bg-gray-900 border border-white/10 shadow-2xl space-y-5 text-white">
          <div class="flex justify-between items-center">
            <h3 class="text-xl font-black">{{ editingMovie ? 'ویرایش اطلاعات فیلم' : 'افزودن به آرشیو' }}</h3>
            <button @click="showModal = false" class="p-1 hover:bg-white/10 rounded-full"><X /></button>
          </div>

          <div class="space-y-4 text-right" dir="rtl">
            <div>
              <label class="text-xs mb-1.5 block opacity-70">عنوان (انگلیسی برای دریافت پوستر خودکار) *</label>
              <div class="flex gap-2">
                <input v-model="form.title" placeholder="مثلاً: Inception" class="flex-1 px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
                <button @click="searchOmdb" :disabled="isLoadingImdb" class="px-4 py-3 rounded-xl font-bold text-xs bg-yellow-500 text-black flex items-center gap-1 shadow-md hover:bg-yellow-400 disabled:opacity-50">
                  <Sparkles class="w-4 h-4" /> {{ isLoadingImdb ? 'در حال دریافت...' : 'جستجوی IMDb' }}
                </button>
              </div>
            </div>

            <!-- کادر جدید: انتخاب ایرانی / خارجی -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs mb-1.5 block opacity-70">منشأ اثر</label>
                <div class="flex gap-2 p-1 rounded-xl bg-black/40 border border-white/10">
                  <button type="button" @click="form.origin = 'foreign'"
                          class="flex-1 py-2 rounded-lg text-xs font-bold transition"
                          :class="form.origin === 'foreign' ? 'bg-purple-600 text-white shadow' : 'opacity-50'">
                    🌐 خارجی
                  </button>
                  <button type="button" @click="form.origin = 'iranian'"
                          class="flex-1 py-2 rounded-lg text-xs font-bold transition"
                          :class="form.origin === 'iranian' ? 'bg-amber-600 text-white shadow' : 'opacity-50'">
                    🇮🇷 ایرانی
                  </button>
                </div>
              </div>

              <div>
                <label class="text-xs mb-1.5 block opacity-70">نوع اثر</label>
                <select v-model="form.movie_type" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 text-xs outline-none">
                  <option value="movie">سینمایی</option>
                  <option value="series">سریال</option>
                  <option value="documentary">مستند</option>
                </select>
              </div>
            </div>

            <div>
              <label class="text-xs mb-1.5 block opacity-70">ژانر</label>
              <select v-model="form.category" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 text-xs outline-none">
                <option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
              </select>
            </div>

            <div>
              <label class="text-xs mb-1.5 block opacity-70">آدرس تصویر پوستر (URL)</label>
              <input v-model="form.poster_url" placeholder="https://..." dir="ltr" class="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-xs" />
              
              <div v-if="form.poster_url" class="mt-3 flex items-center gap-3 p-2 rounded-xl bg-white/5 border border-white/10">
                <img :src="form.poster_url" class="w-12 h-16 object-cover rounded-lg shadow-md" />
                <div>
                  <p class="text-xs font-bold text-green-400">پیش‌نمایش پوستر آماده است</p>
                  <p class="text-[10px] opacity-50">امکان تعویض دستی آدرس عکس وجود دارد.</p>
                </div>
              </div>
            </div>

            <div class="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
              <label class="flex items-center gap-3 cursor-pointer text-sm font-bold">
                <input type="checkbox" v-model="form.is_watched" class="w-5 h-5 rounded-lg" />
                این فیلم را دیده‌ام
              </label>

              <div v-if="form.is_watched" class="space-y-3 pt-2">
                <div>
                  <label class="text-xs mb-1 block opacity-70">امتیاز شما (۱ تا ۵ ستاره):</label>
                  <div class="flex gap-2 text-yellow-400">
                    <button v-for="star in 5" :key="star" @click="form.rating = star" type="button" class="p-1 hover:scale-125 transition">
                      <Star class="w-6 h-6" :class="star <= form.rating ? 'fill-yellow-400' : 'opacity-20'" />
                    </button>
                  </div>
                </div>
                <div>
                  <label class="text-xs mb-1 block opacity-70">تاریخ تماشا:</label>
                  <DateInputPersian v-model="form.watch_date" />
                </div>
              </div>
            </div>

            <div>
              <label class="text-xs mb-1.5 block opacity-70">یادداشت / نقد شما</label>
              <textarea v-model="form.notes" rows="2" placeholder="حس شما بعد از دیدن این فیلم..." class="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm"></textarea>
            </div>
          </div>

          <div class="flex gap-3 mt-6">
            <button @click="saveMovie" class="flex-1 py-3.5 rounded-2xl text-white font-bold shadow-lg shadow-purple-500/20" :style="{ background: 'var(--accent)' }">ذخیره فیلم</button>
            <button @click="showModal = false" class="px-6 py-3.5 rounded-2xl font-semibold bg-white/10 hover:bg-white/20">انصراف</button>
          </div>
        </div>
      </div>

      <!-- ========== مودال چی ببینم؟ ========== -->
      <div v-if="showRandomModal" class="fixed inset-0 z-[400] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" @click.self="showRandomModal = false">
        <div class="w-full max-w-sm rounded-3xl p-8 text-center space-y-6 bg-gray-900 border border-white/10 shadow-2xl animate-in zoom-in duration-300">
          <div class="w-16 h-16 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center mx-auto">
            <Sparkles class="w-8 h-8 animate-pulse" />
          </div>

          <div>
            <p class="text-xs font-bold text-purple-400 mb-1">پیشنهاد هوشمند امشب شما:</p>
            <h2 class="text-2xl font-black mb-2">{{ randomMovie?.title }}</h2>
            <p class="text-xs opacity-60">{{ randomMovie?.category }}</p>
          </div>

          <div v-if="randomMovie?.poster_url" class="aspect-[2/3] w-40 mx-auto rounded-2xl overflow-hidden shadow-2xl border border-white/10">
            <img :src="randomMovie.poster_url" class="w-full h-full object-cover" />
          </div>

          <div class="flex gap-3">
            <button @click="toggleWatched(randomMovie); showRandomModal = false" class="flex-1 py-3 rounded-xl bg-green-500 text-white font-bold text-xs shadow-lg">دیدمش!</button>
            <button @click="pickRandomMovie" class="flex-1 py-3 rounded-xl bg-purple-600 text-white font-bold text-xs shadow-lg">یکی دیگه پیشنهاد بده</button>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>