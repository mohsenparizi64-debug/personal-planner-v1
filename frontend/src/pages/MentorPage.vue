<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import { 
  Sparkles, Bot, TrendingUp, AlertTriangle, Lightbulb, Target, 
  Send, RefreshCw, MessageSquare, CheckCircle2, ShieldAlert, Zap, ArrowRight, Clock, HelpCircle
} from 'lucide-vue-next'

const themeStore = useThemeStore()
const isLoading = ref(true)
const isChatLoading = ref(false)
const reportData = ref(null)
const selectedTimeFrame = ref('last_1_week') // last_3_days, last_1_week, last_2_weeks, last_1_month
const chatMessage = ref('')

const timeFrames = [
  { id: 'last_3_days', label: '۳ روز گذشته' },
  { id: 'last_1_week', label: '۱ هفته گذشته' },
  { id: 'last_2_weeks', label: '۲ هفته گذشته' },
  { id: 'last_1_month', label: '۱ ماه گذشته' },
]

const chatHistory = ref([
  {
    sender: 'ai',
    text: 'سلام! من منتور استراتژیک و کارشناس تخصصی شما هستم. تمام داده‌های اهداف، تسک‌ها و عملکرد زمانی‌تان را تحلیل کرده‌ام. چطور می‌توانم راهنمایی‌تان کنم؟'
  }
])

const fetchReport = async () => {
  try {
    isLoading.value = true
    const response = await api.get(`/mentor/report?time_frame=${selectedTimeFrame.value}`)
    reportData.value = response.data
  } catch (error) {
    console.error('خطا در دریافت گزارش منتور:', error)
  } finally {
    isLoading.value = false
  }
}

const sendChatMessage = async (prefilledMsg = null) => {
  const msgToSend = prefilledMsg || chatMessage.value.trim()
  if (!msgToSend) return

  chatHistory.value.push({ sender: 'user', text: msgToSend })
  if (!prefilledMsg) chatMessage.value = ''
  isChatLoading.value = true

  try {
    const response = await api.post('/mentor/chat', { message: msgToSend })
    chatHistory.value.push({ sender: 'ai', text: response.data.reply })
  } catch (error) {
    chatHistory.value.push({ sender: 'ai', text: '❌ خطا در برقراری ارتباط با منتور هوشمند.' })
  } finally {
    isChatLoading.value = false
  }
}

