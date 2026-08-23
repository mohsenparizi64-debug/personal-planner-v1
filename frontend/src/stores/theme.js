import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'light-2026')
  
  // 🔤 مقیاس جهانی اندازه‌ فونت کل برنامه (100% | 120% | 135%)
  const fontScale = ref(localStorage.getItem('fontScale') || '100%')

  const themes = [
    { id: 'light-2026', label: 'روشن مدرن ۲۰۲۶', icon: '☀️' },
    { id: 'dark-modern', label: 'مدرن تاریک', icon: '🌙' },
    { id: 'persian-classic', label: 'کلاسیک ایرانی', icon: '🏛️' },
    { id: 'cyber-digital', label: 'رباتیک دیجیتال', icon: '🤖' },
    { id: 'gemini-theme', label: 'جمنای هوش مصنوعی', icon: '✨' },
  ]

  const fontScaleOptions = [
    { id: '100%', label: 'استاندارد (۱۰۰٪)' },
    { id: '120%', label: 'درشت (۱۲۰٪)' },
    { id: '135%', label: 'خیلی درشت (۱۳۵٪)' },
  ]

  function setTheme(themeId) {
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
    fontScale, 
    fontScaleOptions, 
    setTheme, 
    setFontScale 
  }
})