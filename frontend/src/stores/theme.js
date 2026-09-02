import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'light-2026')

  // 🔤 مقیاس جهانی اندازه‌ فونت کل برنامه (100% | 120% | 135%)
  const fontScale = ref(localStorage.getItem('fontScale') || '100%')

  // 🛡️ لیست تم‌های معتبر (اگه کاربر تم قدیمی داشت، به پیش‌فرض برمیگرده)
  const validThemes = ['light-2026', 'dark-modern-2026', 'cyber-digital']

  // اگه تم ذخیره‌شده دیگه معتبر نیست (مثلاً کاربر قبلاً dark-modern یا persian-classic داشت)
  // به تم پیش‌فرض light-2026 برگرد
  if (!validThemes.includes(currentTheme.value)) {
    currentTheme.value = 'light-2026'
    localStorage.setItem('theme', 'light-2026')
  }

  const themes = [
    { id: 'light-2026', label: 'روشن مدرن ۲۰۲۶', icon: '☀️' },
    { id: 'dark-modern-2026', label: 'تیره مدرن ۲۰۲۶', icon: '🌙' },
    { id: 'cyber-digital', label: 'رباتیک دیجیتال', icon: '🤖' },
  ]

  const fontScaleOptions = [
    { id: '100%', label: 'استاندارد (۱۰۰٪)' },
    { id: '120%', label: 'درشت (۱۲۰٪)' },
    { id: '135%', label: 'خیلی درشت (۱۳۵٪)' },
  ]

  function setTheme(themeId) {
    // اگه تم معتبر نیست، نادیده بگیر
    if (!validThemes.includes(themeId)) {
      console.warn(`⚠️ تم "${themeId}" معتبر نیست`)
      return
    }
    currentTheme.value = themeId
    localStorage.setItem('theme', themeId)
    applyTheme(themeId)
  }

  // 🔤 اعمال مستقیم مقیاس فونت روی ریشه رندر مرورگر (HTML Root)
  function setFontScale(scale) {
    fontScale.value = scale
    localStorage.setItem('fontScale', scale)
    document.documentElement.style.fontSize = scale
  }

  function applyTheme(themeId) {
    const root = document.documentElement
    root.className = themeId
  }

  // Startup initialization
  applyTheme(currentTheme.value)
  setFontScale(fontScale.value)

  return {
    currentTheme,
    themes,
    validThemes,
    fontScale,
    fontScaleOptions,
    setTheme,
    setFontScale
  }
})
