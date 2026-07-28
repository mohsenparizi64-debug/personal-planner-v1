<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, X, MapPin, Star, Calendar, Eye, EyeOff, ChevronDown, ChevronUp, Search, Heart } from 'lucide-vue-next'
import api from '@/services/api'

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
  await api.put(`/places/${place.id}`, { is_visited: !place.is_visited, visit_date: !place.is_visited ? new Date().toISOString().split('T')[0] : place.visit_date })
  await fetchPlaces()
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
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen">
    
    <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">{{ message }}</div>

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-extrabold mb-1" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">مکان‌ها</h1>
        <p :style="{ color: 'var(--text-secondary)' }">{{ filteredPlaces.length }} مکان</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button @click="filterFavorite = !filterFavorite" class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm"
                :style="filterFavorite ? { background: '#ef4444', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <Heart class="w-4 h-4" :fill="filterFavorite ? '#fff' : 'none'" /> علاقه‌مندی‌ها
        </button>
        <button @click="showAll = !showAll" class="px-4 py-2 rounded-xl transition flex items-center gap-2 text-sm"
                :style="showAll ? { background: 'var(--accent)', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
          <Eye v-if="showAll" class="w-4 h-4" /> <EyeOff v-else class="w-4 h-4" />
          {{ showAll ? 'مخفی کردن' : 'نمایش همه' }}
        </button>
        <button @click="openNewForm" class="px-5 py-2 rounded-xl text-white font-semibold transition flex items-center gap-2" :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> مکان جدید
        </button>
      </div>
    </div>

    <div class="mb-6 p-4 rounded-xl space-y-3" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
      <div class="relative">
        <Search class="absolute right-3 top-2.5 w-5 h-5" :style="{ color: 'var(--text-secondary)' }" />
        <input v-model="searchQuery" placeholder="جستجوی مکان یا آدرس..." class="w-full pr-10 pl-4 py-2.5 rounded-lg text-sm"
               :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
      </div>
      <div class="grid grid-cols-3 gap-2">
        <select v-model="filterCategory" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option value="">همه دسته‌بندی‌ها</option>
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.icon }} {{ c.label }}</option>
        </select>
        <select v-model="filterVisited" class="px-3 py-2 rounded-lg text-sm" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
          <option :value="null">همه</option>
          <option value="visited">رفته‌ام</option>
          <option value="unvisited">می‌خوام برم</option>
        </select>
        <button @click="resetFilters" class="px-3 py-2 rounded-lg text-sm transition" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">حذف فیلترها</button>
      </div>
    </div>

    <div v-if="filteredPlaces.length === 0" class="text-center py-20">
      <MapPin class="w-16 h-16 mx-auto mb-4" :style="{ color: 'var(--accent)' }" />
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">هنوز مکانی ثبت نکردی!</p>
    </div>

    <div v-if="showAll" class="space-y-3">
      <div v-for="place in filteredPlaces" :key="place.id"
           class="rounded-xl overflow-hidden transition-all duration-200 border"
           :style="{ background: 'var(--bg-card)', borderColor: place.is_favorite ? 'rgba(239,68,68,0.3)' : 'var(--border)', opacity: place.is_visited ? 0.7 : 1 }">
        
        <div class="flex items-center gap-3 p-4 cursor-pointer" @click="toggleExpand(place.id)">
          <div class="text-2xl">{{ categoryIcons[place.category] || '📍' }}</div>
          <div class="flex-1 min-w-0">
            <h3 class="font-bold flex items-center gap-2" :style="{ color: 'var(--text-primary)', textDecoration: place.is_visited ? 'line-through' : 'none' }">
              {{ place.name }}
              <Heart v-if="place.is_favorite" class="w-4 h-4 text-red-500" fill="#ef4444" />
            </h3>
            <div class="flex gap-2 text-xs mt-0.5" :style="{ color: 'var(--text-secondary)' }">
              <span v-if="place.category">{{ categoryLabels[place.category] || place.category }}</span>
              <span v-if="place.rating">{{ starRating(place.rating) }}</span>
              <span v-if="place.address" class="truncate max-w-[200px]">{{ place.address }}</span>
            </div>
          </div>
          <div class="flex gap-1 flex-shrink-0" @click.stop>
            <button @click="toggleFavorite(place)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: place.is_favorite ? '#ef4444' : 'var(--text-secondary)' }">
              <Heart class="w-4 h-4" :fill="place.is_favorite ? '#ef4444' : 'none'" />
            </button>
            <button @click="toggleVisited(place)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: place.is_visited ? '#22c55e' : 'var(--text-secondary)' }">
              <Eye v-if="!place.is_visited" class="w-4 h-4" /><EyeOff v-else class="w-4 h-4" />
            </button>
            <button @click="openEditForm(place)" class="p-1.5 rounded-lg hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-4 h-4" /></button>
            <button @click="deletePlace(place.id)" class="p-1.5 rounded-lg hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-4 h-4" /></button>
            <button class="p-1.5" :style="{ color: 'var(--text-secondary)' }">
              <ChevronDown v-if="!expandedPlaces[place.id]" class="w-4 h-4" /><ChevronUp v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div v-if="expandedPlaces[place.id]" class="px-4 pb-4 border-t" :style="{ borderColor: 'var(--border)' }">
          <div class="grid grid-cols-2 gap-3 mt-3 text-sm">
            <div><span :style="{ color: 'var(--text-secondary)' }">آدرس:</span> <span :style="{ color: 'var(--text-primary)' }">{{ place.address || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">دسته‌بندی:</span> <span :style="{ color: 'var(--text-primary)' }">{{ categoryLabels[place.category] || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت:</span> <span :style="{ color: 'var(--text-primary)' }">{{ place.register_date || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">تاریخ بازدید:</span> <span :style="{ color: 'var(--text-primary)' }">{{ place.visit_date || '-' }}</span></div>
            <div><span :style="{ color: 'var(--text-secondary)' }">امتیاز:</span> <span :style="{ color: 'var(--accent)' }">{{ place.rating || '-' }}/5</span></div>
            <div v-if="place.latitude"><span :style="{ color: 'var(--text-secondary)' }">موقعیت:</span> <span :style="{ color: 'var(--text-primary)' }">{{ place.latitude }}, {{ place.longitude }}</span></div>
          </div>
          <div v-if="place.description" class="mt-3 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <p class="text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">توضیحات:</p>
            <p class="text-sm" :style="{ color: 'var(--text-primary)' }">{{ place.description }}</p>
          </div>
          <div v-if="place.notes" class="mt-2 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <p class="text-xs mb-1" :style="{ color: 'var(--text-secondary)' }">یادداشت:</p>
            <p class="text-sm" :style="{ color: 'var(--text-primary)' }">{{ place.notes }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== مودال ========== -->
    <div v-if="showForm" class="fixed inset-0 z-[100] flex items-start justify-center p-4 pt-20 pb-20 bg-black/60 backdrop-blur-sm overflow-y-auto" @click.self="showForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingPlace ? 'ویرایش مکان' : 'مکان جدید' }}</h3>
          <button @click="showForm = false" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">نام مکان *</label>
            <input v-model="form.name" placeholder="نام مکان" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">دسته‌بندی</label>
            <select v-model="form.category" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }">
              <option value="">انتخاب کنید...</option>
              <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.icon }} {{ c.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">آدرس</label>
            <input v-model="form.address" placeholder="آدرس" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">توضیحات</label>
            <textarea v-model="form.description" rows="2" placeholder="توضیحات..." class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ ثبت</label>
            <input v-model="form.register_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div class="flex items-center gap-2 p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
            <input v-model="form.is_visited" type="checkbox" class="w-5 h-5 rounded" />
            <label class="text-sm font-semibold" :style="{ color: form.is_visited ? '#22c55e' : '#f59e0b' }">
              {{ form.is_visited ? '✅ اینجا رفتم' : '📋 می‌خوام برم' }}
            </label>
          </div>
          <div v-if="form.is_visited">
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">تاریخ بازدید</label>
            <input v-model="form.visit_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div v-if="form.is_visited">
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">امتیاز (۱ تا ۵)</label>
            <div class="flex gap-1 text-2xl">
              <span v-for="i in 5" :key="i" class="cursor-pointer" @click="form.rating = i">{{ i <= form.rating ? '⭐' : '☆' }}</span>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">یادداشت</label>
            <textarea v-model="form.notes" rows="2" placeholder="یادداشت شخصی..." class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">Lat</label>
              <input v-model.number="form.latitude" type="number" step="any" placeholder="عرض جغرافیایی" class="w-full px-3 py-2.5 rounded-lg text-left" dir="ltr" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
            <div>
              <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">Lng</label>
              <input v-model.number="form.longitude" type="number" step="any" placeholder="طول جغرافیایی" class="w-full px-3 py-2.5 rounded-lg text-left" dir="ltr" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="form.is_favorite" type="checkbox" class="w-5 h-5 rounded" />
            <label class="text-sm" :style="{ color: 'var(--text-primary)' }">❤️ علاقه‌مندی</label>
          </div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="savePlace" class="flex-1 py-2.5 rounded-xl text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showForm = false" class="px-4 py-2.5 rounded-xl" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>