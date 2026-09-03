<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, Check, Star, Search, BookOpen, 
  Bookmark, User, Calendar, X, Eye, BookMarked
} from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const books = ref([])
const message = ref('')
const messageType = ref('success')

// فیلترها
const filterSearch = ref('')
const filterCategory = ref('')
const filterStatus = ref('all') // all, read, unread

// فرم کتاب
const showModal = ref(false)
const editingBook = ref(null)
const form = ref({
  title: '',
  author: '',
  category: 'توسعه فردی',
  rating: 0,
  notes: '',
  is_read: false,
  read_date: new Date().toISOString().split('T')[0]
})

const categoriesList = ['توسعه فردی', 'روانشناسی', 'مدیریت و کسب‌وکار', 'رمان و ادبیات', 'فلسفه', 'تکنولوژی', 'تاریخی', 'سایر']

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchBooks = async () => {
  try {
    const res = await api.get('/books')
    books.value = res.data
  } catch (e) { showToast('⚠️ خطا در دریافت لیست کتاب‌ها', 'error') }
}

// محاسبات آمار کتابخوانی
const readCount = computed(() => books.value.filter(b => b.is_read).length)
const avgRating = computed(() => {
  const read = books.value.filter(b => b.is_read && b.rating > 0)
  if (!read.length) return 0
  return (read.reduce((sum, b) => sum + b.rating, 0) / read.length).toFixed(1)
})

// محاسبه فیلترها
const filteredBooks = computed(() => {
  return books.value.filter(b => {
    const matchSearch = !filterSearch.value || 
                        b.title.toLowerCase().includes(filterSearch.value.toLowerCase()) ||
                        (b.author && b.author.toLowerCase().includes(filterSearch.value.toLowerCase()))
    const matchCategory = !filterCategory.value || b.category === filterCategory.value
    const matchStatus = filterStatus.value === 'all' || 
                        (filterStatus.value === 'read' && b.is_read) || 
                        (filterStatus.value === 'unread' && !b.is_read)
    return matchSearch && matchCategory && matchStatus
  })
})

const openNewModal = () => {
  form.value = {
    title: '', author: '', category: 'توسعه فردی',
    rating: 0, notes: '', is_read: false,
    read_date: new Date().toISOString().split('T')[0]
  }
  editingBook.value = null
  showModal.value = true
}

const openEditModal = (book) => {
  form.value = { ...book }
  editingBook.value = book
  showModal.value = true
}

const saveBook = async () => {
  if (!form.value.title.trim()) return
  try {
    if (editingBook.value) {
      await api.put(`/books/${editingBook.value.id}`, form.value)
      showToast('✅ اطلاعات کتاب بروزرسانی شد')
    } else {
      await api.post('/books', form.value)
      showToast('✅ کتاب جدید به کتابخانه اضافه شد')
    }
    showModal.value = false
    await fetchBooks()
  } catch (e) { showToast('❌ خطا در ذخیره‌سازی', 'error') }
}

// اصلاح باگ تاریخ در دکمه خواندم (ارسال تاریخ کوتاه YYYY-MM-DD)
const toggleRead = async (book) => {
  try {
    const newStatus = !book.is_read
    const today = new Date().toISOString().split('T')[0]
    const payload = {
      ...book,
      is_read: newStatus,
      read_date: newStatus ? today : book.read_date
    }
    await api.put(`/books/${book.id}`, payload)
    await fetchBooks()
    showToast(newStatus ? '📖 به لیست خوانده‌شده‌ها اضافه شد' : '🔄 به لیست در حال مطالعه برگشت')
  } catch (e) {}
}

const deleteBook = async (id) => {
  if (!confirm('آیا از حذف این کتاب مطمئن هستید؟')) return
  try { await api.delete(`/books/${id}`); showToast('🗑️ کتاب حذف شد'); await fetchBooks() } catch (e) {}
}

onMounted(fetchBooks)
</script>

