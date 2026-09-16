<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useThemeStore } from '@/stores/theme'
import { formatDate } from '@/utils/date'
import DateInputPersian from '@/components/DateInputPersian.vue'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()

const account = ref(null)
const loading = ref(true)
const loadError = ref(false)
const message = ref('')

const showToast = (msg) => { message.value = msg; setTimeout(() => message.value = '', 3000) }

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

// ====== ویرایش / حذف تراکنش ======
const showForm = ref(false)
const editingTrans = ref(null)
const form = ref({ transaction_date: '', transaction_type: 'withdrawal', amount: 0, category: '', items: '', description: '' })
const formError = ref('')

const categories = {
  withdrawal: [
    { id: 'food', name: 'خوراک و رستوران' },
    { id: 'transport', name: 'حمل و نقل / خودرو' },
    { id: 'home', name: 'اجاره و قبوض' },
    { id: 'shopping', name: 'خرید لباس و کالا' },
    { id: 'health', name: 'سلامت و درمان' },
    { id: 'digital', name: 'اشتراک و ابزار دیجیتال' },
    { id: 'loan', name: 'قسط و بدهی' },
    { id: 'services', name: 'خدمات و سرویس‌ها' },
    { id: 'education', name: 'آموزش و کتاب' },
    { id: 'leisure', name: 'تفریح و سفر' },
    { id: 'saving', name: 'پس‌انداز و سرمایه‌گذاری' },
    { id: 'other_out', name: 'سایر هزینه‌ها' },
  ],
  deposit: [
    { id: 'salary', name: 'حقوق و دستمزد' },
    { id: 'gift', name: 'هدیه / جایزه' },
    { id: 'selling', name: 'فروش کالا' },
    { id: 'other_in', name: 'سایر درآمدها' },
  ]
}
const catName = (type, id) => categories[type]?.find(c => c.id === id)?.name || categories.withdrawal.find(c => c.id === id)?.name || categories.deposit.find(c => c.id === id)?.name || id

const openEdit = (trans) => {
  editingTrans.value = trans
  form.value = {
    transaction_date: (trans.transaction_date || '').slice(0, 10),
    transaction_type: trans.transaction_type || 'withdrawal',
    amount: trans.amount || 0,
    category: trans.category || '',
    items: trans.items || '',
    description: trans.description || '',
  }
  formError.value = ''
  showForm.value = true
}

const saveEdit = async () => {
  const amount = Number(String(form.value.amount).replace(/,/g, '')) || 0
  if (amount <= 0) { formError.value = 'مبلغ باید بزرگ‌تر از صفر باشد'; return }
  if (!form.value.category) { formError.value = 'دسته‌بندی را انتخاب کن'; return }
  try {
    await api.put(`/finance/transactions/${editingTrans.value.id}`, { ...form.value, amount })
    showForm.value = false
    showToast('✅ تراکنش ویرایش شد')
    await fetchAccount()
  } catch (e) { formError.value = '❌ خطا در ذخیره' }
}

const delTrans = async (id) => {
  if (!confirm('این تراکنش حذف شود؟')) return
  try {
    await api.delete(`/finance/transactions/${id}`)
    showToast('🗑️ تراکنش حذف شد')
    await fetchAccount()
  } catch (e) { showToast('❌ خطا در حذف') }
}

onMounted(fetchAccount)
</script>

