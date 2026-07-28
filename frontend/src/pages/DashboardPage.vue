<script setup>
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { ListTodo, CheckCircle, Flame, TrendingUp, Zap } from 'lucide-vue-next'

const themeStore = useThemeStore()

const stats = ref([
  { title: 'تسک‌های امروز', value: 5, icon: ListTodo },
  { title: 'تکمیل‌شده', value: 3, icon: CheckCircle },
  { title: 'روزهای متوالی', value: 12, icon: Flame },
  { title: 'پیشرفت هفته', value: '68%', icon: TrendingUp },
])
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto">
    <!-- Welcome -->
    <div class="mb-10" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center"
             :class="themeStore.currentTheme === 'persian-classic' ? 'bg-amber-100' : themeStore.currentTheme === 'cyber-digital' ? 'bg-green-500/20 neon-border' : 'bg-purple-500/20'">
          <Zap class="w-5 h-5" :style="{ color: 'var(--accent)' }" />
        </div>
        <h1 class="text-3xl font-extrabold">روزت به خیر! 👋</h1>
      </div>
      <p :style="{ color: 'var(--text-secondary)' }">امروز یه روز عالی برای پیشرفته.</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      <div 
        v-for="stat in stats" 
        :key="stat.title"
        :class="[
          'relative overflow-hidden rounded-2xl p-6 group transition-all duration-300',
          themeStore.currentTheme === 'persian-classic' ? 'card-ornament' : 
          themeStore.currentTheme === 'cyber-digital' ? 'neon-border' : 'glass-card'
        ]"
        :style="{ background: 'var(--bg-card)' }"
      >
        <div class="flex items-center justify-between">
          <div>
            <p :style="{ color: 'var(--text-secondary)' }" class="text-sm mb-1">{{ stat.title }}</p>
            <p class="text-3xl font-extrabold" :style="{ color: 'var(--text-primary)' }">{{ stat.value }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center" :style="{ background: 'var(--bg-hover)' }">
            <component :is="stat.icon" class="w-6 h-6" :style="{ color: 'var(--accent)' }" />
          </div>
        </div>
      </div>
    </div>

    <!-- تم کلاسیک: تزئینات اضافی -->
    <div v-if="themeStore.currentTheme === 'persian-classic'" class="text-center mb-10">
      <p class="text-2xl font-bold" style="color: var(--accent); font-family: BNazanin, serif;">
        به نام خداوند جان و خرد
      </p>
      <div class="flex justify-center gap-2 mt-2">
        <span class="text-4xl">🏛️</span>
        <span class="text-4xl">🕌</span>
        <span class="text-4xl">🦁</span>
      </div>
    </div>

    <!-- تم رباتیک: تزئینات اضافی -->
    <div v-if="themeStore.currentTheme === 'cyber-digital'" class="mb-10">
      <div class="flex items-center gap-2 neon-text">
        <span class="text-2xl">⚡</span>
        <p class="text-lg font-mono">SYS::ONLINE // NODES: 4 // UPLINK: STABLE</p>
      </div>
    </div>

    <!-- Quick Tasks -->
    <div 
      :class="[
        'rounded-2xl p-6',
        themeStore.currentTheme === 'persian-classic' ? 'card-ornament' : 
        themeStore.currentTheme === 'cyber-digital' ? 'neon-border' : 'glass-card'
      ]"
      :style="{ background: 'var(--bg-card)' }"
    >
      <h2 class="text-lg font-bold mb-4 flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
        <ListTodo class="w-5 h-5" :style="{ color: 'var(--accent)' }" />
        کارهای امروز
      </h2>
      <div class="space-y-2">
        <div class="flex items-center gap-3 p-3 rounded-xl transition cursor-pointer" :style="{ background: 'var(--bg-hover)' }">
          <div class="w-5 h-5 rounded-lg border-2 flex-shrink-0" :style="{ borderColor: 'var(--border)' }"></div>
          <span :style="{ color: 'var(--text-primary)' }">مطالعه معماری FastAPI</span>
        </div>
        <div class="flex items-center gap-3 p-3 rounded-xl transition cursor-pointer" :style="{ background: 'var(--bg-hover)' }">
          <div class="w-5 h-5 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ background: 'var(--accent)' }">
            <CheckCircle class="w-3 h-3 text-white" />
          </div>
          <span :style="{ color: 'var(--text-secondary)', textDecoration: 'line-through' }">ورزش صبحگاهی</span>
        </div>
      </div>
    </div>
  </div>
</template>