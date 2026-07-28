<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const canvas = ref(null)
let animationId = null

function drawClock() {
  const ctx = canvas.value?.getContext('2d')
  if (!ctx) return

  const size = 100
  canvas.value.width = size
  canvas.value.height = size

  const now = new Date()
  const hours = now.getHours() % 12
  const minutes = now.getMinutes()
  const seconds = now.getSeconds()

  const cx = size / 2
  const cy = size / 2
  const radius = size / 2 - 4

  // Clear
  ctx.clearRect(0, 0, size, size)

  // رنگ‌ها بر اساس تم
  const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#8b5cf6'
  const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#e2e8f0'
  const bgColor = getComputedStyle(document.documentElement).getPropertyValue('--bg-card').trim() || '#1a1a2e'

  // بدنه ساعت
  ctx.beginPath()
  ctx.arc(cx, cy, radius, 0, Math.PI * 2)
  ctx.fillStyle = bgColor
  ctx.fill()
  ctx.strokeStyle = accent
  ctx.lineWidth = 2
  ctx.stroke()

  // glow effect
  ctx.shadowColor = accent
  ctx.shadowBlur = 8
  ctx.stroke()
  ctx.shadowBlur = 0

  // اعداد
  ctx.fillStyle = textColor
  ctx.font = 'bold 11px Vazirmatn'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  for (let i = 1; i <= 12; i++) {
    const angle = (i * 30 - 90) * Math.PI / 180
    const x = cx + Math.cos(angle) * (radius - 16)
    const y = cy + Math.sin(angle) * (radius - 16)
    ctx.fillText(i.toString(), x, y)
  }

  // عقربه‌ها
  drawHand(ctx, cx, cy, (hours * 30 + minutes * 0.5 - 90) * Math.PI / 180, radius * 0.5, 4, accent)
  drawHand(ctx, cx, cy, (minutes * 6 - 90) * Math.PI / 180, radius * 0.7, 3, textColor)
  drawHand(ctx, cx, cy, (seconds * 6 - 90) * Math.PI / 180, radius * 0.8, 1.5, '#ef4444')

  // نقطه مرکزی
  ctx.beginPath()
  ctx.arc(cx, cy, 4, 0, Math.PI * 2)
  ctx.fillStyle = accent
  ctx.fill()

  animationId = requestAnimationFrame(drawClock)
}

function drawHand(ctx, x, y, angle, length, width, color) {
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + Math.cos(angle) * length, y + Math.sin(angle) * length)
  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.lineCap = 'round'
  ctx.stroke()
}

onMounted(() => {
  drawClock()
})
onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="relative inline-flex items-center gap-3">
    <canvas ref="canvas" class="w-[50px] h-[50px] md:w-[60px] md:h-[60px]"></canvas>
  </div>
</template>