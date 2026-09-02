<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import {
  Sparkles, Bot, TrendingUp, AlertTriangle, Lightbulb, Target,
  Send, RefreshCw, MessageSquare, CheckCircle2, ShieldAlert, Zap, ArrowRight, Clock, HelpCircle, X, Copy, Download, ChevronLeft
} from 'lucide-vue-next'

const themeStore = useThemeStore()
const isLoading = ref(true)
const isChatLoading = ref(false)
const reportData = ref(null)
const selectedTimeFrame = ref('last_1_week')
const chatMessage = ref('')
const showFullReportModal = ref(false)
const copySuccess = ref(false)

const timeFrames = [
  { id: 'last_3_days', label: '۳ روز' },
  { id: 'last_1_week', label: '۱ هفته' },
  { id: 'last_2_weeks', label: '۲ هفته' },
  { id: 'last_1_month', label: '۱ ماه' },
]

const chatHistory = ref([
  {
    sender: 'ai',
    text: 'سلام! من منتور شخصی تو هستم. هر موقع سوال داشتی، ازم بپرس. من کل زندگی و اهدافت رو می‌بینم و می‌تونم کمکت کنم. 😊'
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

const changeTimeFrame = (tfId) => {
  if (tfId === selectedTimeFrame.value) return
  selectedTimeFrame.value = tfId
  fetchReport()
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

const openFullReport = () => {
  showFullReportModal.value = true
}

const closeFullReport = () => {
  showFullReportModal.value = false
}

const copyFullReport = async () => {
  if (!reportData.value?.full_report) return
  try {
    await navigator.clipboard.writeText(reportData.value.full_report)
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2000)
  } catch (e) {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = reportData.value.full_report
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2000)
  }
}

const downloadFullReport = () => {
  if (!reportData.value?.full_report) return
  const text = `گزارش منتور - ${reportData.value.time_frame_label}\n` +
    `تاریخ: ${new Date(reportData.value.generated_at || Date.now()).toLocaleString('fa-IR')}\n` +
    `کاربر: ${reportData.value.user_name}\n` +
    `\n${'='.repeat(50)}\n\n` +
    reportData.value.full_report
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mentor-report-${new Date().toISOString().slice(0, 10)}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// گرفتن فقط ۲ پاراگراف اول از short_report
const getTwoParagraphs = (text) => {
  if (!text) return ''
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim())
  return paragraphs.slice(0, 2).join('\n\n')
}

onMounted(() => {
  fetchReport()
})
</script>

<template>
  <div class="p-3 sm:p-4 md:p-8 lg:p-10 max-w-7xl mx-auto space-y-4 sm:space-y-6 md:space-y-8 text-right" dir="rtl">

    <!-- هدر اصلی منتور هوشمند -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 shadow-2xl">
      <div class="flex items-center gap-3 sm:gap-4">
        <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl flex items-center justify-center bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 shadow-xl shadow-purple-500/30 text-white border border-white/20 shrink-0">
          <Sparkles class="w-6 h-6 sm:w-8 sm:h-8 animate-pulse" />
        </div>
        <div>
          <h1 class="text-lg sm:text-2xl md:text-3xl font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            منتور شخصی
          </h1>
          <p class="text-[11px] sm:text-xs md:text-sm mt-0.5 sm:mt-1" :style="{ color: 'var(--text-secondary)' }">تحلیل زنده و توصیه‌های تخصصی برای تو</p>
        </div>
      </div>

      <!-- انتخاب بازه زمانی -->
      <div class="flex items-center gap-1.5 sm:gap-2 bg-white/5 p-1 sm:p-1.5 rounded-xl sm:rounded-2xl border border-white/10 self-start md:self-auto">
        <Clock class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-purple-400 ml-1 mr-1.5 sm:mr-2 shrink-0" />
        <button
          v-for="tf in timeFrames"
          :key="tf.id"
          @click="changeTimeFrame(tf.id)"
          class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg sm:rounded-xl text-[11px] sm:text-xs font-black transition"
          :class="selectedTimeFrame === tf.id ? 'bg-purple-600 text-white shadow' : 'text-gray-400 hover:text-white'"
        >
          {{ tf.label }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-16 sm:py-20" :style="{ color: 'var(--text-secondary)' }">
      <Sparkles class="w-10 h-10 sm:w-12 sm:h-12 animate-spin mx-auto mb-3 text-purple-400" />
      <p class="font-bold text-xs sm:text-sm">در حال تحلیل عملکرد {{ timeFrames.find(t=>t.id===selectedTimeFrame)?.label }} توسط منتور...</p>
    </div>

    <div v-else-if="reportData" class="space-y-4 sm:space-y-6 md:space-y-8">

      <!-- کارت گزارش ۲ پاراگرافی -->
      <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 space-y-3 sm:space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <h3 class="text-base sm:text-lg md:text-xl font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            <Bot class="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 text-purple-400 shrink-0" />
            گزارش منتور ({{ reportData.time_frame_label }})
          </h3>
          <div class="flex items-center gap-2">
            <span v-if="reportData.from_cache" class="text-[10px] sm:text-xs px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">
              📌 گزارش امروز
            </span>
            <span class="text-[10px] sm:text-xs" :style="{ color: 'var(--text-secondary)' }">
              {{ new Date(reportData.generated_at).toLocaleString('fa-IR', { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' }) }}
            </span>
          </div>
        </div>

        <!-- متن ۲ پاراگرافی -->
        <div class="text-sm sm:text-base leading-loose whitespace-pre-line text-justify p-3 sm:p-4 rounded-xl sm:rounded-2xl" :style="{ color: 'var(--text-primary)', background: 'var(--bg-secondary)' }">
          {{ getTwoParagraphs(reportData.short_report) }}
        </div>

        <!-- دکمه نمایش بیشتر -->
        <div class="flex items-center justify-center pt-1">
          <button
            @click="openFullReport"
            class="px-4 sm:px-5 py-2 sm:py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black rounded-xl sm:rounded-2xl text-xs sm:text-sm transition flex items-center gap-1.5 sm:gap-2 shadow-lg"
          >
            <ChevronLeft class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            <span>نمایش گزارش کامل</span>
          </button>
        </div>
      </div>

      <!-- 💬 چت‌بات تعاملی -->
      <div class="glass-card p-4 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 space-y-3 sm:space-y-4">
        <div class="flex items-center justify-between pb-2 sm:pb-3 border-b border-white/10">
          <h3 class="text-base sm:text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            <MessageSquare class="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" />
            گفتگو با منتور
          </h3>
          <span class="text-[10px] sm:text-xs text-emerald-400 font-bold flex items-center gap-1">
            <span class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-emerald-500 inline-block animate-ping"></span>
            <span class="hidden sm:inline">کش بهینه</span>
          </span>
        </div>

        <div class="h-64 sm:h-80 overflow-y-auto space-y-3 p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-black/10 border border-white/5 custom-scrollbar">
          <div
            v-for="(msg, idx) in chatHistory"
            :key="idx"
            class="flex items-start gap-2 sm:gap-3 max-w-2xl"
            :class="msg.sender === 'user' ? 'mr-auto flex-row-reverse' : 'ml-auto'"
          >
            <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg sm:rounded-xl flex items-center justify-center text-white text-[10px] sm:text-xs font-bold shrink-0" :class="msg.sender === 'user' ? 'bg-blue-600' : 'bg-purple-600'">
              {{ msg.sender === 'user' ? 'شما' : 'AI' }}
            </div>
            <div class="p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-line border shadow-md" :class="msg.sender === 'user' ? 'bg-blue-600/20 border-blue-500/30 text-white' : 'bg-white/10 border-white/10 text-white'">
              {{ msg.text }}
            </div>
          </div>

          <div v-if="isChatLoading" class="flex items-center gap-2 text-[10px] sm:text-xs text-purple-400 font-bold p-2">
            <Sparkles class="w-3 h-3 sm:w-4 sm:h-4 animate-spin" /> منتور در حال فکر کردن...
          </div>
        </div>

        <form @submit.prevent="sendChatMessage()" class="flex items-center gap-2 sm:gap-3">
          <input
            v-model="chatMessage"
            type="text"
            placeholder="از منتور بپرس..."
            class="flex-1 px-3 sm:px-5 py-2.5 sm:py-3.5 bg-white/5 border border-white/10 rounded-xl sm:rounded-2xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" :style="{ color: 'var(--text-primary)' }"
          />
          <button type="submit" :disabled="isChatLoading" class="px-4 sm:px-6 py-2.5 sm:py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black rounded-xl sm:rounded-2xl shadow-lg transition flex items-center gap-1.5 sm:gap-2 disabled:opacity-50 text-xs sm:text-sm">
            <Send class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            <span class="hidden sm:inline">ارسال</span>
          </button>
        </form>
      </div>

    </div>

    <!-- Modal نمایش کامل گزارش -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showFullReportModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-2 sm:p-4 bg-black/85 backdrop-blur-md" @click.self="closeFullReport">
          <div class="w-full max-w-3xl max-h-[92vh] glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl border border-white/20 flex flex-col">
            <!-- هدر Modal -->
            <div class="flex items-center justify-between pb-3 sm:pb-4 mb-3 sm:mb-4 border-b border-white/10">
              <div>
                <h3 class="text-base sm:text-lg md:text-xl font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
                  <Bot class="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" />
                  گزارش کامل منتور
                </h3>
                <p class="text-[10px] sm:text-xs mt-0.5" :style="{ color: 'var(--text-secondary)' }">
                  {{ reportData?.time_frame_label }} - {{ new Date(reportData?.generated_at || Date.now()).toLocaleString('fa-IR') }}
                </p>
              </div>
              <button @click="closeFullReport" class="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center transition">
                <X class="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>

            <!-- محتوای گزارش -->
            <div class="flex-1 overflow-y-auto p-3 sm:p-4 md:p-5 rounded-xl sm:rounded-2xl" :style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }">
              <div class="text-sm sm:text-base leading-loose whitespace-pre-line text-justify">
                {{ reportData?.full_report }}
              </div>
            </div>

            <!-- دکمه‌های action -->
            <div class="flex items-center gap-2 sm:gap-3 pt-3 sm:pt-4 mt-3 sm:mt-4 border-t border-white/10">
              <button
                @click="copyFullReport"
                class="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl sm:rounded-2xl text-xs sm:text-sm font-bold flex items-center justify-center gap-1.5 sm:gap-2 transition" :style="{ color: 'var(--text-primary)' }"
              >
                <Copy class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                <span>{{ copySuccess ? 'کپی شد ✓' : 'کپی متن' }}</span>
              </button>
              <button
                @click="downloadFullReport"
                class="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 text-white rounded-xl sm:rounded-2xl text-xs sm:text-sm font-bold flex items-center justify-center gap-1.5 sm:gap-2 shadow-lg transition"
              >
                <Download class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                <span>ذخیره فایل</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
.modal-enter-from > div, .modal-leave-to > div {
  transform: scale(0.9) translateY(20px);
}
</style>
