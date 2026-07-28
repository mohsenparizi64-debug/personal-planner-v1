<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Plus, Trash2, Edit3, X, Wallet, CreditCard, Banknote, TrendingUp, TrendingDown, Calendar, ArrowUp, ArrowDown } from 'lucide-vue-next'
import api from '@/services/api'

const themeStore = useThemeStore()
const accounts = ref([])
const message = ref('')
const messageType = ref('success')

// فرم حساب
const showAccountForm = ref(false)
const editingAccount = ref(null)
const accountForm = ref({ name: '', bank_name: '', sheba_number: '', current_balance: 0, register_date: new Date().toISOString().split('T')[0] })

// فرم تراکنش
const showTransactionForm = ref(false)
const selectedAccountId = ref(null)
const selectedAccount = ref(null)
const transactionForm = ref({ transaction_date: new Date().toISOString().split('T')[0], transaction_type: 'deposit', amount: 0, description: '' })

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchAccounts = async () => {
  try { const res = await api.get('/finance/accounts'); accounts.value = res.data } catch (e) {}
}

// ====== Account CRUD ======
const openNewAccount = () => {
  accountForm.value = { name: '', bank_name: '', sheba_number: '', current_balance: 0, register_date: new Date().toISOString().split('T')[0] }
  editingAccount.value = null
  showAccountForm.value = true
}

const openEditAccount = (acc) => {
  accountForm.value = { ...acc }
  editingAccount.value = acc
  showAccountForm.value = true
}

const saveAccount = async () => {
  if (!accountForm.value.name.trim()) return
  try {
    if (editingAccount.value) {
      await api.put(`/finance/accounts/${editingAccount.value.id}`, accountForm.value)
      showToast('✅ حساب بروزرسانی شد')
    } else {
      await api.post('/finance/accounts', accountForm.value)
      showToast('✅ حساب جدید ایجاد شد')
    }
    showAccountForm.value = false
    await fetchAccounts()
  } catch (e) { showToast('❌ خطا', 'error') }
}

const deleteAccount = async (id) => {
  if (!confirm('حذف حساب یعنی همه تراکنش‌هاش هم حذف میشن. مطمئنی؟')) return
  try { await api.delete(`/finance/accounts/${id}`); showToast('🗑️ حساب حذف شد'); await fetchAccounts() } catch (e) {}
}

// ====== Transaction CRUD ======
const openNewTransaction = (acc) => {
  selectedAccount.value = acc
  selectedAccountId.value = acc.id
  transactionForm.value = { 
    transaction_date: new Date().toISOString().split('T')[0], 
    transaction_type: 'deposit', 
    amount: 0, 
    description: '' 
  }
  showTransactionForm.value = true
}

const saveTransaction = async () => {
  if (!transactionForm.value.amount || transactionForm.value.amount <= 0) return
  try {
    await api.post(`/finance/accounts/${selectedAccountId.value}/transactions`, transactionForm.value)
    showToast('✅ تراکنش ثبت شد')
    showTransactionForm.value = false
    selectedAccount.value = null
    await fetchAccounts()
  } catch (e) { showToast('❌ خطا', 'error') }
}


const deleteTransaction = async (transId) => {
  if (!confirm('حذف تراکنش؟')) return
  try { await api.delete(`/finance/transactions/${transId}`); showToast('🗑️ تراکنش حذف شد'); await fetchAccounts() } catch (e) {}
}

const formatMoney = (amount) => {
  return Number(amount).toLocaleString('fa-IR') + ' تومان'
}

