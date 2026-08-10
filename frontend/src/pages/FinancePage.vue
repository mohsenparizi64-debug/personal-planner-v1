<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, X, Wallet, CreditCard, ArrowUp, ArrowDown, 
  ChevronDown, ChevronUp, ShoppingBag, Utensils, Car, Home, HeartPulse, 
  Smartphone, Gift, Landmark, Briefcase, HelpCircle, Package, ReceiptText
} from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const accounts = ref([])
const message = ref('')
const messageType = ref('success')
const expandedAccounts = ref({})

// دسته‌بندی‌های پیش‌فرض
const categories = {
  withdrawal: [
    { id: 'food', name: 'خوراک و رستوران', icon: Utensils, color: '#f97316' },
    { id: 'transport', name: 'حمل و نقل / خودرو', icon: Car, color: '#3b82f6' },
    { id: 'home', name: 'اجاره و قبوض', icon: Home, color: '#8b5cf6' },
    { id: 'shopping', name: 'خرید لباس و کالا', icon: ShoppingBag, color: '#ec4899' },
    { id: 'health', name: 'سلامت و درمان', icon: HeartPulse, color: '#ef4444' },
    { id: 'digital', name: 'اشتراک و ابزار دیجیتال', icon: Smartphone, color: '#06b6d4' },
    { id: 'loan', name: 'قسط و بدهی', icon: Landmark, color: '#64748b' },
    { id: 'other_out', name: 'سایر هزینه‌ها', icon: HelpCircle, color: '#94a3b8' },
  ],
  deposit: [
    { id: 'salary', name: 'حقوق و دستمزد', icon: Briefcase, color: '#22c55e' },
    { id: 'gift', name: 'هدیه / جایزه', icon: Gift, color: '#eab308' },
    { id: 'selling', name: 'فروش کالا', icon: Package, color: '#10b981' },
    { id: 'other_in', name: 'سایر درآمدها', icon: Landmark, color: '#14b8a6' },
  ]
}

// فرم‌ها و وضعیت‌ها
const showAccountForm = ref(false)
const editingAccount = ref(null)
const accountForm = ref({ name: '', bank_name: '', sheba_number: '', current_balance: 0, register_date: new Date().toISOString().split('T')[0] })

const showTransactionForm = ref(false)
const editingTransaction = ref(null)
const selectedAccountId = ref(null)
const selectedAccount = ref(null)
const transactionForm = ref({ 
  transaction_date: new Date().toISOString().split('T')[0], 
  transaction_type: 'withdrawal', 
  amount: 0, 
  category: '', 
  items: '', 
  description: '' 
})

const errors = ref({ amount: false, category: false, name: false })

