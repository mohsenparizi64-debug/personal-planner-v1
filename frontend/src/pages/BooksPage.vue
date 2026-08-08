<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, X, BookOpen, Star, Calendar, Eye, EyeOff, ChevronDown, ChevronUp, Search } from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const books = ref([])
const categories = ref([])
const showForm = ref(false)
const editingBook = ref(null)
const message = ref('')
const messageType = ref('success')
const showAll = ref(true)
const expandedBooks = ref({})
const searchQuery = ref('')
const filterCategory = ref('')
const filterRead = ref(null)

const form = ref({
  title: '', author: '', category: '', register_date: new Date().toISOString().split('T')[0],
  read_date: '', rating: 0, notes: '', is_read: false
})

const categoryLabels = {
  'novel': 'رمان', 'science': 'علمی', 'history': 'تاریخی', 'philosophy': 'فلسفه',
  'psychology': 'روانشناسی', 'business': 'کسب‌وکار', 'poetry': 'شعر',
  'biography': 'زندگی‌نامه', 'other': 'سایر'
}

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchBooks = async () => {
  try { const res = await api.get('/books'); books.value = res.data } catch (e) {}
}

const fetchCategories = async () => {
  try { const res = await api.get('/books/categories'); categories.value = res.data } catch (e) {}
}

const filteredBooks = computed(() => {
  let result = books.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(b => b.title.toLowerCase().includes(q) || (b.author && b.author.toLowerCase().includes(q)))
  }
  if (filterCategory.value) result = result.filter(b => b.category === filterCategory.value)
  if (filterRead.value === 'read') result = result.filter(b => b.is_read)
  if (filterRead.value === 'unread') result = result.filter(b => !b.is_read)
  return result
})

const resetFilters = () => { searchQuery.value = ''; filterCategory.value = ''; filterRead.value = null }

const openNewForm = () => {
  form.value = { title: '', author: '', category: '', register_date: new Date().toISOString().split('T')[0], read_date: '', rating: 0, notes: '', is_read: false }
  editingBook.value = null; showForm.value = true
}

const openEditForm = (book) => {
  form.value = { ...book }
  editingBook.value = book; showForm.value = true
}

const saveBook = async () => {
  if (!form.value.title.trim()) return
  try {
    const data = { ...form.value }
    if (!data.is_read) { data.read_date = null; data.rating = 0 }
    if (editingBook.value) {
      await api.put(`/books/${editingBook.value.id}`, data)
      showToast('✅ کتاب بروزرسانی شد')
    } else {
      await api.post('/books', data)
      showToast('✅ کتاب اضافه شد')
    }
    showForm.value = false; editingBook.value = null; await fetchBooks()
  } catch (e) { showToast('❌ خطا', 'error') }
}

const toggleRead = async (book) => {
  await api.put(`/books/${book.id}`, { is_read: !book.is_read, read_date: !book.is_read ? new Date().toISOString().split('T')[0] : book.read_date })
  await fetchBooks()
}

const deleteBook = async (id) => {
  if (!confirm('مطمئنی؟')) return
  try { await api.delete(`/books/${id}`); showToast('🗑️ حذف شد'); await fetchBooks() } catch (e) {}
}

const toggleExpand = (id) => { expandedBooks.value[id] = !expandedBooks.value[id] }

const starRating = (rating) => '⭐'.repeat(Math.round(rating / 2)) + (rating === 0 ? '' : ` (${rating}/10)`)