onMounted(fetchAccounts)
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen">
    
    <!-- Toast -->
    <div v-if="message" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold transition-all duration-300"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-extrabold mb-1" :class="themeStore.currentTheme === 'cyber-digital' ? 'neon-text' : ''" :style="{ color: 'var(--text-primary)' }">مدیریت مالی</h1>
        <p :style="{ color: 'var(--text-secondary)' }">حساب‌ها و تراکنش‌های مالی</p>
      </div>
      <button @click="openNewAccount" class="px-5 py-2.5 rounded-xl text-white font-semibold transition flex items-center gap-2" :style="{ background: 'var(--accent)' }">
        <Plus class="w-5 h-5" /> حساب جدید
      </button>
    </div>

    <!-- مجموع موجودی -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <p class="text-sm mb-2" :style="{ color: 'var(--text-secondary)' }">مجموع موجودی</p>
        <p class="text-3xl font-extrabold" :style="{ color: 'var(--accent)' }">
          {{ formatMoney(accounts.reduce((sum, a) => sum + a.current_balance, 0)) }}
        </p>
      </div>
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <p class="text-sm mb-2" :style="{ color: 'var(--text-secondary)' }">تعداد حساب‌ها</p>
        <p class="text-3xl font-extrabold" :style="{ color: 'var(--text-primary)' }">{{ accounts.length }}</p>
      </div>
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <p class="text-sm mb-2" :style="{ color: 'var(--text-secondary)' }">کل تراکنش‌ها</p>
        <p class="text-3xl font-extrabold" :style="{ color: 'var(--text-primary)' }">{{ accounts.reduce((sum, a) => sum + (a.transaction_count || 0), 0) }}</p>
      </div>
    </div>

    <!-- لیست حساب‌ها -->
    <div v-if="accounts.length === 0" class="text-center py-20">
      <Wallet class="w-16 h-16 mx-auto mb-4" :style="{ color: 'var(--accent)' }" />
      <p class="text-xl font-bold mb-2" :style="{ color: 'var(--text-primary)' }">هنوز حسابی ثبت نکردی!</p>
      <p :style="{ color: 'var(--text-secondary)' }">اولین حساب بانکی رو اضافه کن.</p>
    </div>

    <div class="space-y-6">
      <div v-for="acc in accounts" :key="acc.id" class="rounded-2xl overflow-hidden" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        
        <!-- هدر حساب -->
        <div @click="openNewTransaction(acc)" class="p-6 flex items-center justify-between cursor-pointer hover:bg-white/[0.02] transition">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center" :style="{ background: 'var(--accent)' }">
              <CreditCard class="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ acc.name }}</h3>
              <div class="flex gap-3 text-xs" :style="{ color: 'var(--text-secondary)' }">
                <span v-if="acc.bank_name">{{ acc.bank_name }}</span>
                <span v-if="acc.sheba_number">شبا: {{ acc.sheba_number }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <div class="text-left">
              <p class="text-xs" :style="{ color: 'var(--text-secondary)' }">موجودی</p>
              <p class="text-xl font-extrabold" :style="{ color: acc.current_balance >= 0 ? '#22c55e' : '#ef4444' }">
                {{ formatMoney(acc.current_balance) }}
              </p>
            </div>
            <div class="flex gap-1">
              <button @click="openNewTransaction(acc)" class="p-2 rounded-lg transition" :style="{ background: 'var(--accent)', color: '#fff' }" title="تراکنش جدید">
                <Plus class="w-4 h-4" />
              </button>
              <button @click="openEditAccount(acc)" class="p-2 rounded-lg hover:bg-white/10 transition" :style="{ color: 'var(--text-secondary)' }">
                <Edit3 class="w-4 h-4" />
              </button>
              <button @click="deleteAccount(acc.id)" class="p-2 rounded-lg hover:bg-red-500/10 transition" :style="{ color: 'var(--text-secondary)' }">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- تراکنش‌ها -->
        <div v-if="acc.transactions && acc.transactions.length > 0" class="border-t" :style="{ borderColor: 'var(--border)' }">
          <div class="px-6 py-2 text-xs font-bold" :style="{ color: 'var(--text-secondary)', background: 'var(--bg-hover)' }">
            تراکنش‌ها ({{ acc.transaction_count }})
          </div>
          <div class="divide-y" :style="{ borderColor: 'var(--border)' }">
            <div v-for="trans in acc.transactions?.slice(0, 10)" :key="trans.id" 
                 class="flex items-center justify-between px-6 py-3 text-sm hover:bg-white/[0.02] transition">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center"
                     :style="{ background: trans.transaction_type === 'deposit' ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)' }">
                  <ArrowUp v-if="trans.transaction_type === 'deposit'" class="w-4 h-4 text-green-500" />
                  <ArrowDown v-else class="w-4 h-4 text-red-400" />
                </div>
                <div>
                  <p :style="{ color: 'var(--text-primary)' }">{{ trans.description || (trans.transaction_type === 'deposit' ? 'واریز' : 'برداشت') }}</p>
                  <p class="text-xs" :style="{ color: 'var(--text-secondary)' }">{{ trans.transaction_date }}</p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <div class="text-left">
                  <p class="font-bold" :style="{ color: trans.transaction_type === 'deposit' ? '#22c55e' : '#ef4444' }">
                    {{ trans.transaction_type === 'deposit' ? '+' : '-' }}{{ formatMoney(trans.amount) }}
                  </p>
                  <p class="text-xs text-left" :style="{ color: 'var(--text-secondary)' }">مانده: {{ formatMoney(trans.balance_after) }}</p>
                </div>
                <button @click="deleteTransaction(trans.id)" class="p-1 rounded hover:bg-red-500/10 opacity-0 hover:opacity-100 transition" :style="{ color: 'var(--text-secondary)' }">
                  <Trash2 class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== مودال حساب ========== -->
    <div v-if="showAccountForm" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="showAccountForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ editingAccount ? 'ویرایش حساب' : 'حساب جدید' }}</h3>
          <button @click="showAccountForm = false" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۱- تاریخ ثبت</label>
            <input v-model="accountForm.register_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۲- نام حساب *</label>
            <input v-model="accountForm.name" placeholder="مثلاً: حساب جاری ملت" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۳- بانک صادر کننده</label>
            <input v-model="accountForm.bank_name" placeholder="مثلاً: بانک ملت" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۴- شماره شبا</label>
            <input v-model="accountForm.sheba_number" placeholder="IR..." class="w-full px-3 py-2.5 rounded-lg text-left" dir="ltr" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۵- آخرین موجودی (تومان)</label>
            <input v-model.number="accountForm.current_balance" type="number" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="saveAccount" class="flex-1 py-2.5 rounded-xl text-white font-semibold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showAccountForm = false" class="px-4 py-2.5 rounded-xl" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>

    <!-- ========== مودال تراکنش ========== -->
    <div v-if="showTransactionForm" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="showTransactionForm = false">
      <div class="w-full max-w-md rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">تراکنش جدید</h3>
          <p class="text-sm mb-2" :style="{ color: 'var(--accent)' }" v-if="selectedAccount">
  حساب: {{ selectedAccount.name }} | موجودی فعلی: {{ formatMoney(selectedAccount.current_balance) }}
</p>
          <button @click="showTransactionForm = false" :style="{ color: 'var(--text-secondary)' }"><X class="w-5 h-5" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۱- تاریخ تراکنش</label>
            <input v-model="transactionForm.transaction_date" type="date" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۲- نوع تراکنش</label>
            <div class="flex gap-2">
              <button @click="transactionForm.transaction_type = 'deposit'"
                      class="flex-1 py-2.5 rounded-lg font-semibold transition flex items-center justify-center gap-2"
                      :style="transactionForm.transaction_type === 'deposit' ? { background: '#22c55e', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
                <ArrowUp class="w-4 h-4" /> واریز
              </button>
              <button @click="transactionForm.transaction_type = 'withdrawal'"
                      class="flex-1 py-2.5 rounded-lg font-semibold transition flex items-center justify-center gap-2"
                      :style="transactionForm.transaction_type === 'withdrawal' ? { background: '#ef4444', color: '#fff' } : { background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">
                <ArrowDown class="w-4 h-4" /> برداشت
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۳- مبلغ (تومان)</label>
            <input v-model.number="transactionForm.amount" type="number" class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="block text-sm mb-1" :style="{ color: 'var(--text-secondary)' }">۴- توضیحات</label>
            <input v-model="transactionForm.description" placeholder="بابت..." class="w-full px-3 py-2.5 rounded-lg" :style="{ background: 'var(--bg-primary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div v-if="selectedAccount" class="p-3 rounded-lg" :style="{ background: 'var(--bg-hover)' }">
  <p class="text-sm" :style="{ color: 'var(--text-secondary)' }">۵- مانده حساب پس از تراکنش:</p>
  <p class="text-lg font-extrabold" :style="{ color: (selectedAccount.current_balance + (transactionForm.transaction_type === 'deposit' ? transactionForm.amount : -transactionForm.amount)) >= 0 ? '#22c55e' : '#ef4444' }">
    {{ formatMoney(selectedAccount.current_balance + (transactionForm.transaction_type === 'deposit' ? transactionForm.amount : -transactionForm.amount)) }}
  </p>
</div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="saveTransaction" class="flex-1 py-2.5 rounded-xl text-white font-semibold" :style="{ background: 'var(--accent)' }">ثبت تراکنش</button>
          <button @click="showTransactionForm = false" class="px-4 py-2.5 rounded-xl" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>

  </div>
</template>