<template>
  <div class="relative min-h-screen text-right p-3 sm:p-4 md:p-8 lg:p-10 overflow-hidden" dir="rtl">

    <!-- پس‌زمینه شیشه‌ای gradient (هماهنگ با داشبورد) -->
    <div class="fixed inset-0 z-0 bg-cover bg-center"
         style="background-image: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 50%, #831843 100%);">
      <div class="absolute inset-0 bg-black/30"></div>
    </div>

    <!-- ۲. محتوای اصلی رو لایه شیشه‌ای -->
    <div class="relative z-10 max-w-7xl mx-auto space-y-8 text-white">

      <!-- Toast -->
      <div v-if="message" class="fixed top-24 left-1/2 -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl font-semibold"
           :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
        {{ message }}
      </div>

      <!-- هدر صفحه -->
      <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4">
        <div>
          <h1 class="text-xl sm:text-2xl md:text-3xl font-black mb-1 drop-shadow-md flex items-center gap-2">
            <BookOpen class="w-6 h-6 sm:w-7 sm:h-7 text-amber-400" />
            کتابخانه شخصی من
          </h1>
          <p class="text-[11px] sm:text-xs opacity-70">آرشیو کتاب‌های خوانده‌شده و لیست مطالعه آتی</p>
        </div>
        <button @click="openNewModal" class="px-3 sm:px-5 py-2 sm:py-3 rounded-xl sm:rounded-2xl font-bold text-white text-xs sm:text-sm transition flex items-center gap-1.5 sm:gap-2 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
          <Plus class="w-4 h-4 sm:w-5 sm:h-5" /> <span class="hidden sm:inline">افزودن کتاب جدید</span><span class="sm:hidden">کتاب</span>
        </button>
      </div>

      <!-- داشبورد آمار مطالعه -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3 md:gap-4">
        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex items-center gap-2.5 sm:gap-3 md:gap-4">
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0"><BookOpen class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" /></div>
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs opacity-60 truncate">کل کتاب‌های کتابخانه</p>
            <p class="text-lg sm:text-2xl md:text-3xl font-black truncate">{{ books.length }} <span class="text-xs sm:text-sm">جلد</span></p>
          </div>
        </div>

        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex items-center gap-2.5 sm:gap-3 md:gap-4">
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-green-500/20 text-green-400 flex items-center justify-center flex-shrink-0"><BookMarked class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" /></div>
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs opacity-60 truncate">خوانده‌شده‌ها</p>
            <p class="text-lg sm:text-2xl md:text-3xl font-black text-green-400 truncate">{{ readCount }} <span class="text-xs sm:text-sm">جلد</span></p>
          </div>
        </div>

        <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex items-center gap-2.5 sm:gap-3 md:gap-4">
          <div class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-yellow-500/20 text-yellow-400 flex items-center justify-center flex-shrink-0"><Star class="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" /></div>
          <div class="min-w-0">
            <p class="text-[10px] sm:text-xs opacity-60 truncate">میانگین امتیاز</p>
            <p class="text-lg sm:text-2xl md:text-3xl font-black text-yellow-400 truncate">{{ avgRating }} <span class="text-xs sm:text-sm">/ ۵</span></p>
          </div>
        </div>
      </div>

      <!-- نوار جستجو و فیلتر -->
      <div class="glass-card p-3 sm:p-4 md:p-5 rounded-2xl md:rounded-3xl border border-white/10 flex flex-col sm:flex-row gap-3 sm:gap-4 sm:items-center sm:justify-between">
        <div class="flex items-center gap-2.5 sm:gap-3 flex-1 min-w-0">
          <Search class="w-4 h-4 sm:w-5 sm:h-5 opacity-40 flex-shrink-0" />
          <input v-model="filterSearch" placeholder="جستجوی عنوان کتاب یا نویسنده..." class="w-full bg-transparent outline-none text-xs sm:text-sm placeholder-white/40" />
        </div>

        <div class="flex flex-wrap gap-2 sm:gap-3">
          <select v-model="filterCategory" class="px-2.5 sm:px-3 py-2 rounded-xl border border-white/10 bg-black/40 text-[11px] sm:text-xs outline-none">
            <option value="">همه دسته‌ها</option>
            <option v-for="c in categoriesList" :key="c" :value="c">{{ c }}</option>
          </select>

          <select v-model="filterStatus" class="px-2.5 sm:px-3 py-2 rounded-xl border border-white/10 bg-black/40 text-[11px] sm:text-xs outline-none">
            <option value="all">همه وضعیت‌ها</option>
            <option value="read">خوانده‌شده</option>
            <option value="unread">در حال مطالعه</option>
          </select>
        </div>
      </div>

      <!-- لیست کارت‌های کتاب چوبی و شیشه‌ای -->
      <div v-if="filteredBooks.length === 0" class="text-center py-20 opacity-40">
        <BookOpen class="w-16 h-16 mx-auto mb-4" />
        <p class="text-lg font-bold">کتابی یافت نشد</p>
      </div>

      <div class="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
        <div v-for="b in filteredBooks" :key="b.id"
             class="group relative rounded-2xl md:rounded-3xl p-3 sm:p-4 md:p-6 border border-white/10 bg-black/30 backdrop-blur-xl shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-amber-500/40 flex flex-col justify-between">

          <div class="space-y-2.5 sm:space-y-4">
            <!-- هدر کارت: عنوان + دکمه وضعیت -->
            <div class="flex items-start justify-between gap-2 sm:gap-3">
              <div class="flex items-start gap-2 sm:gap-3 min-w-0">
                <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0 mt-0.5 sm:mt-1">
                  <Bookmark class="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <div class="min-w-0">
                  <h3 class="font-bold text-xs sm:text-base md:text-lg leading-snug line-clamp-2">{{ b.title }}</h3>
                  <p v-if="b.author" class="text-[10px] sm:text-xs opacity-60 flex items-center gap-1 mt-0.5 sm:mt-1 truncate">
                    <User class="w-2.5 h-2.5 sm:w-3 sm:h-3 flex-shrink-0" /> <span class="truncate">{{ b.author }}</span>
                  </p>
                </div>
              </div>

              <!-- دکمه تیک خوانده‌شده -->
              <button @click="toggleRead(b)" class="p-1.5 sm:p-2 rounded-lg sm:rounded-2xl backdrop-blur-md transition shadow-md shrink-0"
                      :class="b.is_read ? 'bg-green-500 text-white' : 'bg-white/10 text-white/50 hover:bg-white/20'">
                <Check class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </button>
            </div>

            <!-- دسته و یادداشت -->
            <div class="space-y-1.5 sm:space-y-2">
              <span class="inline-block text-[9px] sm:text-[10px] px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-md sm:rounded-lg bg-white/10 font-bold opacity-80">
                {{ b.category }}
              </span>
              <p v-if="b.notes" class="text-[10px] sm:text-xs opacity-70 leading-relaxed border-r-2 border-amber-500/40 pr-2 sm:pr-3 py-1 bg-white/[0.02] rounded-r-lg line-clamp-2">
                {{ b.notes }}
              </p>
            </div>
          </div>

          <!-- فوتر کارت: امتیاز و تاریخ -->
          <div class="pt-2.5 sm:pt-4 border-t border-white/10 mt-2.5 sm:mt-4 flex items-center justify-between text-[10px] sm:text-xs">
            <div>
              <div v-if="b.is_read" class="flex gap-0.5 sm:gap-1 text-yellow-400">
                <Star v-for="i in 5" :key="i" class="w-3 h-3 sm:w-3.5 sm:h-3.5" :class="i <= b.rating ? 'fill-yellow-400' : 'opacity-20'" />
              </div>
              <span v-else class="opacity-40 text-[9px] sm:text-[10px]">در حال مطالعه</span>
            </div>

            <div class="flex items-center gap-1.5 sm:gap-3">
              <span v-if="b.is_read && b.read_date" class="opacity-50 text-[9px] sm:text-[10px] flex items-center gap-0.5 sm:gap-1">
                <Calendar class="w-2.5 h-2.5 sm:w-3 sm:h-3" /> {{ formatDate(b.read_date) }}
              </span>
              <div class="flex gap-0.5 sm:gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click="openEditModal(b)" class="p-1 sm:p-1.5 rounded-md sm:rounded-lg hover:bg-white/10 opacity-70 hover:opacity-100"><Edit3 class="w-3 h-3 sm:w-4 sm:h-4" /></button>
                <button @click="deleteBook(b.id)" class="p-1 sm:p-1.5 rounded-md sm:rounded-lg hover:bg-red-500/20 text-red-400"><Trash2 class="w-3 h-3 sm:w-4 sm:h-4" /></button>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- ========== مودال افزودن/ویرایش کتاب ========== -->
      <div v-if="showModal" class="fixed inset-0 z-[300] flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md" @click.self="showModal = false">
        <div class="w-full max-w-lg max-h-[92vh] overflow-y-auto rounded-2xl sm:rounded-3xl p-5 sm:p-7 bg-gray-900/95 border border-white/10 shadow-2xl shadow-black/50 text-white space-y-4 sm:space-y-5">

          <!-- هدر مودال -->
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <h3 class="text-lg sm:text-xl font-black flex items-center gap-2">
              <BookOpen class="w-5 h-5 text-amber-400" />
              {{ editingBook ? 'ویرایش کتاب' : 'افزودن کتاب جدید' }}
            </h3>
            <button @click="showModal = false" class="p-1.5 rounded-lg hover:bg-white/10 transition text-slate-400 hover:text-white">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="space-y-3 sm:space-y-4 text-right" dir="rtl">
            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">عنوان کتاب *</label>
              <input v-model="form.title" placeholder="مثلاً: اثر مرکب"
                     class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-xs sm:text-sm focus:ring-2 focus:ring-amber-500/50" />
            </div>

            <div class="grid grid-cols-2 gap-2 sm:gap-3">
              <div>
                <label class="text-xs mb-1.5 block opacity-70 font-bold">نویسنده</label>
                <input v-model="form.author" placeholder="مثلاً: دارن هاردی"
                       class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-xs sm:text-sm focus:ring-2 focus:ring-amber-500/50" />
              </div>
              <div>
                <label class="text-xs mb-1.5 block opacity-70 font-bold">دسته‌بندی</label>
                <select v-model="form.category" class="w-full px-2.5 sm:px-3 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 text-[11px] sm:text-xs outline-none">
                  <option v-for="c in categoriesList" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
            </div>

            <!-- وضعیت خوانده‌شده -->
            <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10 space-y-3">
              <label class="flex items-center gap-2.5 cursor-pointer text-xs sm:text-sm font-bold">
                <input type="checkbox" v-model="form.is_read" class="w-4 h-4 sm:w-5 sm:h-5 rounded-md" />
                این کتاب را خوانده‌ام
              </label>

              <div v-if="form.is_read" class="space-y-3 pt-1">
                <div>
                  <label class="text-xs mb-1 block opacity-70 font-bold">امتیاز (۱ تا ۵):</label>
                  <div class="flex gap-1 text-yellow-400">
                    <button v-for="star in 5" :key="star" @click="form.rating = star" type="button" class="p-1 hover:scale-125 transition">
                      <Star class="w-5 h-5 sm:w-6 sm:h-6" :class="star <= form.rating ? 'fill-yellow-400' : 'opacity-20'" />
                    </button>
                  </div>
                </div>
                <div>
                  <label class="text-xs mb-1 block opacity-70 font-bold">تاریخ اتمام:</label>
                  <DateInputPersian v-model="form.read_date" />
                </div>
              </div>
            </div>

            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">یادداشت / جملات برتر</label>
              <textarea v-model="form.notes" rows="3" placeholder="نکته کلیدی از کتاب..."
                        class="w-full px-3 sm:px-4 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-xs sm:text-sm focus:ring-2 focus:ring-amber-500/50 resize-none"></textarea>
            </div>
          </div>

          <!-- دکمه‌های تأیید/انصراف (همیشه در پایین مودال) -->
          <div class="flex gap-2 sm:gap-3 pt-2 sticky bottom-0 bg-gray-900/95 -mx-5 sm:-mx-7 -mb-5 sm:-mb-7 px-5 sm:px-7 py-3 sm:py-4 border-t border-white/10">
            <button @click="saveBook" class="flex-1 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl text-white font-bold text-sm sm:text-base shadow-lg shadow-amber-500/20"
                    :style="{ background: 'var(--accent)' }">
              {{ editingBook ? 'ذخیره تغییرات' : 'افزودن کتاب' }}
            </button>
            <button @click="showModal = false" class="px-4 sm:px-6 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl text-sm sm:text-base font-semibold bg-white/10 hover:bg-white/20 transition">
              انصراف
            </button>
          </div>

        </div>
      </div>

    </div>

  </div>
</template>

<style scoped>
.glass-card {
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>