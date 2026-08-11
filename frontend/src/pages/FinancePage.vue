<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  Plus, Trash2, Edit3, X, Wallet, CreditCard, ArrowUp, ArrowDown, 
  ChevronDown, ChevronUp, ShoppingBag, Utensils, Car, Home, HeartPulse, 
  Smartphone, Gift, Landmark, Briefcase, HelpCircle, Package, ReceiptText,
  Building2, TrendingUp
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
  <div class="relative min-h-screen text-right p-6 md:p-10 overflow-hidden" dir="rtl">
    
    <!-- ۱. پس‌زمینه ثابت مرکز مالی و بانکی مدرن (شفاف و 4K) -->
    <div class="fixed inset-0 z-0 bg-cover bg-center"
         style="background-image: url('https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=2560&q=90');">
      <div class="absolute inset-0 bg-black/35"></div>
    </div>

    <!-- ۲. محتوای اصلی روی لایه شیشه‌ای -->
    <div class="relative z-10 max-w-7xl mx-auto space-y-8 text-white">

      <!-- Toast -->
      <div v-if="message" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-[500] px-6 py-3 rounded-xl shadow-2xl text-white font-semibold"
           :style="{ background: messageType === 'error' ? '#ef4444' : 'var(--accent)' }">
        {{ message }}
      </div>

      <!-- هدر صفحه -->
      <div class="flex items-center justify-between p-6 rounded-3xl bg-black/40 backdrop-blur-md border border-white/10 shadow-2xl">
        <div>
          <h1 class="text-3xl font-black mb-1 drop-shadow-md">مدیریت امور مالی</h1>
          <p class="text-xs opacity-70">کنترل موجودی، حساب‌های بانکی و تراکنش‌ها</p>
        </div>
        <button @click="openNewAccount" class="px-5 py-3 rounded-2xl font-bold text-white transition flex items-center gap-2 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
          <Plus class="w-5 h-5" /> تعریف حساب جدید
        </button>
      </div>

      <!-- داشبورد دارایی و موجودی -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center"><Wallet class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">مجموع کل دارایی شما</p>
            <p class="text-2xl font-black text-emerald-400">
              {{ formatMoney(accounts.reduce((sum, a) => sum + a.current_balance, 0)) }}
            </p>
          </div>
        </div>

        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center"><Building2 class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">تعداد حساب‌های فعال</p>
            <p class="text-2xl font-black">{{ accounts.length }} حساب</p>
          </div>
        </div>

        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-purple-500/20 text-purple-400 flex items-center justify-center"><TrendingUp class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">کل تراکنش‌های ثبت‌شده</p>
            <p class="text-2xl font-black">{{ accounts.reduce((sum, a) => sum + (a.transaction_count || 0), 0) }} مورد</p>
          </div>
        </div>
      </div>

      <!-- لیست حساب‌ها -->
      <div v-if="accounts.length === 0" class="text-center py-20 opacity-40">
        <Wallet class="w-16 h-16 mx-auto mb-4" />
        <p class="text-lg font-bold">هیچ حسابی تعریف نشده است</p>
      </div>

      <div class="space-y-6">
        <div v-for="acc in accounts" :key="acc.id" class="rounded-3xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-300">
          
          <!-- هدر حساب بانکی -->
          <div class="p-6 flex items-center justify-between">
            <div class="flex items-center gap-4 cursor-pointer" @click="toggleTransactions(acc.id)">
              <div class="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center shadow-inner">
                <CreditCard class="w-6 h-6 text-amber-400" />
              </div>
              <div>
                <h3 class="text-lg font-black">{{ acc.name }}</h3>
                <p class="text-xs opacity-60">{{ acc.bank_name || 'بانک نامشخص' }} <span v-if="acc.sheba_number" dir="ltr" class="mr-2">| {{ acc.sheba_number }}</span></p>
              </div>
            </div>

            <div class="flex items-center gap-6">
              <div class="text-left">
                <p class="text-[10px] opacity-50 uppercase">موجودی فعلی</p>
                <p class="text-xl font-black" :class="acc.current_balance >= 0 ? 'text-emerald-400' : 'text-red-400'">
                  {{ formatMoney(acc.current_balance) }}
                </p>
              </div>

              <div class="flex gap-2">
                <button @click="openNewTransaction(acc)" class="p-2.5 rounded-xl text-white font-bold transition shadow-md hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }" title="تراکنش جدید">
                  <Plus class="w-5 h-5" />
                </button>
                <button @click="toggleTransactions(acc.id)" class="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition">
                  <ChevronUp v-if="expandedAccounts[acc.id]" class="w-5 h-5" />
                  <ChevronDown v-else class="w-5 h-5" />
                </button>
                <button @click="openEditAccount(acc)" class="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition"><Edit3 class="w-5 h-5" /></button>
                <button @click="deleteAccount(acc.id)" class="p-2.5 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition"><Trash2 class="w-5 h-5" /></button>
              </div>
            </div>
          </div>

          <!-- لیست تراکنش‌های زیرمجموعه -->
          <div v-if="expandedAccounts[acc.id]" class="border-t border-white/10 animate-in fade-in duration-300">
            <div v-if="acc.transactions && acc.transactions.length > 0" class="divide-y divide-white/10">
              <div v-for="trans in acc.transactions" :key="trans.id" class="flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] group">
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 rounded-2xl flex items-center justify-center shadow-inner"
                       :style="{ background: trans.transaction_type === 'deposit' ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)' }">
                    <component :is="getCategoryIcon(trans.category)" class="w-5 h-5" :style="{ color: getCategoryColor(trans.category) }" />
                  </div>
                  <div>
                    <p class="font-bold text-sm">{{ trans.description || (trans.transaction_type === 'deposit' ? 'واریز به حساب' : 'برداشت از حساب') }}</p>
                    <p v-if="trans.items" class="text-[11px] opacity-60">اقلام: {{ trans.items }}</p>
                  </div>
                </div>
                
                <div class="flex items-center gap-6">
                  <div class="text-left">
                    <p class="font-black text-base" :class="trans.transaction_type === 'deposit' ? 'text-emerald-400' : 'text-red-400'">
                      {{ trans.transaction_type === 'deposit' ? '+' : '-' }} {{ formatMoney(trans.amount) }}
                    </p>
                    <p class="text-[10px] text-left opacity-40">مانده: {{ formatMoney(trans.balance_after) }} | {{ formatDate(trans.transaction_date) }}</p>
                  </div>
                  <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openEditTransaction(acc, trans)" class="p-1.5 rounded-lg hover:bg-white/10"><Edit3 class="w-4 h-4" /></button>
                    <button @click="deleteTransaction(trans.id)" class="p-1.5 rounded-lg hover:bg-red-500/20 text-red-400"><Trash2 class="w-4 h-4" /></button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="p-8 text-center opacity-40">تراکنشی برای این حساب ثبت نشده است.</div>
          </div>

        </div>
      </div>

      <!-- ========== مودال حساب ========== -->
      <div v-if="showAccountForm" class="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" @click.self="showAccountForm = false">
        <div class="w-full max-w-md rounded-3xl p-8 bg-gray-900 border border-white/10 shadow-2xl text-white space-y-4">
          <h3 class="text-xl font-black mb-6">{{ editingAccount ? 'ویرایش اطلاعات حساب' : 'تعریف حساب جدید' }}</h3>
          <div class="space-y-4 text-right" dir="rtl">
            <div>
              <label class="text-xs mb-1 block opacity-70">نام حساب (اجباری) *</label>
              <input v-model="accountForm.name" placeholder="مثلاً: کارت اصلی ملت" class="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>
            <div>
              <label class="text-xs mb-1 block opacity-70">نام بانک</label>
              <input v-model="accountForm.bank_name" placeholder="مثلاً: بانک پاسارگاد" class="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>
            <div>
              <label class="text-xs mb-1 block opacity-70">شماره شبا</label>
              <input v-model="accountForm.sheba_number" placeholder="IR..." dir="ltr" class="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>
            <div>
              <label class="text-xs mb-1 block opacity-70">موجودی اولیه (تومان)</label>
              <input :value="formatNumber(accountForm.current_balance)" @input="accountForm.current_balance = parseNumber($event.target.value)" class="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-lg font-bold text-emerald-400" />
              <p class="text-[10px] mt-1 text-emerald-300 font-medium pr-1">{{ numberToPersianWords(parseNumber(accountForm.current_balance)) }}</p>
            </div>
            <div>
              <label class="text-xs mb-1 block opacity-70">تاریخ ثبت/افتتاح</label>
              <DateInputPersian v-model="accountForm.register_date" />
            </div>
          </div>
          <div class="flex gap-3 mt-8">
            <button @click="saveAccount" class="flex-1 py-3.5 rounded-2xl text-white font-bold shadow-lg shadow-emerald-500/20" :style="{ background: 'var(--accent)' }">ذخیره حساب</button>
            <button @click="showAccountForm = false" class="px-6 py-3.5 rounded-2xl font-semibold bg-white/10 hover:bg-white/20">انصراف</button>
          </div>
        </div>
      </div>

      <!-- ========== مودال تراکنش ========== -->
      <div v-if="showTransactionForm" class="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" @click.self="showTransactionForm = false">
        <div class="w-full max-w-lg rounded-3xl p-8 bg-gray-900 border border-white/10 shadow-2xl text-white space-y-4">
          <h3 class="text-xl font-black mb-1">{{ editingTransaction ? 'ویرایش تراکنش' : 'ثبت تراکنش جدید' }}</h3>
          <p class="text-xs opacity-60 mb-4">حساب: {{ selectedAccount?.name }}</p>

          <div class="space-y-4 text-right" dir="rtl">
            <div class="flex gap-2 p-1 rounded-2xl bg-black/40 border border-white/10">
              <button @click="transactionForm.transaction_type = 'withdrawal'; transactionForm.category=''"
                      class="flex-1 py-2.5 rounded-xl font-bold transition flex items-center justify-center gap-2 text-xs"
                      :style="transactionForm.transaction_type === 'withdrawal' ? { background: '#ef4444', color: '#fff' } : { color: 'var(--text-secondary)' }">
                <ArrowDown class="w-4 h-4" /> برداشت (هزینه)
              </button>
              <button @click="transactionForm.transaction_type = 'deposit'; transactionForm.category=''"
                      class="flex-1 py-2.5 rounded-xl font-bold transition flex items-center justify-center gap-2 text-xs"
                      :style="transactionForm.transaction_type === 'deposit' ? { background: '#22c55e', color: '#fff' } : { color: 'var(--text-secondary)' }">
                <ArrowUp class="w-4 h-4" /> واریز (درآمد)
              </button>
            </div>

            <div>
              <label class="text-xs mb-2 block opacity-70">انتخاب دسته‌بندی *</label>
              <div class="grid grid-cols-4 gap-2">
                <button v-for="cat in categories[transactionForm.transaction_type]" :key="cat.id" 
                        @click="transactionForm.category = cat.id"
                        class="flex flex-col items-center p-2 rounded-2xl border border-white/10 transition-all hover:scale-105"
                        :style="transactionForm.category === cat.id ? { borderColor: cat.color, background: cat.color + '25' } : { background: 'rgba(255,255,255,0.03)' }">
                  <component :is="cat.icon" class="w-5 h-5 mb-1" :style="{ color: cat.color }" />
                  <span class="text-[9px] text-center opacity-80">{{ cat.name }}</span>
                </button>
              </div>
            </div>

            <div>
              <label class="text-xs mb-1 block opacity-70">مبلغ (تومان) *</label>
              <input :value="formatNumber(transactionForm.amount)" @input="transactionForm.amount = parseNumber($event.target.value)" 
                     class="w-full px-4 py-3.5 rounded-2xl border border-white/10 bg-black/40 font-black text-2xl text-center outline-none" 
                     :style="{ color: transactionForm.transaction_type === 'deposit' ? '#22c55e' : '#ef4444' }" />
              <p class="text-xs mt-1 text-center font-bold text-emerald-400">{{ numberToPersianWords(parseNumber(transactionForm.amount)) }}</p>
            </div>

            <div v-if="transactionForm.transaction_type === 'withdrawal'">
              <label class="text-xs mb-1 block opacity-70">اقلام خرید</label>
              <input v-model="transactionForm.items" placeholder="مثلاً: شیر، نان، میوه..." class="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>

            <div>
              <label class="text-xs mb-1 block opacity-70">توضیحات</label>
              <input v-model="transactionForm.description" placeholder="بابتِ..." class="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm" />
            </div>

            <div>
              <label class="text-xs mb-1 block opacity-70">تاریخ تراکنش</label>
              <DateInputPersian v-model="transactionForm.transaction_date" />
            </div>
          </div>

          <div class="flex gap-3 mt-6">
            <button @click="saveTransaction" class="flex-1 py-3.5 rounded-2xl text-white font-bold shadow-lg" :style="{ background: 'var(--accent)' }">ثبت نهایی</button>
            <button @click="showTransactionForm = false" class="px-6 py-3.5 rounded-2xl font-semibold bg-white/10 hover:bg-white/20">انصراف</button>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>