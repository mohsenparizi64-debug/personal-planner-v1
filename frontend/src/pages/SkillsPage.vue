<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { Award, Plus, BookOpen, CheckCircle2, Clock, Sparkles, Tag, ExternalLink, Target } from 'lucide-vue-next'

const skills = ref([])
const learningLogs = ref([])
const goals = ref([])
const loading = ref(false)

const showSkillModal = ref(false)
const showLogModal = ref(false)

const skillForm = ref({
  title: '',
  category: 'برنامه‌نویسی',
  status: 'in_progress',
  progress_percent: 10,
  goal_id: null,
  notes: ''
})

const logForm = ref({
  skill_id: null,
  title: '',
  content: '',
  log_date: new Date().toISOString().split('T')[0],
  resource_url: '',
  tags: ''
})

// بارگذاری داده‌ها با مسیرهای صحیح
const fetchData = async () => {
  loading.value = true
  try {
    const [skRes, lgRes, goRes] = await Promise.all([
      api.get('/skills/'),
      api.get('/skills/logs'),
      api.get('/goals/')
    ])
    skills.value = skRes.data
    learningLogs.value = lgRes.data
    goals.value = goRes.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const saveSkill = async () => {
  try {
    await api.post('/skills/', skillForm.value)
    showSkillModal.value = false
    skillForm.value.title = ''
    fetchData()
  } catch (e) {
    console.error(e)
  }
}

const saveLog = async () => {
  try {
    await api.post('/skills/logs', logForm.value)
    showLogModal.value = false
    logForm.value.title = ''
    logForm.value.content = ''
    fetchData()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    
    <!-- هدر بخش بانک مهارت‌ها -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 rounded-3xl border border-white/10">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-lg shadow-amber-500/20">
          <Award class="w-8 h-8 text-white" />
        </div>
        <div>
          <h2 class="text-2xl font-black text-white">بانک مهارت‌ها و دفترچه آموزه‌ها</h2>
          <p class="text-xs text-gray-400 mt-1">مدیریت درخت دانش، درصد تسلط و ثبت روزنوشت یادگیری‌ها</p>
        </div>
      </div>

      <div class="flex gap-3">
        <button 
          @click="showSkillModal = true"
          class="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white text-xs font-black rounded-xl shadow-lg flex items-center gap-2 transition"
        >
          <Plus class="w-4 h-4" /> افزودن مهارت جدید
        </button>

        <button 
          @click="showLogModal = true"
          class="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white text-xs font-bold rounded-xl flex items-center gap-2 transition border border-white/10"
        >
          <BookOpen class="w-4 h-4 text-amber-400" /> ثبت نکته آموزه
        </button>
      </div>
    </div>

    <!-- شبکه‌بندی کارت‌های مهارت -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="skill in skills" 
        :key="skill.id"
        class="glass-card p-6 rounded-3xl border border-white/10 space-y-4 hover:border-amber-500/50 transition duration-300"
      >
        <div class="flex justify-between items-start">
          <div>
            <span class="text-[10px] px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-300 font-bold border border-amber-500/20">
              {{ skill.category || 'عمومی' }}
            </span>
            <h3 class="font-black text-white text-lg mt-2">{{ skill.title }}</h3>
          </div>

          <span 
            class="text-xs px-2.5 py-1 rounded-full font-bold"
            :class="skill.status === 'mastered' ? 'bg-green-500/20 text-green-300' : 'bg-blue-500/20 text-blue-300'"
          >
            {{ skill.status === 'mastered' ? 'تسلط کامل' : 'در حال یادگیری' }}
          </span>
        </div>

        <!-- درصد پیشرفت -->
        <div class="space-y-1.5">
          <div class="flex justify-between text-xs text-gray-400 font-bold">
            <span>درصد تسلط:</span>
            <span>{{ skill.progress_percent }}٪</span>
          </div>
          <div class="w-full h-2.5 bg-white/10 rounded-full overflow-hidden p-0.5">
            <div 
              class="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-500 shadow-md"
              :style="{ width: skill.progress_percent + '%' }"
            ></div>
          </div>
        </div>

        <p class="text-xs text-gray-400 line-clamp-2" v-if="skill.notes">{{ skill.notes }}</p>
      </div>
    </div>

    <!-- دفترچه آموزه‌ها و نکات روزانه -->
    <div class="glass-card p-6 rounded-3xl border border-white/10 space-y-4">
      <h3 class="text-lg font-bold text-white flex items-center gap-2">
        <BookOpen class="w-5 h-5 text-amber-400" />
        دفترچه آموزه‌ها (امروز چه چیز جدیدی یاد گرفتم؟)
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="log in learningLogs" 
          :key="log.id"
          class="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2"
        >
          <div class="flex justify-between items-center">
            <h4 class="font-bold text-white text-sm">{{ log.title }}</h4>
            <span class="text-xs text-gray-400">{{ log.log_date }}</span>
          </div>

          <p class="text-xs text-gray-300 leading-relaxed">{{ log.content }}</p>

          <div class="flex items-center justify-between pt-2 text-[11px] text-gray-400 border-t border-white/5">
            <span v-if="log.tags" class="flex items-center gap-1 text-amber-300"><Tag class="w-3 h-3" /> {{ log.tags }}</span>
            <a v-if="log.resource_url" :href="log.resource_url" target="_blank" class="text-blue-400 hover:underline flex items-center gap-1">
              منبع <ExternalLink class="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- مودال افزودن مهارت (تله‌پورت به بدنه) -->
    <Teleport to="body">
      <div v-if="showSkillModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="w-full max-w-md glass-card p-6 rounded-3xl border border-white/20 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto custom-scrollbar">
          <h3 class="text-lg font-bold text-white">افزودن مهارت جدید</h3>

          <form @submit.prevent="saveSkill" class="space-y-4 text-right">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">عنوان مهارت</label>
              <input v-model="skillForm.title" type="text" required class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">دسته‌بندی</label>
              <input v-model="skillForm.category" type="text" class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">درصد تسلط (۰ تا ۱۰۰)</label>
              <input v-model="skillForm.progress_percent" type="number" min="0" max="100" class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">اتصال به هدف کلان (اختیاری)</label>
              <select v-model="skillForm.goal_id" class="w-full px-3 py-2 bg-slate-900 border border-white/20 rounded-xl text-white text-xs outline-none">
                <option :value="null">بدون اتصال</option>
                <option v-for="g in goals" :key="g.id" :value="g.id">{{ g.title }}</option>
              </select>
            </div>

            <div class="flex gap-3 pt-2">
              <button type="submit" class="flex-1 py-3 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl shadow-lg">ذخیره مهارت</button>
              <button type="button" @click="showSkillModal = false" class="flex-1 py-3 bg-white/10 hover:bg-white/20 text-gray-300 font-bold text-xs rounded-xl">انصراف</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- مودال ثبت نکته آموزه (تله‌پورت به بدنه) -->
    <Teleport to="body">
      <div v-if="showLogModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="w-full max-w-md glass-card p-6 rounded-3xl border border-white/20 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto custom-scrollbar">
          <h3 class="text-lg font-bold text-white">ثبت نکته / آموزه جدید</h3>

          <form @submit.prevent="saveLog" class="space-y-4 text-right">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">عنوان موضوع یا نکته</label>
              <input v-model="logForm.title" type="text" required class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none" />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">توضیحات و خلاصه آموخته</label>
              <textarea v-model="logForm.content" rows="4" class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none"></textarea>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-400 mb-1">لینک منبع (اختیاری)</label>
              <input v-model="logForm.resource_url" type="url" placeholder="https://..." class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs outline-none dir-ltr" />
            </div>

            <div class="flex gap-3 pt-2">
              <button type="submit" class="flex-1 py-3 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl shadow-lg">ذخیره نکته</button>
              <button type="button" @click="showLogModal = false" class="flex-1 py-3 bg-white/10 hover:bg-white/20 text-gray-300 font-bold text-xs rounded-xl">انصراف</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>