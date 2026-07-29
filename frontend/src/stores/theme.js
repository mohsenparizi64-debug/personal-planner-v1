import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'dark-modern')

  const themes = [
    { id: 'dark-modern', label: 'مدرن تاریک', icon: '🌙' },
    { id: 'persian-classic', label: 'کلاسیک ایرانی', icon: '🏛️' },
    { id: 'cyber-digital', label: 'رباتیک دیجیتال', icon: '🤖' },
    { id: 'gemini-theme', label: 'جمنای هوش مصنوعی', icon: '✨' },
  ]

  function setTheme(themeId) {
    currentTheme.value = themeId
    localStorage.setItem('theme', themeId)
    applyTheme(themeId)
  }

  function applyTheme(themeId) {
    const root = document.documentElement
    root.className = themeId
  }

  // اعمال تم ذخیره شده در startup
  applyTheme(currentTheme.value)

  return { currentTheme, themes, setTheme }
})