onMounted(() => { fetchBooks(); fetchCategories() })
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen">
    
    <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-extrabold mb-1" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">لیست کتاب‌ها</h1>
        <p :style="{ color: 'var(--text-secondary)' }">{{ filteredBooks.length }} کتاب</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button @click="showAll = !showAll" class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm"
                :style="showAll ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <Eye v-if="showAll" class="w-4 h-4" /> <EyeOff v-else class="w-4 h-4" />
          {{ showAll ? 'مخفی کردن' : 'نمایش همه' }}
        </button>
        <button @click="openNewForm" class="px-5 py-2 rounded-xl text-white font-semibold transition flex items-center gap-2" :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> کتاب جدید
        </button>
      </div>
    </div>

    <div class="mb-6 p-4 rounded-xl space-y-3" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      <div class="relative">
        <Search class="absolute right-3 top-2.5 w-5 h-5" :style="{ color: 'var(--text-secondary)' }" />
        <input v-model="searchQuery" placeholder="جستجوی کتاب یا نویسنده..." class="w-full pr-10 pl-4 py-2.5 rounded-lg text-sm"
               :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
      </div>
      <div class="grid grid-cols-3 gap-2">
        <select v-model="filterCategory" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option value="">همه دسته‌بندی‌ها</option>
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <select v-model="filterRead" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option :value="null">همه</option>
          <option value="read">خوانده شده</option>
          <option value="unread">خوانده نشده</option>
        </select>
        <button @click="resetFilters" class="px-3 py-2 rounded-lg text-sm transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">حذف فیلترها</button>
      </div>
    </div>

    <div v-if="filteredBooks.length === 0" class="text-center py-20">
      <BookOpen class="w-16 h-16 mx-auto mb-4" :style="{ color: 'var(--accent)' }" />
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">هنوز کتابی ثبت نکردی!</p>
    </div>

    <div v-if="showAll" class="space-y-3">
      <div v-for="book in filteredBooks" :key="book.id"
           class="rounded-xl overflow-hidden transition-all duration-200 border"
           :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)', opacity: book.is_read ? 0.6 : 1 }">
        
        <div class="flex items-center gap-3 p-4 cursor-pointer" @click="toggleExpand(book.id)">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
               :style="{ background: book.is_read ? 'rgba(34,197,94,0.15)' : 'var(--bg-hover)' }">
            {{ book.is_read ? '✅' : '📖' }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-bold" :style="{ color: 'var(--text-primary)', textDecoration: book.is_read ? 'line-through' : 'none' }">{{ book.title }}</h3>
            <div class="flex gap-2 text-xs mt-0.5" :style="{ color: 'var(--text-secondary)' }">
              <span v-if="book.author">{{ book.author }}</span>
              <span v-if="book.category">{{ categoryLabels[book.category] || book.category }}</span>
              <span v-if="book.rating">{{ starRating(book.rating) }}</span>
            </div>
          </div>
          <div class="flex gap-1 flex-shrink-0" @click.stop>
            <button @click="toggleRead(book)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: book.is_read ? '#22c55e' : 'var(--text-secondary)' }">
              <Eye v-if="!book.is_read" class="w-4 h-4" /><EyeOff v-else class="w-4 h-4" />
            </button>
            <button @click="openEditForm(book)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-4 h-4" /></button>
            <button @click="deleteBook(book.id)" class="p-1.5 rounded-lg hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-4 h-4" /></button>
            <button class="p-1.5" :style="{ color: 'var(--text-secondary)' }">
              <ChevronDown v-if="!expandedBooks[book.id]" class="w-4 h-4" /><ChevronUp v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div v-if="expandedBooks[book.id]" class="px-4 pb-4 border-t" :style="{ borderColor: 'var(--border)' }">
          <div class="grid grid-cols-2 gap-3 mt-3 text-sm">
            <div><span :style="{ color: 'var(--text-secondary)' }">نویسنده:</span> <span :style="{ color: 'var(--text-primary)' }">{{ book.author || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت:</span> <span :style="{ color: 'var(--text-primary)' }">{{ formatDate(book.register_date) || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ خواندن:</span> <span :style="{ color: 'var(--text-primary)' }">{{ formatDate(book.read_date) || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">امتیاز:</span> <span :style="{ color: 'var(--accent)' }">{{ book.rating || '-' }}/10</span></div>
          </div>
          <div v-if="book.notes" class="mt-3 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <p class="text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">یادداشت:</p>
            <p class="text-sm" :style="{ color: 'var(--text-primary)' }">{{ book.notes }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== مودال ========== -->
    <div v-if="showForm" class="fixed inset-0 z-[100] flex items-start justify-center p-4 pt-20 pb-20 bg-black/60 backdrop-blur-sm overflow-y-auto" @click.self="showForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingBook ? 'ویرایش کتاب' : 'کتاب جدید' }}</h3>
          <button @click="showForm = false" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت</label>
            <DateInputPersian v-model="form.register_date" placeholder="تاریخ ثبت" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">نام کتاب *</label>
            <input v-model="form.title" placeholder="نام کتاب" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">نویسنده</label>
            <input v-model="form.author" placeholder="نام نویسنده" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">دسته‌بندی</label>
            <select v-model="form.category" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="">انتخاب کنید...</option>
              <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
          </div>
          <div v-if="form.is_read">
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ خواندن</label>
            <DateInputPersian v-model="form.read_date" placeholder="تاریخ خواندن" />
          </div>
          <div v-if="form.is_read">
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">امتیاز (۱ تا ۱۰)</label>
            <div class="flex items-center gap-3">
              <input v-model.number="form.rating" type="range" min="0" max="10" step="1" class="flex-1" />
              <span class="text-lg font-bold" :style="{ color: 'var(--accent)' }">{{ form.rating }}/10</span>
            </div>
            <div class="flex gap-1 mt-1 text-lg">
              <span v-for="i in 10" :key="i" class="cursor-pointer" @click="form.rating = i">{{ i <= form.rating ? '⭐' : '☆' }}</span>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">یادداشت</label>
            <textarea v-model="form.notes" rows="3" placeholder="نظرت درباره کتاب..." class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>
          <div class="flex items-center gap-2 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <input v-model="form.is_read" type="checkbox" class="w-5 h-5 rounded" />
            <label class="text-sm font-semibold" :style="{ color: form.is_read ? '#22c55e' : '#f59e0b' }">
              {{ form.is_read ? '✅ کتاب رو خوندم' : '📋 می‌خوام بخونم' }}
            </label>
          </div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="saveBook" class="flex-1 py-2.5 rounded-xl text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showForm = false" class="px-4 py-2.5 rounded-xl" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>