onMounted(() => {
  fetchReport()
})
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
    
    <!-- هدر اصلی منتور هوشمند -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 rounded-3xl border border-white/10 shadow-2xl">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 shadow-xl shadow-purple-500/30 text-white border border-white/20">
          <Sparkles class="w-8 h-8 animate-pulse" />
        </div>
        <div>
          <h1 class="text-2xl md:text-3xl font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            منتور استراتژیک و کارشناس تخصصی (AI Mentor)
          </h1>
          <p class="text-xs md:text-sm mt-1" :style="{ color: 'var(--text-secondary)' }">تحلیل زنده معماری اهداف، کشف نقاط کور و ارائه توصیه‌های تخصصی</p>
        </div>
      </div>

      <!-- انتخاب بازه زمانی ارزیابی عملکرد -->
      <div class="flex items-center gap-2 bg-white/5 p-1.5 rounded-2xl border border-white/10">
        <Clock class="w-4 h-4 text-purple-400 ml-1 mr-2" />
        <button 
          v-for="tf in timeFrames" 
          :key="tf.id"
          @click="selectedTimeFrame = tf.id; fetchReport()"
          class="px-3 py-1.5 rounded-xl text-xs font-black transition"
          :class="selectedTimeFrame === tf.id ? 'bg-purple-600 text-white shadow' : 'text-gray-400 hover:text-white'"
        >
          {{ tf.label }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-20" :style="{ color: 'var(--text-secondary)' }">
      <Sparkles class="w-12 h-12 animate-spin mx-auto mb-3 text-purple-400" />
      <p class="font-bold text-sm">در حال آنالیز معماری اهداف و عملکرد بازه {{ timeFrames.find(t=>t.id===selectedTimeFrame)?.label }} توسط منتور...</p>
    </div>

    <div v-else-if="reportData" class="space-y-8">

      <!-- 🚨 کادر ویژه: هشدارهای اهداف کمتر مورد توجه قرار گرفته (Neglected Goals Warning) -->
      <div v-if="reportData.neglected_goals && reportData.neglected_goals.length > 0" class="glass-card p-6 rounded-3xl border border-red-500/40 bg-red-500/10 shadow-xl">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-black text-red-400 flex items-center gap-2">
            <AlertTriangle class="w-6 h-6 animate-pulse" /> اخطار منتور: اهداف کم‌توجه و رهاشده در بازه {{ reportData.time_frame_label }}
          </h3>
          <span class="px-3 py-1 rounded-full bg-red-500/20 text-red-300 font-black text-xs border border-red-500/30">
            {{ reportData.neglected_goals.length }} هدف رهاشده
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div v-for="ng in reportData.neglected_goals" :key="ng.id" class="p-3.5 rounded-2xl bg-black/20 border border-red-500/20 text-xs text-white">
            <p class="font-black text-sm text-red-300 mb-1">🎯 {{ ng.title }} (اولویت: {{ ng.priority }})</p>
            <p class="text-gray-300">📌 گام بعدی: {{ ng.next_step }}</p>
          </div>
        </div>
      </div>

      <!-- کارت‌های آمار سلامتی -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6">
        
        <div class="glass-card p-5 rounded-3xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">سلامت کلی برنامه</p>
            <p class="text-xl font-black text-emerald-400">{{ reportData.health_status }}</p>
          </div>
          <div class="w-12 h-12 bg-emerald-500/20 text-emerald-400 rounded-2xl flex items-center justify-center border border-emerald-500/30">
            <CheckCircle2 class="w-6 h-6" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">اقدامات بازه {{ reportData.time_frame_label }}</p>
            <p class="text-2xl font-black text-blue-400">{{ reportData.context_summary.acted_tasks_in_timeframe_count }} تسک</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/20 text-blue-400 rounded-2xl flex items-center justify-center border border-blue-500/30">
            <TrendingUp class="w-6 h-6" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-2xl border border-red-500/30 bg-red-500/5 flex items-center justify-between">
          <div>
            <p class="text-xs text-red-400 font-bold mb-1">کارهای عقب‌افتاده</p>
            <p class="text-2xl font-black text-red-400">{{ reportData.context_summary.overdue_tasks_count }} مورد</p>
          </div>
          <div class="w-12 h-12 bg-red-500/20 text-red-400 rounded-2xl flex items-center justify-center border border-red-500/30">
            <AlertTriangle class="w-6 h-6 animate-pulse" />
          </div>
        </div>

        <div class="glass-card p-5 rounded-2xl border border-white/10 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold mb-1" :style="{ color: 'var(--text-secondary)' }">بانک ایده‌ها</p>
            <p class="text-2xl font-black text-amber-400">{{ reportData.context_summary.total_ideas_count }} ایده</p>
          </div>
          <div class="w-12 h-12 bg-amber-500/20 text-amber-400 rounded-2xl flex items-center justify-center border border-amber-500/30">
            <Lightbulb class="w-6 h-6" />
          </div>
        </div>

      </div>

      <!-- 📊 گزارش تشخیصی و مرتب هوش مصنوعی با فونت درشت -->
      <div class="glass-card p-6 md:p-8 rounded-3xl border border-white/10 space-y-6">
        <div class="flex items-center justify-between border-b border-white/10 pb-4">
          <h3 class="text-xl font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            <Bot class="w-7 h-7 text-purple-400" /> گزارش تشخیصی منتور و کارشناس تخصصی (بازه {{ reportData.time_frame_label }})
          </h3>
        </div>

        <!-- متن گزارش مرتب، شکیل و با فونت درشت -->
        <div class="space-y-4 text-base md:text-lg font-bold leading-loose whitespace-pre-line text-justify p-4 rounded-2xl bg-white/5 border border-white/10" :style="{ color: 'var(--text-primary)' }">
          {{ reportData.insights[0] }}
        </div>
      </div>

      <!-- 💬 چت‌بات تعاملی با منتور -->
      <div class="glass-card p-6 rounded-3xl border border-white/10 space-y-6">
        <div class="flex items-center justify-between pb-4 border-b border-white/10">
          <h3 class="text-xl font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            <MessageSquare class="w-6 h-6 text-purple-400" /> گفتگوی تعاملی با منتور اختصاصی
          </h3>
          <span class="text-xs text-emerald-400 font-bold flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-ping"></span> متصل به دیتابیس زنده
          </span>
        </div>

        <div class="h-80 overflow-y-auto space-y-4 p-4 rounded-2xl bg-black/10 border border-white/5 custom-scrollbar">
          <div 
            v-for="(msg, idx) in chatHistory" 
            :key="idx" 
            class="flex items-start gap-3 max-w-2xl"
            :class="msg.sender === 'user' ? 'mr-auto flex-row-reverse' : 'ml-auto'"
          >
            <div class="w-8 h-8 rounded-xl flex items-center justify-center text-white text-xs font-bold flex-shrink-0" :class="msg.sender === 'user' ? 'bg-blue-600' : 'bg-purple-600'">
              {{ msg.sender === 'user' ? 'شما' : 'AI' }}
            </div>
            <div class="p-4 rounded-2xl text-sm md:text-base leading-relaxed whitespace-pre-line border shadow-md" :class="msg.sender === 'user' ? 'bg-blue-600/20 border-blue-500/30 text-white' : 'bg-white/10 border-white/10 text-white'">
              {{ msg.text }}
            </div>
          </div>

          <div v-if="isChatLoading" class="flex items-center gap-2 text-xs text-purple-400 font-bold p-2">
            <Sparkles class="w-4 h-4 animate-spin" /> منتور در حال تحلیل پاسخ...
          </div>
        </div>

        <form @submit.prevent="sendChatMessage()" class="flex items-center gap-3">
          <input 
            v-model="chatMessage" 
            type="text" 
            placeholder="سوال خود را از منتور هوشمند بپرسید..." 
            class="flex-1 px-5 py-3.5 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            :style="{ color: 'var(--text-primary)' }"
          />
          <button type="submit" :disabled="isChatLoading" class="px-6 py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black rounded-2xl shadow-lg transition flex items-center gap-2">
            <Send class="w-4 h-4" />
            <span>ارسال</span>
          </button>
        </form>
      </div>

    </div>
  </div>
</template>