// تابع تبدیل عدد به حروف فارسی (تومان)
const numberToPersianWords = (num) => {
  if (!num || num === 0) return '';
  const units = ['', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه'];
  const teens = ['ده', 'یازده', 'دوازده', 'سیزده', 'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده'];
  const tens = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود'];
  const hundreds = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پانصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد'];
  
  const convertChunk = (n) => {
    let res = '';
    if (n >= 100) { res += hundreds[Math.floor(n / 100)] + ' و '; n %= 100; }
    if (n >= 20) { res += tens[Math.floor(n / 10)] + ' و '; n %= 10; }
    else if (n >= 10) { res += teens[n - 10] + ' و '; n = 0; }
    if (n > 0) { res += units[n] + ' و '; }
    return res.endsWith(' و ') ? res.slice(0, -3) : res;
  };

  let n = Math.abs(num);
  let result = '';
  if (n >= 1000000000) { result += convertChunk(Math.floor(n / 1000000000)) + ' میلیارد و '; n %= 1000000000; }
  if (n >= 1000000) { result += convertChunk(Math.floor(n / 1000000)) + ' میلیون و '; n %= 1000000; }
  if (n >= 1000) { result += convertChunk(Math.floor(n / 1000)) + ' هزار و '; n %= 1000; }
  if (n > 0) { result += convertChunk(n); }
  
  if (result.endsWith(' و ')) result = result.slice(0, -3);
  return result + ' تومان';
}

const formatNumber = (val) => {
  if (val === undefined || val === null || val === "") return "";
  return String(val).replace(/\D/g, "").replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

const parseNumber = (val) => {
  if (typeof val === 'number') return val;
  return Number(String(val).replace(/,/g, '')) || 0;
};

const showToast = (msg, type = 'success') => {
  message.value = msg; messageType.value = type
  setTimeout(() => message.value = '', 3000)
}

const fetchAccounts = async () => {
  try { const res = await api.get('/finance/accounts'); accounts.value = res.data; } catch (e) {}
}

const toggleTransactions = (id) => expandedAccounts.value[id] = !expandedAccounts.value[id];

// ====== عملیات حساب (Account) ======
const openNewAccount = () => {
  accountForm.value = { name: '', bank_name: '', sheba_number: '', current_balance: 0, register_date: new Date().toISOString().split('T')[0] }
  editingAccount.value = null
  showAccountForm.value = true
}

const openEditAccount = (acc) => {
  accountForm.value = { ...acc, current_balance: acc.current_balance }
  editingAccount.value = acc
  showAccountForm.value = true
}

const saveAccount = async () => {
  if (!accountForm.value.name.trim()) { errors.value.name = true; return; }
  try {
    const payload = { ...accountForm.value, current_balance: parseNumber(accountForm.value.current_balance) };
    if (editingAccount.value) {
      await api.put(`/finance/accounts/${editingAccount.value.id}`, payload)
      showToast('✅ حساب بروزرسانی شد')
    } else {
      await api.post('/finance/accounts', payload)
      showToast('✅ حساب جدید ایجاد شد')
    }
    showAccountForm.value = false; await fetchAccounts()
  } catch (e) { showToast('❌ خطا در ذخیره حساب', 'error') }
}

const deleteAccount = async (id) => {
  if (!confirm('حذف حساب باعث حذف تمام تراکنش‌های آن می‌شود. آیا مطمئن هستید؟')) return
  try { await api.delete(`/finance/accounts/${id}`); showToast('🗑️ حساب حذف شد'); await fetchAccounts() } catch (e) {}
}

// ====== عملیات تراکنش (Transaction) ======
const openNewTransaction = (acc) => {
  selectedAccount.value = acc; selectedAccountId.value = acc.id
  editingTransaction.value = null
  transactionForm.value = { 
    transaction_date: new Date().toISOString().split('T')[0], 
    transaction_type: 'withdrawal', amount: 0, category: '', items: '', description: '' 
  }
  errors.value = { amount: false, category: false }
  showTransactionForm.value = true
}

const openEditTransaction = (acc, trans) => {
  selectedAccount.value = acc; selectedAccountId.value = acc.id
  editingTransaction.value = trans
  transactionForm.value = { ...trans }
  showTransactionForm.value = true
}

const saveTransaction = async () => {
  const amount = parseNumber(transactionForm.value.amount);
  errors.value.amount = amount <= 0;
  errors.value.category = !transactionForm.value.category;

  if (errors.value.amount || errors.value.category) {
    showToast('لطفاً فیلدهای اجباری را پر کنید', 'error'); return;
  }

  try {
    const payload = { ...transactionForm.value, amount: amount };
    if (editingTransaction.value) {
      await api.put(`/finance/transactions/${editingTransaction.value.id}`, payload)
      showToast('✅ تراکنش ویرایش شد')
    } else {
      await api.post(`/finance/accounts/${selectedAccountId.value}/transactions`, payload)
      showToast('✅ تراکنش ثبت شد')
    }
    showTransactionForm.value = false; await fetchAccounts()
  } catch (e) { showToast('❌ خطا در ثبت', 'error') }
}

const deleteTransaction = async (id) => {
  if (!confirm('آیا این تراکنش حذف شود؟')) return
  try { await api.delete(`/finance/transactions/${id}`); showToast('🗑️ حذف شد'); await fetchAccounts() } catch (e) {}
}

const getCategoryIcon = (catId) => {
  const all = [...categories.withdrawal, ...categories.deposit];
  return all.find(c => c.id === catId)?.icon || ReceiptText;
}

const getCategoryColor = (catId) => {
  const all = [...categories.withdrawal, ...categories.deposit];
  return all.find(c => c.id === catId)?.color || 'var(--text-secondary)';
}

const formatMoney = (amount) => formatNumber(Math.abs(amount)) + ' تومان';

onMounted(fetchAccounts)
</script>

<template>
  <div class="p-6 md:p-10 max-w-6xl mx-auto relative min-h-screen">
    
    <!-- Toast -->
    <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold"
         :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-extrabold mb-1" :style="{ color: 'var(--text-primary)' }">امور مالی</h1>
        <p :style="{ color: 'var(--text-secondary)' }">مدیریت درآمد و هزینه‌ها</p>
      </div>
      <button @click="openNewAccount" class="px-5 py-2.5 rounded-xl text-white font-semibold transition flex items-center gap-2 shadow-lg" :style="{ background: 'var(--accent)' }">
        <Plus class="w-5 h-5" /> حساب جدید
      </button>
    </div>

    <!-- Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <p class="text-sm mb-2 opacity-70" :style="{ color: 'var(--text-secondary)' }">کل دارایی نقد</p>
        <p class="text-2xl font-black" :style="{ color: 'var(--accent)' }">
          {{ formatMoney(accounts.reduce((sum, a) => sum + a.current_balance, 0)) }}
        </p>
      </div>
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <p class="text-sm mb-2 opacity-70" :style="{ color: 'var(--text-secondary)' }">تعداد حساب‌ها</p>
        <p class="text-2xl font-black" :style="{ color: 'var(--text-primary)' }">{{ accounts.length }}</p>
      </div>
      <div class="rounded-2xl p-6" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <p class="text-sm mb-2 opacity-70" :style="{ color: 'var(--text-secondary)' }">کل گردش حساب</p>
        <p class="text-2xl font-black" :style="{ color: 'var(--text-primary)' }">{{ accounts.reduce((sum, a) => sum + (a.transaction_count || 0), 0) }}</p>
      </div>
    </div>

    <!-- Accounts List -->
    <div class="space-y-6">
      <div v-for="acc in accounts" :key="acc.id" class="rounded-2xl overflow-hidden shadow-sm border" :style="{ background: 'var(--bg-card)', borderColor: 'var(--border)' }">
        <div class="p-6 flex items-center justify-between">
          <div class="flex items-center gap-4 cursor-pointer" @click="toggleTransactions(acc.id)">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center" :style="{ background: 'var(--bg-primary)' }">
              <CreditCard class="w-6 h-6" :style="{ color: 'var(--accent)' }" />
            </div>
            <div>
              <h3 class="text-lg font-bold" :style="{ color: 'var(--text-primary)' }">{{ acc.name }}</h3>
              <p class="text-xs opacity-70" :style="{ color: 'var(--text-secondary)' }">{{ acc.bank_name || 'بدون نام بانک' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-left">
              <p class="text-[10px] uppercase opacity-50 text-left" :style="{ color: 'var(--text-secondary)' }">موجودی</p>
              <p class="text-lg font-black" :style="{ color: acc.current_balance >= 0 ? '#22c55e' : '#ef4444' }">{{ formatMoney(acc.current_balance) }}</p>
            </div>
            <div class="flex gap-2">
              <button @click="openNewTransaction(acc)" class="p-2 rounded-lg text-white shadow-md" :style="{ background: 'var(--accent)' }"><Plus class="w-5 h-5" /></button>
              <button @click="openEditAccount(acc)" class="p-2 rounded-lg hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-4 h-4" /></button>
              <button @click="deleteAccount(acc.id)" class="p-2 rounded-lg hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-4 h-4" /></button>
              <button @click="toggleTransactions(acc.id)" class="p-2 rounded-lg hover:bg-white/10" :style="{ color: 'var(--text-secondary)' }">
                <ChevronUp v-if="expandedAccounts[acc.id]" /> <ChevronDown v-else />
              </button>
            </div>
          </div>
        </div>

        <!-- Transactions Inside Account -->
        <div v-if="expandedAccounts[acc.id]" class="border-t animate-in slide-in-from-top duration-300" :style="{ borderColor: 'var(--border)' }">
          <div v-if="acc.transactions?.length > 0" class="divide-y" :style="{ borderColor: 'var(--border)' }">
            <div v-for="trans in acc.transactions" :key="trans.id" class="flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] group">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-full flex items-center justify-center shadow-inner" 
                     :style="{ background: trans.transaction_type === 'deposit' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)' }">
                  <component :is="getCategoryIcon(trans.category)" class="w-5 h-5" :style="{ color: getCategoryColor(trans.category) }" />
                </div>
                <div>
                  <p class="font-bold text-sm" :style="{ color: 'var(--text-primary)' }">{{ trans.description || 'تراکنش بانکی' }}</p>
                  <p v-if="trans.items" class="text-[10px] opacity-60" :style="{ color: 'var(--text-secondary)' }">اقلام: {{ trans.items }}</p>
                </div>
              </div>
              <div class="flex items-center gap-6">
                <div class="text-left">
                  <p class="font-black" :style="{ color: trans.transaction_type === 'deposit' ? '#22c55e' : '#ef4444' }">
                    {{ trans.transaction_type === 'deposit' ? '+' : '-' }} {{ formatMoney(trans.amount) }}
                  </p>
                  <p class="text-[10px] opacity-50 text-left">{{ formatDate(trans.transaction_date) }}</p>
                </div>
                <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="openEditTransaction(acc, trans)" class="p-1.5 rounded hover:bg-blue-500/10" :style="{ color: 'var(--text-secondary)' }"><Edit3 class="w-4 h-4" /></button>
                  <button @click="deleteTransaction(trans.id)" class="p-1.5 rounded hover:bg-red-500/10" :style="{ color: 'var(--text-secondary)' }"><Trash2 class="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center opacity-40" :style="{ color: 'var(--text-secondary)' }">تراکنشی یافت نشد.</div>
        </div>
      </div>
    </div>

    <!-- Modal: Account -->
    <div v-if="showAccountForm" class="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md" @click.self="showAccountForm = false">
      <div class="w-full max-w-md rounded-3xl p-8 shadow-2xl" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <h3 class="text-xl font-black mb-6" :style="{ color: 'var(--text-primary)' }">{{ editingAccount ? 'ویرایش حساب' : 'حساب جدید' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="text-xs mb-1.5 block opacity-70" :style="{ color: 'var(--text-secondary)' }">نام حساب *</label>
            <input v-model="accountForm.name" placeholder="مثلاً: کارت اصلی" class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: errors.name ? '#ef4444' : 'var(--border)', color: 'var(--text-primary)' }" @input="errors.name=false" />
          </div>
          <div>
            <label class="text-xs mb-1.5 block opacity-70" :style="{ color: 'var(--text-secondary)' }">نام بانک</label>
            <input v-model="accountForm.bank_name" placeholder="مثلاً: ملت" class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
          </div>
          <div>
            <label class="text-xs mb-1.5 block opacity-70" :style="{ color: 'var(--text-secondary)' }">موجودی فعلی (تومان)</label>
            <input :value="formatNumber(accountForm.current_balance)" @input="accountForm.current_balance = parseNumber($event.target.value)" class="w-full px-4 py-3 rounded-xl border font-bold text-lg" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--accent)' }" />
            <p class="text-[10px] mt-1 pr-1 opacity-70" :style="{ color: 'var(--text-secondary)' }">{{ numberToPersianWords(parseNumber(accountForm.current_balance)) }}</p>
          </div>
          <div>
            <label class="text-xs mb-1.5 block opacity-70" :style="{ color: 'var(--text-secondary)' }">تاریخ افتتاح</label>
            <DateInputPersian v-model="accountForm.register_date" />
          </div>
        </div>
        <div class="flex gap-3 mt-8">
          <button @click="saveAccount" class="flex-1 py-3.5 rounded-2xl text-white font-bold" :style="{ background: 'var(--accent)' }">ذخیره</button>
          <button @click="showAccountForm = false" class="px-6 py-3.5 rounded-2xl font-semibold" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>

    <!-- Modal: Transaction -->
    <div v-if="showTransactionForm" class="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md" @click.self="showTransactionForm = false">
      <div class="w-full max-w-lg rounded-3xl p-8 max-h-[90vh] overflow-y-auto shadow-2xl" :style="{ background: 'var(--bg-card)', border: '1px solid var(--border)' }">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-black" :style="{ color: 'var(--text-primary)' }">ثبت تراکنش ({{ selectedAccount?.name }})</h3>
          <button @click="showTransactionForm = false" :style="{ color: 'var(--text-secondary)' }"><X /></button>
        </div>

        <div class="space-y-5">
          <div class="flex gap-2 p-1 rounded-2xl" :style="{ background: 'var(--bg-primary)' }">
            <button @click="transactionForm.transaction_type = 'withdrawal'; transactionForm.category=''" class="flex-1 py-3 rounded-xl font-bold transition flex items-center justify-center gap-2" :style="transactionForm.transaction_type === 'withdrawal' ? { background: '#ef4444', color: '#fff' } : { color: 'var(--text-secondary)' }"> <ArrowDown class="w-4 h-4"/> هزینه </button>
            <button @click="transactionForm.transaction_type = 'deposit'; transactionForm.category=''" class="flex-1 py-3 rounded-xl font-bold transition flex items-center justify-center gap-2" :style="transactionForm.transaction_type === 'deposit' ? { background: '#22c55e', color: '#fff' } : { color: 'var(--text-secondary)' }"> <ArrowUp class="w-4 h-4"/> درآمد </button>
          </div>

          <div>
            <label class="text-xs mb-2 block opacity-70" :style="{ color: errors.category ? '#ef4444' : 'var(--text-secondary)' }">انتخاب دسته‌بندی *</label>
            <div class="grid grid-cols-4 gap-2">
              <button v-for="cat in categories[transactionForm.transaction_type]" :key="cat.id" 
                      @click="transactionForm.category = cat.id; errors.category = false"
                      class="flex flex-col items-center p-2 rounded-xl border transition-all"
                      :style="transactionForm.category === cat.id ? { borderColor: cat.color, background: cat.color + '15' } : { borderColor: 'var(--border)', background: 'transparent' }">
                <component :is="cat.icon" class="w-6 h-6 mb-1" :style="{ color: cat.color }" />
                <span class="text-[9px] text-center" :style="{ color: 'var(--text-primary)' }">{{ cat.name }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="text-xs mb-1 block" :style="{ color: errors.amount ? '#ef4444' : 'var(--text-secondary)' }">مبلغ (تومان) *</label>
            <input :value="formatNumber(transactionForm.amount)" @input="transactionForm.amount = $event.target.value; errors.amount = false" 
                   class="w-full px-4 py-4 rounded-xl border font-black text-2xl text-center outline-none focus:ring-2" 
                   :style="{ background: 'var(--bg-primary)', borderColor: errors.amount ? '#ef4444' : 'var(--border)', color: 'var(--text-primary)', '--tw-ring-color': 'var(--accent)' }" />
            <p class="text-xs mt-2 text-center font-medium" :style="{ color: 'var(--accent)' }">{{ numberToPersianWords(parseNumber(transactionForm.amount)) }}</p>
          </div>

          <div v-if="transactionForm.transaction_type === 'withdrawal'">
            <label class="text-xs mb-1 block opacity-70" :style="{ color: 'var(--text-secondary)' }">لیست اقلام خرید</label>
            <input v-model="transactionForm.items" placeholder="مثلاً: ماست، نان، میوه..." class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
          </div>

          <div>
            <label class="text-xs mb-1 block opacity-70" :style="{ color: 'var(--text-secondary)' }">توضیحات یا نام فروشگاه</label>
            <input v-model="transactionForm.description" placeholder="توضیح اختیاری..." class="w-full px-4 py-3 rounded-xl border outline-none" :style="{ background: 'var(--bg-primary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }" />
          </div>

          <div>
            <label class="text-xs mb-1 block opacity-70" :style="{ color: 'var(--text-secondary)' }">تاریخ تراکنش</label>
            <DateInputPersian v-model="transactionForm.transaction_date" />
          </div>
        </div>

        <div class="flex gap-3 mt-8">
          <button @click="saveTransaction" class="flex-1 py-4 rounded-2xl text-white font-bold text-lg shadow-lg" :style="{ background: 'var(--accent)' }">تایید نهایی</button>
          <button @click="showTransactionForm = false" class="px-6 py-4 rounded-2xl font-semibold" :style="{ background: 'var(--bg-hover)', color: 'var(--text-secondary)' }">انصراف</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.animate-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
</style>