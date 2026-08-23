<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animId = null

function drawClock() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  const radius = width / 2
  
  ctx.clearRect(0, 0, width, height)

  const now = new Date()
  const hours = now.getHours() % 12
  const minutes = now.getMinutes()
  const seconds = now.getSeconds()
  const milliseconds = now.getMilliseconds()

  ctx.save()
  ctx.translate(radius, radius)

  // ۱. پس‌زمینه و حلقه بیرونی درخشان بزرگتر
  ctx.beginPath()
  ctx.arc(0, 0, radius - 3, 0, 2 * Math.PI)
  ctx.fillStyle = 'rgba(15, 23, 42, 0.7)'
  ctx.fill()
  ctx.lineWidth = 2
  ctx.strokeStyle = '#8b5cf6' // هاله بنفش
  ctx.stroke()

  // ۲. نشانگرهای ۱۲ ساعت
  for (let i = 0; i < 12; i++) {
    const angle = (i * Math.PI) / 6
    ctx.rotate(angle)
    ctx.beginPath()
    ctx.moveTo(0, -(radius - 8))
    ctx.lineTo(0, -(radius - (i % 3 === 0 ? 14 : 10)))
    ctx.lineWidth = i % 3 === 0 ? 2.5 : 1.2
    ctx.strokeStyle = i % 3 === 0 ? '#8b5cf6' : 'rgba(255, 255, 255, 0.4)'
    ctx.stroke()
    ctx.rotate(-angle)
  }

  // ۳. عقربه ساعت (ضخیم‌تر)
  const hourAngle = (hours * Math.PI) / 6 + (minutes * Math.PI) / 360
  ctx.save()
  ctx.rotate(hourAngle)
  ctx.beginPath()
  ctx.moveTo(0, 5)
  ctx.lineTo(0, -(radius * 0.45))
  ctx.lineWidth = 4
  ctx.lineCap = 'round'
  ctx.strokeStyle = '#ffffff'
  ctx.stroke()
  ctx.restore()

  // ۴. عقربه دقیقه
  const minuteAngle = (minutes * Math.PI) / 30 + (seconds * Math.PI) / 1800
  ctx.save()
  ctx.rotate(minuteAngle)
  ctx.beginPath()
  ctx.moveTo(0, 7)
  ctx.lineTo(0, -(radius * 0.68))
  ctx.lineWidth = 2.5
  ctx.lineCap = 'round'
  ctx.strokeStyle = '#3b82f6'
  ctx.stroke()
  ctx.restore()

  // ۵. عقربه ثانیه (روان)
  const exactSecond = seconds + milliseconds / 1000
  const secondAngle = (exactSecond * Math.PI) / 30
  ctx.save()
  ctx.rotate(secondAngle)
  ctx.beginPath()
  ctx.moveTo(0, 10)
  ctx.lineTo(0, -(radius * 0.82))
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.strokeStyle = '#ef4444'
  ctx.stroke()
  ctx.restore()

  // ۶. دکمه مرکزی
  ctx.beginPath()
  ctx.arc(0, 0, 4, 0, 2 * Math.PI)
  ctx.fillStyle = '#ef4444'
  ctx.fill()

  ctx.restore()

  animId = requestAnimationFrame(drawClock)
}

onMounted(() => {
  animId = requestAnimationFrame(drawClock)
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
})
</script>

<template>
  <div class="relative flex items-center justify-center p-1.5 rounded-full shadow-xl" :style="{ background: 'rgba(255, 255, 255, 0.08)', border: '1px solid rgba(255, 255, 255, 0.15)' }">
    <canvas ref="canvasRef" width="64" height="64" class="block"></canvas>
  </div>
</template>