<template>
  <div class="max-w-3xl mx-auto px-3 sm:px-4 py-5" dir="rtl">
    <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold text-sm" :style="{ background: 'var(--accent)' }">{{ message }}</div>

    <button @click="router.push('/finance')" class="mb-4 px-3 py-1.5 rounded-lg text-xs font-bold border border-white/10 bg-white/5 hover:bg-white/10 transition" :style="{ color: 'var(--text-primary)' }">→ بازگشت به مالی</button>

    <div v-if="loading" class="text-center py-16 text-sm font-bold" :style="{ color: 'var(--text-secondary)' }">⏳ در حال بارگذاری حساب…</div>

    <div v-else-if="loadError || !account" class="text-center py-16">
      <p class="text-sm font-bold mb-3" :style="{ color: 'var(--text-secondary)' }">❌ حساب پیدا نشد</p>
      <button @click="router.push('/finance')" class="px-4 py-2 rounded-lg text-xs font-black bg-blue-500/90 hover:bg-blue-400 text-white transition">بازگشت به مالی</button>
    </div>

    <div v-else>
      <div class="rounded-2xl border border-white/10 bg-white/[0.03] p-4 sm:p-6 mb-4">
        <h1 class="text-xl sm:text-2xl font-black mb-1" :style="{ color: 'var(--text-primary)' }">{{ account.name }} <span v-if="account.is_hidden">🙈</span></h1>
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
          <div class="min-w-0 flex-1">
            <p class="text-xs sm:text-sm font-bold truncate" :style="{ color: 'var(--text-primary)' }">{{ t.description || catName(t.transaction_type, t.category) }}</p>
            <p class="text-[10px] sm:text-xs font-bold" :style="{ color: 'var(--text-secondary)' }">{{ catName(t.transaction_type, t.category) }} • {{ formatDate(t.transaction_date) }}</p>
          </div>
          <span class="text-xs sm:text-sm font-black shrink-0" :style="{ color: t.transaction_type === 'deposit' ? '#6ee7b7' : '#fca5a5' }">{{ t.transaction_type === 'deposit' ? '+' : '−' }}{{ faNum(t.amount) }}</span>
          <div class="flex gap-1 shrink-0">
            <button @click="openEdit(t)" title="ویرایش" class="px-2 py-1.5 rounded-lg text-xs bg-white/10 hover:bg-white/20 transition">✏️</button>
            <button @click="delTrans(t.id)" title="حذف" class="px-2 py-1.5 rounded-lg text-xs bg-red-500/15 text-red-300 hover:bg-red-500/30 transition">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- مودال ویرایش تراکنش -->
    <div v-if="showForm" class="fixed inset-0 z-[300] flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md" @click.self="showForm = false">
      <div class="w-full max-w-md max-h-[92vh] overflow-y-auto rounded-2xl p-5 bg-gray-900/95 border border-white/10 shadow-2xl text-white space-y-4">
        <h3 class="text-lg font-black">ویرایش تراکنش</h3>
        <div class="flex gap-2 p-1 rounded-2xl bg-black/40 border border-white/10">
          <button @click="form.transaction_type = 'withdrawal'; form.category = ''"
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition"
                  :style="form.transaction_type === 'withdrawal' ? { background: '#ef4444', color: '#fff' } : { color: 'var(--text-secondary)' }">برداشت</button>
          <button @click="form.transaction_type = 'deposit'; form.category = ''"
                  class="flex-1 py-2 rounded-xl text-xs font-bold transition"
                  :style="form.transaction_type === 'deposit' ? { background: '#22c55e', color: '#fff' } : { color: 'var(--text-secondary)' }">واریز</button>
        </div>
        <div>
          <label class="text-xs mb-1.5 block opacity-70 font-bold">دسته‌بندی *</label>
          <select v-model="form.category" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm">
            <option value="">— انتخاب —</option>
            <option v-for="c in categories[form.transaction_type]" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs mb-1.5 block opacity-70 font-bold">مبلغ (تومان) *</label>
          <input v-model.number="form.amount" type="number" min="0" inputmode="numeric"
                 class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-lg font-black text-center" />
        </div>
        <div v-if="form.transaction_type === 'withdrawal'">
          <label class="text-xs mb-1.5 block opacity-70 font-bold">اقلام خرید</label>
          <input v-model="form.items" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
        </div>
        <div>
          <label class="text-xs mb-1.5 block opacity-70 font-bold">توضیحات</label>
          <input v-model="form.description" class="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
        </div>
        <div>
          <label class="text-xs mb-1.5 block opacity-70 font-bold">تاریخ تراکنش</label>
          <DateInputPersian v-model="form.transaction_date" />
        </div>
        <p v-if="formError" class="text-xs font-bold text-red-300">{{ formError }}</p>
        <div class="flex gap-2">
          <button @click="saveEdit" class="flex-1 py-3 rounded-xl text-white font-bold text-sm" :style="{ background: 'var(--accent)' }">ذخیره تغییرات</button>
          <button @click="showForm = false" class="px-5 py-3 rounded-xl text-sm font-semibold bg-white/10 hover:bg-white/20 transition">انصراف</button>
        </div>
      </div>
    </div>
  </div>
</template>
