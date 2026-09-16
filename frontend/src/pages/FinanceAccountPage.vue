<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useThemeStore } from '@/stores/theme'
import { formatDate } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()

const account = ref(null)
const loading = ref(true)
const loadError = ref(false)

const fetchAccount = async () => {
  loading.value = true; loadError.value = false
  try {
    const res = await api.get('/finance/accounts')
    const list = Array.isArray(res.data) ? res.data : []
    account.value = list.find(a => String(a.id) === String(route.params.id)) || null
    if (!account.value) loadError.value = true
  } catch (e) { loadError.value = true }
  finally { loading.value = false }
}

const txs = computed(() => account.value?.transactions || [])
const totalIn = computed(() => txs.value.filter(t => t.transaction_type === 'deposit').reduce((s, t) => s + Number(t.amount || 0), 0))
const totalOut = computed(() => txs.value.filter(t => t.transaction_type !== 'deposit').reduce((s, t) => s + Number(t.amount || 0), 0))
const faNum = (n) => Number(n || 0).toLocaleString('fa-IR')

onMounted(fetchAccount)
</script>

<template>
  <div class="max-w-3xl mx-auto px-3 sm:px-4 py-5">
    <button @click="router.push('/finance')" class="mb-4 px-3 py-1.5 rounded-lg text-xs font-bold border border-white/10 bg-white/5 hover:bg-white/10 transition" :style="{ color: 'var(--text-primary)' }">→ بازگشت به مالی</button>

    <div v-if="loading" class="text-center py-16 text-sm font-bold" :style="{ color: 'var(--text-secondary)' }">⏳ در حال بارگذاری حساب…</div>

    <div v-else-if="loadError || !account" class="text-center py-16">
      <p class="text-sm font-bold mb-3" :style="{ color: 'var(--text-secondary)' }">❌ حساب پیدا نشد</p>
      <button @click="router.push('/finance')" class="px-4 py-2 rounded-lg text-xs font-black bg-blue-500/90 hover:bg-blue-400 text-white transition">بازگشت به مالی</button>
    </div>

    <div v-else>
      <div class="rounded-2xl border border-white/10 bg-white/[0.03] p-4 sm:p-6 mb-4">
        <h1 class="text-xl sm:text-2xl font-black mb-1" :style="{ color: 'var(--text-primary)' }">{{ account.name }}</h1>
        <p v-if="account.bank_name" class="text-xs font-bold mb-3" :style="{ color: 'var(--text-secondary)' }">{{ account.bank_name }}</p>
        <div class="flex flex-wrap gap-2 sm:gap-3 text-xs font-black">
          <span class="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10" :style="{ color: 'var(--text-primary)' }">💰 موجودی: {{ faNum(account.current_balance) }} تومان</span>
          <span class="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">⬆ ورودی: {{ faNum(totalIn) }}</span>
          <span class="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300">⬇ خروجی: {{ faNum(totalOut) }}</span>
        </div>
      </div>

      <h2 class="text-sm font-black mb-2" :style="{ color: 'var(--text-primary)' }">🧾 تراکنش‌ها ({{ faNum(txs.length) }})</h2>
      <div v-if="txs.length === 0" class="text-center py-10 text-xs font-bold" :style="{ color: 'var(--text-secondary)' }">تراکنشی ثبت نشده است</div>
      <div v-else class="rounded-2xl border border-white/10 overflow-hidden divide-y divide-white/5">
        <div v-for="t in txs" :key="t.id" class="flex items-center justify-between gap-2 p-3 sm:p-4 bg-white/[0.02]">
          <div class="min-w-0">
            <p class="text-xs sm:text-sm font-bold truncate" :style="{ color: 'var(--text-primary)' }">{{ t.category || t.description || '—' }}</p>
            <p class="text-[10px] sm:text-xs font-bold" :style="{ color: 'var(--text-secondary)' }">{{ formatDate(t.transaction_date) }}</p>
          </div>
          <span class="text-xs sm:text-sm font-black shrink-0" :style="{ color: t.transaction_type === 'deposit' ? '#6ee7b7' : '#fca5a5' }">{{ t.transaction_type === 'deposit' ? '+' : '−' }}{{ faNum(t.amount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
