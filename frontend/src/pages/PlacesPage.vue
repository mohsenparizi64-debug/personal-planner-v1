<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, X, MapPin, Star, Calendar, Eye, EyeOff, ChevronDown, ChevronUp, Search, Heart } from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const places = ref([])
const categories = ref([])
const showForm = ref(false)
const editingPlace = ref(null)
const message = ref('')
const messageType = ref('success')
const showAll = ref(true)
const expandedPlaces = ref({})
const searchQuery = ref('')
const filterCategory = ref('')
const filterVisited = ref(null)
const filterFavorite = ref(false)

const form = ref({
  name: '', category: '', address: '', description: '',
  register_date: new Date().toISOString().split('T')[0],
  is_visited: false, visit_date: '', rating: 0, notes: '',
  latitude: null, longitude: null, is_favorite: false
})

const categoryLabels = {}
const categoryIcons = {}

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchPlaces = async () => {
  try { const res = await api.get('/places'); places.value = res.data } catch (e) {}
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/places/categories')
    categories.value = res.data
    res.data.forEach(c => { categoryLabels[c.value] = c.label; categoryIcons[c.value] = c.icon })
  } catch (e) {}
}

const filteredPlaces = computed(() => {
  let result = places.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p => p.name.toLowerCase().includes(q) || (p.address && p.address.toLowerCase().includes(q)))
  }
  if (filterCategory.value) result = result.filter(p => p.category === filterCategory.value)
  if (filterVisited.value === 'visited') result = result.filter(p => p.is_visited)
  if (filterVisited.value === 'unvisited') result = result.filter(p => !p.is_visited)
  if (filterFavorite.value) result = result.filter(p => p.is_favorite)
  return result
})

const resetFilters = () => { searchQuery.value = ''; filterCategory.value = ''; filterVisited.value = null; filterFavorite.value = false }

const openNewForm = () => {
  form.value = { name: '', category: '', address: '', description: '', register_date: new Date().toISOString().split('T')[0], is_visited: false, visit_date: '', rating: 0, notes: '', latitude: null, longitude: null, is_favorite: false }
  editingPlace.value = null; showForm.value = true
}

const openEditForm = (place) => {
  form.value = { ...place }
  editingPlace.value = place; showForm.value = true
}

const savePlace = async () => {
  if (!form.value.name.trim()) return
  try {
    const data = { ...form.value }
    if (!data.is_visited) { data.visit_date = null; data.rating = 0 }
    if (editingPlace.value) {
      await api.put(`/places/${editingPlace.value.id}`, data)
      showToast('✅ مکان بروزرسانی شد')
    } else {
      await api.post('/places', data)
      showToast('✅ مکان اضافه شد')
    }
    showForm.value = false; editingPlace.value = null; await fetchPlaces()
  } catch (e) { showToast('❌ خطا', 'error') }
}

const toggleVisited = async (place) => {
  try {
    const newStatus = !place.is_visited
    const today = new Date().toISOString().split('T')[0]
    
    const payload = {
      ...place,
      is_visited: newStatus,
      visit_date: newStatus ? today : place.visit_date
    }
    
    await api.put(`/places/${place.id}`, payload)
    await fetchPlaces()
    showToast(newStatus ? '📍 به مکان‌های رفته‌شده اضافه شد' : '🔄 به لیست رفتنی‌ها برگشت')
  } catch (e) {
    showToast('❌ خطا در بروزرسانی وضعیت', 'error')
  }
}

const toggleFavorite = async (place) => {
  await api.put(`/places/${place.id}`, { is_favorite: !place.is_favorite })
  await fetchPlaces()
}

const deletePlace = async (id) => {
  if (!confirm('مطمئنی؟')) return
  try { await api.delete(`/places/${id}`); showToast('🗑️ حذف شد'); await fetchPlaces() } catch (e) {}
}

const toggleExpand = (id) => { expandedPlaces.value[id] = !expandedPlaces.value[id] }

