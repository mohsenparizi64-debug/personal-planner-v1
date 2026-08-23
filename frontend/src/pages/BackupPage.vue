<script setup>
import { ref } from 'vue'
import { Download, Upload, AlertTriangle } from 'lucide-vue-next'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isExporting = ref(false)
const isImporting = ref(false)
const message = ref('')
const messageType = ref('success')
const fileInput = ref(null)

const exportBackup = async () => {
  isExporting.value = true
  try {
    const response = await api.get('/backup/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    const now = new Date().toISOString().slice(0, 10)
    link.setAttribute('download', `planner-backup-${now}.json`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    message.value = '✅ بکاپ با موفقیت دانلود شد'
    messageType.value = 'success'
  } catch (e) {
    message.value = '❌ خطا در تهیه بکاپ'
    messageType.value = 'error'
  } finally { isExporting.value = false }
}

const importBackup = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!confirm('⚠️ با این کار همه دیتای فعلی حذف و با بکاپ جایگزین میشه. مطمئنی؟')) {
    fileInput.value.value = ''
    return
  }
  
  isImporting.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/backup/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    message.value = `✅ بازیابی موفق! ${JSON.stringify(response.data.counts)}`
    messageType.value = 'success'
    // رفرش کل صفحات با reload
    setTimeout(() => window.location.reload(), 2000)
  } catch (e) {
    message.value = '❌ خطا در بازیابی. فایل معتبر نیست.'
    messageType.value = 'error'
  } finally {
    isImporting.value = false
    fileInput.value.value = ''
  }
}
</script>

<template>
  <div class="min-h-screen bg-surface-dark p-6 md:p-10 max-w-2xl mx-auto">
    
    <div class="mb-10">
      <h1 class="text-3xl font-extrabold text-white mb-2">بکاپ و بازیابی</h1>
      <p class="text-gray-500">تهیه نسخه پشتیبان از تمام اطلاعات و بازیابی آن</p>
    </div>

    <!-- پیام -->
    <div v-if="message" :class="messageType === 'error' ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'" 
         class="p-4 rounded-xl mb-6 text-sm">{{ message }}</div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- کارت بکاپ -->
      <div class="bg-surface-card rounded-2xl border border-white/5 p-6">
        <div class="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center mb-4">
          <Download class="w-6 h-6 text-green-400" />
        </div>
        <h3 class="text-lg font-bold text-white mb-2">دریافت بکاپ</h3>
        <p class="text-sm text-gray-500 mb-4">یک فایل JSON از تمام اطلاعاتت دانلود کن. این فایل شامل تسک‌ها، اهداف، مالی، فیلم‌ها، کتاب‌ها و مکان‌هاست.</p>
        <button @click="exportBackup" :disabled="isExporting"
                class="w-full py-2.5 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition disabled:opacity-50">
          {{ isExporting ? 'در حال آماده‌سازی...' : 'دانلود بکاپ 📥' }}
        </button>
      </div>

      <!-- کارت بازیابی -->
      <div class="bg-surface-card rounded-2xl border border-white/5 p-6">
        <div class="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center mb-4">
          <Upload class="w-6 h-6 text-orange-400" />
        </div>
        <h3 class="text-lg font-bold text-white mb-2">بازیابی بکاپ</h3>
        <p class="text-sm text-gray-500 mb-4">فایل JSON بکاپ رو آپلود کن تا همه اطلاعاتت برگرده. ⚠️ دیتای فعلی حذف میشه!</p>
        
        <input ref="fileInput" type="file" accept=".json" @change="importBackup" class="hidden" />
        <button @click="fileInput?.click()" :disabled="isImporting"
                class="w-full py-2.5 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-xl transition disabled:opacity-50">
          {{ isImporting ? 'در حال بازیابی...' : 'آپلود و بازیابی 📤' }}
        </button>
      </div>

    </div>

    <!-- هشدار -->
    <div class="mt-8 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20 flex items-start gap-3">
      <AlertTriangle class="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
      <div class="text-sm text-yellow-300">
        <p class="font-bold mb-1">نکات مهم:</p>
        <ul class="list-disc mr-4 space-y-1 text-yellow-200/80">
          <li>بکاپ شامل <strong>همه</strong> ماژول‌هاست (تسک، هدف، مالی، فیلم، کتاب، مکان)</li>
          <li>فایل بکاپ با فرمت JSON ذخیره میشه و قابل مشاهده با ویرایشگر متنه</li>
          <li>هنگام بازیابی، <strong>همه دیتای فعلی حذف</strong> و با بکاپ جایگزین میشه</li>
          <li>پسورد شما توی بکاپ ذخیره <strong>نمیشه</strong> - فقط دیتای برنامه</li>
          <li>توصیه میشه هر هفته یه بکاپ بگیرید</li>
        </ul>
      </div>
    </div>

  </div>
</template>