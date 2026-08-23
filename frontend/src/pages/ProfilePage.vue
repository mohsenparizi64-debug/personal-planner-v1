<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { User, Mail, Phone, Save, Camera, ArrowRight } from 'lucide-vue-next'

const auth = useAuthStore()
const message = ref('')
const messageType = ref('success')
const isLoading = ref(false)

const form = ref({
  full_name: '',
  phone: '',
  bio: '',
  avatar_url: ''
})

onMounted(() => {
  if (auth.user) {
    form.value = {
      full_name: auth.user.full_name || '',
      phone: auth.user.phone || '',
      bio: auth.user.bio || '',
      avatar_url: auth.user.avatar_url || ''
    }
  }
})

const saveProfile = async () => {
  isLoading.value = true
  try {
    await auth.updateProfile(form.value)
    message.value = '✅ پروفایل با موفقیت بروزرسانی شد'
    messageType.value = 'success'
  } catch (e) {
    message.value = '❌ خطا در بروزرسانی'
    messageType.value = 'error'
  } finally { isLoading.value = false }
}

const handleAvatarUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    form.value.avatar_url = e.target.result
  }
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="p-6 md:p-10 max-w-2xl mx-auto min-h-screen">
    
    <button @click="$router.push('/')" class="flex items-center gap-2 text-sm mb-6 transition" :style="{ color: 'var(--accent)' }">
      <ArrowRight class="w-4 h-4" /> برگشت به داشبورد
    </button>

    <div class="mb-6">
      <h1 class="text-3xl font-extrabold text-white mb-2">پروفایل کاربری</h1>
      <p class="text-gray-500">مدیریت اطلاعات حساب کاربری</p>
    </div>

    <div v-if="message" :class="messageType === 'error' ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'" 
         class="p-4 rounded-xl mb-6 text-sm">{{ message }}</div>

    <div class="bg-surface-card rounded-2xl border border-white/5 p-6">
      
      <div class="flex flex-col items-center mb-8">
        <div class="relative group cursor-pointer" @click="$refs.avatarInput.click()">
          <div class="w-24 h-24 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-2xl"
               :style="{ background: form.avatar_url ? `url(${form.avatar_url}) center/cover` : 'linear-gradient(135deg, #8b5cf6, #3b82f6)' }">
            {{ !form.avatar_url ? (auth.user?.full_name?.charAt(0) || 'U') : '' }}
          </div>
          <div class="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
            <Camera class="w-8 h-8 text-white" />
          </div>
        </div>
        <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarUpload" class="hidden" />
        <p class="text-xs text-gray-500 mt-2">روی آواتار کلیک کن</p>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-2 flex items-center gap-2"><User class="w-4 h-4" /> نام کامل</label>
          <input v-model="form.full_name" placeholder="نام و نام خانوادگی"
                 class="w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl text-right text-gray-200" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2 flex items-center gap-2"><Mail class="w-4 h-4" /> ایمیل</label>
          <input :value="auth.user?.email" disabled
                 class="w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl text-right text-gray-500 opacity-60" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2 flex items-center gap-2"><Phone class="w-4 h-4" /> شماره موبایل</label>
          <input v-model="form.phone" placeholder="09123456789" dir="ltr"
                 class="w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl text-left text-gray-200" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">بیوگرافی</label>
          <textarea v-model="form.bio" rows="3" placeholder="درباره خودت بنویس..."
                    class="w-full px-4 py-3 bg-surface-dark border border-white/10 rounded-xl text-right text-gray-200"></textarea>
        </div>

        <button @click="saveProfile" :disabled="isLoading"
                class="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl transition disabled:opacity-50 flex items-center justify-center gap-2">
          <Save class="w-5 h-5" /> {{ isLoading ? 'در حال ذخیره...' : 'ذخیره تغییرات' }}
        </button>
      </div>
    </div>

  </div>
</template>