const starRating = (rating) => '⭐'.repeat(rating) + (rating === 0 ? '' : ` (${rating}/5)`)

onMounted(() => { fetchPlaces(); fetchCategories() })
</script>

<template>
  <!-- دیو مادر اصلی به همراه پس‌زمینه شفاف ۴K قطب‌نما و نقشه جهان -->
  <div class="relative min-h-screen text-right p-6 md:p-10 overflow-hidden" dir="rtl">
    
    <!-- پس‌زمینه ثابت و شفاف (بدون تاری) -->
    <div class="fixed inset-0 z-0 bg-cover bg-center"
         style="background-image: url('https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=2560&q=90');">
      <div class="absolute inset-0 bg-black/45"></div>
    </div>

    <!-- محتوای اصلی رو لایه‌ی شیشه‌ای -->
    <div class="relative z-10 max-w-6xl mx-auto space-y-6 text-white">

      <!-- Toast Message -->
      <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl font-semibold transition-all duration-300"
           :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

      <!-- هدر صفحه -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-3xl bg-black/40 backdrop-blur-md border border-white/10 shadow-2xl">
        <div>
          <h1 class="text-3xl font-black mb-1 drop-shadow-md" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''">مکان‌ها و مقصدهای دیدنی</h1>
          <p class="opacity-70 text-xs">{{ filteredPlaces.length }} مکان ثبت شده</p>
        </div>
        <div class="flex gap-2 flex-wrap">
          <button @click="filterFavorite = !filterFavorite" class="px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-xs font-bold shadow-md"
                  :style="filterFavorite ? { background: '#ef4444', color: '#fff' } : { background: 'rgba(255,255,255,0.1)', color: '#fff' }">
            <Heart class="w-4 h-4" :fill="filterFavorite ? '#fff' : 'none'" /> علاقه‌مندی‌ها
          </button>
          <button @click="showAll = !showAll" class="px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-xs font-bold shadow-md bg-white/10 hover:bg-white/20">
            <Eye v-if="showAll" class="w-4 h-4" /> <EyeOff v-else class="w-4 h-4" />
            {{ showAll ? 'مخفی کردن' : 'نمایش همه' }}
          </button>
          <button @click="openNewForm" class="px-5 py-2.5 rounded-2xl text-white font-bold transition flex items-center gap-2 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
            <Plus class="w-5 h-5" /> مکان جدید
          </button>
        </div>
      </div>

      <!-- نوار فیلتر و جستجو -->
      <div class="p-5 rounded-3xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl space-y-3">
        <div class="relative">
          <Search class="absolute right-3 top-3 w-5 h-5 opacity-40" />
          <input v-model="searchQuery" placeholder="جستجوی مکان یا آدرس..." class="w-full pr-10 pl-4 py-2.5 rounded-xl text-sm bg-black/40 border border-white/10 outline-none placeholder-white/40" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <select v-model="filterCategory" class="px-3 py-2.5 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option value="">همه دسته‌بندی‌ها</option>
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.icon }} {{ c.label }}</option>
          </select>
          <select v-model="filterVisited" class="px-3 py-2.5 rounded-xl border border-white/10 bg-black/50 text-xs outline-none">
            <option :value="null">همه</option>
            <option value="visited">رفته‌ام 📍</option>
            <option value="unvisited">می‌خوام برم 📋</option>
          </select>
          <button @click="resetFilters" class="px-3 py-2.5 rounded-xl text-xs font-bold transition bg-white/10 hover:bg-white/20">حذف فیلترها</button>
        </div>
      </div>

      <!-- وضعیت خالی -->
      <div v-if="filteredPlaces.length === 0" class="text-center py-20 opacity-40">
        <MapPin class="w-16 h-16 mx-auto mb-4" />
        <p class="text-xl font-bold mb-2">هنوز مکانی ثبت نکردی!</p>
      </div>

      <!-- لیست مکان‌ها -->
      <div v-if="showAll" class="space-y-3">
        <div v-for="place in filteredPlaces" :key="place.id"
             class="rounded-3xl border overflow-hidden transition-all duration-200 bg-black/40 backdrop-blur-xl shadow-2xl"
             :style="{ borderColor: place.is_favorite ? 'rgba(239,68,68,0.5)' : 'rgba(255,255,255,0.1)', opacity: place.is_visited ? 0.8 : 1 }">
          
          <div class="flex items-center gap-3 p-4 cursor-pointer hover:bg-white/[0.02]" @click="toggleExpand(place.id)">
            <div class="text-2xl p-2 rounded-2xl bg-white/5 border border-white/10">{{ categoryIcons[place.category] || '📍' }}</div>
            <div class="flex-1 min-w-0">
              <h3 class="font-bold flex items-center gap-2" :class="place.is_visited ? 'line-through opacity-60' : ''">
                {{ place.name }}
                <Heart v-if="place.is_favorite" class="w-4 h-4 text-red-500" fill="#ef4444" />
              </h3>
              <div class="flex gap-2 text-xs mt-0.5 opacity-70">
                <span v-if="place.category" class="px-2 py-0.5 rounded bg-white/10 font-bold">{{ categoryLabels[place.category] || place.category }}</span>
                <span v-if="place.rating" class="text-yellow-400 font-bold">{{ starRating(place.rating) }}</span>
                <span v-if="place.address" class="truncate max-w-[200px]">{{ place.address }}</span>
              </div>
            </div>
            <div class="flex gap-1 flex-shrink-0" @click.stop>
              <button @click="toggleFavorite(place)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: place.is_favorite ? '#ef4444' : 'rgba(255,255,255,0.6)' }">
                <Heart class="w-4 h-4" :fill="place.is_favorite ? '#ef4444' : 'none'" />
              </button>
              <button @click="toggleVisited(place)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: place.is_visited ? '#22c55e' : 'rgba(255,255,255,0.6)' }">
                <Eye v-if="!place.is_visited" class="w-4 h-4" /><EyeOff v-else class="w-4 h-4" />
              </button>
              <button @click="openEditForm(place)" class="p-1.5 rounded-lg hover:bg-white/10 opacity-70 hover:opacity-100"><Edit3 class="w-4 h-4" /></button>
              <button @click="deletePlace(place.id)" class="p-1.5 rounded-lg hover:bg-red-500/20 text-red-400"><Trash2 class="w-4 h-4" /></button>
              <button class="p-1.5 opacity-50">
                <ChevronDown v-if="!expandedPlaces[place.id]" class="w-4 h-4" /><ChevronUp v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div v-if="expandedPlaces[place.id]" class="px-6 pb-6 pt-4 border-t border-white/10 bg-black/20 text-xs">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs opacity-90">
              <div><span class="opacity-50 font-bold block mb-1">آدرس:</span> <span>{{ place.address || '-' }}</span></div>
              <div><span class="opacity-50 font-bold block mb-1">دسته‌بندی:</span> <span>{{ categoryLabels[place.category] || '-' }}</span></div>
              <div><span class="opacity-50 font-bold block mb-1">تاریخ ثبت:</span> <span>{{ formatDate(place.register_date) || '-' }}</span></div>
              <div><span class="opacity-50 font-bold block mb-1">تاریخ بازدید:</span> <span>{{ formatDate(place.visit_date) || '-' }}</span></div>
              <div><span class="opacity-50 font-bold block mb-1">امتیاز:</span> <span class="text-yellow-400 font-bold">{{ place.rating ? place.rating + ' / 5' : '-' }}</span></div>
              <div v-if="place.latitude"><span class="opacity-50 font-bold block mb-1">موقعیت:</span> <span dir="ltr" class="font-mono">{{ place.latitude }}, {{ place.longitude }}</span></div>
            </div>
            <div v-if="place.description" class="mt-3 p-3 rounded-2xl bg-white/5 border border-white/10">
              <p class="text-[10px] opacity-50 mb-1 font-bold">توضیحات:</p>
              <p class="text-xs leading-relaxed opacity-90">{{ place.description }}</p>
            </div>
            <div v-if="place.notes" class="mt-2 p-3 rounded-2xl bg-white/5 border border-white/10">
              <p class="text-[10px] opacity-50 mb-1 font-bold">یادداشت:</p>
              <p class="text-xs leading-relaxed opacity-90">{{ place.notes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== مودال افزودن/ویرایش مکان ========== -->
      <div v-if="showForm" class="fixed inset-0 z-[100] flex items-start justify-center p-4 pt-20 pb-20 bg-black/80 backdrop-blur-md overflow-y-auto" @click.self="showForm = false">
        <div class="w-full max-w-md rounded-3xl p-8 bg-gray-900 border border-white/10 shadow-2xl text-white space-y-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold">{{ editingPlace ? 'ویرایش مکان' : 'مکان جدید' }}</h3>
            <button @click="showForm = false" class="p-1 hover:bg-white/10 rounded-full"><X class="w-5 h-5" /></button>
          </div>
          <div class="space-y-3 text-right" dir="rtl">
            <div>
              <label class="block text-sm mb-1 opacity-70">نام مکان *</label>
              <input v-model="form.name" placeholder="نام مکان" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70">دسته‌بندی</label>
              <select v-model="form.category" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-xs">
                <option value="">انتخاب کنید...</option>
                <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.icon }} {{ c.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70">آدرس</label>
              <input v-model="form.address" placeholder="آدرس" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70">توضیحات</label>
              <textarea v-model="form.description" rows="2" placeholder="توضیحات..." class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm"></textarea>
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70">تاریخ ثبت</label>
              <DateInputPersian v-model="form.register_date" placeholder="تاریخ ثبت" />
            </div>
            <div class="flex items-center gap-2 p-3 rounded-2xl bg-white/5 border border-white/10">
              <input v-model="form.is_visited" type="checkbox" class="w-5 h-5 rounded-md" />
              <label class="text-sm font-semibold cursor-pointer" :style="{ color: form.is_visited ? '#22c55e' : '#f59e0b' }">
                {{ form.is_visited ? '✅ اینجا رفتم' : '📋 می‌خوام برم' }}
              </label>
            </div>
            <div v-if="form.is_visited">
              <label class="block text-sm mb-1 opacity-70">تاریخ بازدید</label>
              <DateInputPersian v-model="form.visit_date" placeholder="تاریخ بازدید" />
            </div>
            <div v-if="form.is_visited">
              <label class="block text-sm mb-1 opacity-70">امتیاز (۱ تا ۵)</label>
              <div class="flex gap-1 text-2xl text-yellow-400">
                <span v-for="i in 5" :key="i" class="cursor-pointer hover:scale-125 transition" @click="form.rating = i">{{ i <= form.rating ? '⭐' : '☆' }}</span>
              </div>
            </div>
            <div>
              <label class="block text-sm mb-1 opacity-70">یادداشت</label>
              <textarea v-model="form.notes" rows="2" placeholder="یادداشت شخصی..." class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs mb-1 opacity-70">Lat</label>
                <input v-model.number="form.latitude" type="number" step="any" placeholder="عرض جغرافیایی" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-xs text-left" dir="ltr" />
              </div>
              <div>
                <label class="block text-xs mb-1 opacity-70">Lng</label>
                <input v-model.number="form.longitude" type="number" step="any" placeholder="طول جغرافیایی" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-xs text-left" dir="ltr" />
              </div>
            </div>
            <div class="flex items-center gap-2 pt-1">
              <input v-model="form.is_favorite" type="checkbox" class="w-5 h-5 rounded-md" />
              <label class="text-xs opacity-80 cursor-pointer">❤️ علاقه‌مندی</label>
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button @click="savePlace" class="flex-1 py-2.5 rounded-2xl text-white font-semibold shadow-lg" :style="{ background: 'var(--accent)' }">ذخیره</button>
            <button @click="showForm = false" class="px-4 py-2.5 rounded-2xl bg-white/10 hover:bg-white/20">انصراف</button>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>