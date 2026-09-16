<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import {
  Plus, Trash2, Edit3, X, Wallet, CreditCard, ArrowUp, ArrowDown,
  ChevronDown, ChevronUp, ShoppingBag, Utensils, Car, Home, HeartPulse,
  Smartphone, Gift, Landmark, Briefcase, HelpCircle, Package, ReceiptText,
  Building2, TrendingUp, BarChart2, PieChart, RefreshCw, Eye, EyeOff, Wrench,
  GraduationCap, Plane, PiggyBank
} from 'lucide-vue-next'
import api from '@/services/api'
import DateInputPersian from '@/components/DateInputPersian.vue'
import { formatDate } from '@/utils/date'

const themeStore = useThemeStore()
const isLight = computed(() => themeStore.currentTheme === 'light-2026')
// پالت خوانا در هر دو تم (روشن: تیره با کنتراست بالا)
const cEmerald = computed(() => isLight.value ? '#047857' : '#6ee7b7')
const cRose = computed(() => isLight.value ? '#b91c1c' : '#fca5a5')
const cBlue = computed(() => isLight.value ? '#1d4ed8' : '#93c5fd')
const cPurple = computed(() => isLight.value ? '#6d28d9' : '#c4b5fd')
const cAmber = computed(() => isLight.value ? '#b45309' : '#fcd34d')
const cMuted = computed(() => isLight.value ? '#334155' : 'rgba(255,255,255,0.7)')
const router = useRouter()
const goToAccount = (id) => router.push(`/finance/${id}`)
const accounts = ref([])
const message = ref('')
const messageType = ref('success')
const expandedAccounts = ref({})

// ====== محدوده تحلیل: همه / انتخاب چندحسابه ======
const selectedAccountIds = ref([])  // خالی = همه حساب‌های غیرمخفی
const isScopeAll = computed(() => selectedAccountIds.value.length === 0)
const scopeIds = computed(() => {
  if (isScopeAll.value) return accounts.value.filter(a => !a.is_hidden).map(a => a.id)
  return [...selectedAccountIds.value]
})
const toggleScopeAccount = (id) => {
  const i = selectedAccountIds.value.indexOf(id)
  if (i >= 0) selectedAccountIds.value.splice(i, 1)
  else selectedAccountIds.value.push(id)
}
const resetScope = () => { selectedAccountIds.value = [] }
const scopeLabel = computed(() => {
  if (isScopeAll.value) return 'همه حساب‌های قابل‌مشاهده'
  if (selectedAccountIds.value.length === 1) {
    return accounts.value.find(a => a.id === selectedAccountIds.value[0])?.name || '۱ حساب'
  }
  return `${selectedAccountIds.value.length} حساب انتخاب شده`
})
// جمع موجودی محدوده (مخفی‌ها فقط اگر صراحتاً انتخاب شده باشند)
const scopeTotalBalance = computed(() => {
  const ids = new Set(scopeIds.value)
  return accounts.value.filter(a => ids.has(a.id)).reduce((s, a) => s + (Number(a.current_balance) || 0), 0)
})
const hiddenCount = computed(() => accounts.value.filter(a => a.is_hidden).length)

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
    { id: 'services', name: 'خدمات و سرویس‌ها', icon: Wrench, color: '#38bdf8' },
    { id: 'education', name: 'آموزش و کتاب', icon: GraduationCap, color: '#a78bfa' },
    { id: 'leisure', name: 'تفریح و سفر', icon: Plane, color: '#fbbf24' },
    { id: 'saving', name: 'پس‌انداز و سرمایه‌گذاری', icon: PiggyBank, color: '#34d399' },
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
const accountForm = ref({ name: '', bank_name: '', sheba_number: '', current_balance: 0, is_hidden: false, register_date: new Date().toISOString().split('T')[0] })

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
  accountForm.value = { name: '', bank_name: '', sheba_number: '', current_balance: 0, is_hidden: false, register_date: new Date().toISOString().split('T')[0] }
  editingAccount.value = null
  showAccountForm.value = true
}

const openEditAccount = (acc) => {
  accountForm.value = { ...acc, current_balance: acc.current_balance, is_hidden: !!acc.is_hidden }
  editingAccount.value = acc
  showAccountForm.value = true
}

const saveAccount = async () => {
  if (!accountForm.value.name.trim()) { errors.value.name = true; return; }
  try {
    const payload = { ...accountForm.value, current_balance: parseNumber(accountForm.value.current_balance), is_hidden: !!accountForm.value.is_hidden };
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

const toggleHidden = async (acc) => {
  try {
    await api.put(`/finance/accounts/${acc.id}`, { is_hidden: !acc.is_hidden })
    showToast(acc.is_hidden ? '👁️ حساب قابل‌مشاهده شد' : '🙈 حساب مخفی شد (از جمع کل خارج شد)')
    await fetchAccounts()
  } catch (e) { showToast('❌ خطا در تغییر وضعیت', 'error') }
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

// ====== گزارش چند-بازه‌ای (با محدوده حساب) ======
const reportDays = ref(7)
const reportData = ref(null)
const reportLoading = ref(false)
const donutHover = ref(null)
const selectedReportDay = ref(null)  // روز انتخاب‌شده برای popup مرکزی

function openReportDay(day) {
  // toggle
  selectedReportDay.value = (selectedReportDay.value && selectedReportDay.value.date === day.date) ? null : day
}

async function fetchReport(days) {
  if (days) reportDays.value = days
  reportLoading.value = true
  try {
    let url = `/finance/recent-report?days=${reportDays.value}`
    if (!isScopeAll.value && selectedAccountIds.value.length > 0) {
      url += `&account_ids=${selectedAccountIds.value.join(',')}`
    }
    const res = await api.get(url)
    reportData.value = res.data
  } catch (e) {
    console.error('fetchReport error', e)
    reportData.value = null
  } finally {
    reportLoading.value = false
  }
}

// با تغییر محدوده حساب، گزارش تازه شود
watch(selectedAccountIds, () => { fetchReport() }, { deep: true })

const accountNameById = (id) => accounts.value.find(a => a.id === id)?.name || `#${id}`

const maxDailyAmount = computed(() => {
  if (!reportData.value?.daily_buckets) return 0
  return Math.max(
    1,
    ...reportData.value.daily_buckets.map(d => Math.max(d.deposit, d.withdraw))
  )
})

function barHeight(val) {
  if (!maxDailyAmount.value) return 0
  return Math.max(2, (val / maxDailyAmount.value) * 100)
}

// اندیس امروز در daily_buckets (برای ring طلایی مثل داشبورد)
const todayBucketIndex = computed(() => {
  if (!reportData.value?.daily_buckets) return -1
  const today = new Date().toISOString().split('T')[0]
  return reportData.value.daily_buckets.findIndex(d => d.date === today)
})

// نمایش شمسی بازه گزارش
const reportRangeDisplay = computed(() => {
  if (!reportData.value) return '—'
  const s = formatDate(reportData.value.range_start)
  const e = formatDate(reportData.value.range_end)
  return `از ${s} تا ${e}`
})

// برچسب زیر هر ستون: روزانه = شماره روز شمسی؛ هفتگی = شروع هفته شمسی
function bucketSubLabel(bucket) {
  if (!bucket) return ''
  if (reportData.value?.bucket === 'week') return formatDate(bucket.date)
  return shamsiDay(bucket.date)
}

// روز شمسی از تاریخ میلادی (فقط شماره روز)
function shamsiDay(isoDate) {
  if (!isoDate) return ''
  const s = formatDate(isoDate)
  if (!s) return ''
  // s = "۱۴۰۵/۰۶/۱۱" — آخرین بخش بعد از /
  const parts = s.split('/')
  return parts[parts.length - 1] || s
}

const donutSegments = computed(() => {
  if (!reportData.value?.category_breakdown) return []
  const total = reportData.value.summary.withdraw_total || 0
  if (total === 0) return []
  let offset = 0
  return reportData.value.category_breakdown.map(cat => {
    const pct = cat.amount / total
    const seg = {
      id: cat.id,
      amount: cat.amount,
      percent: pct * 100,
      color: getCategoryColor(cat.id),
      offset,
      length: pct * 100,
    }
    offset += pct * 100
    return seg
  })
})

function donutPath(seg) {
  // viewBox 36x36, radius 15.9155 (محیط = 100)
  // stroke-dashoffset منفی به سمت راست حرکت می‌کنه
  // ما چون RTL هستیم و می‌خواهیم از بالا شروع شه با offset 25
  // ساده‌سازی: فقط از بالا با چرخش
  return `${seg.length} ${100 - seg.length}`
}

function getCategoryById(id) {
  const all = [...categories.withdrawal, ...categories.deposit]
  return all.find(c => c.id === id) || { name: id, color: '#94a3b8' }
}

const showCategory = (cat) => {
  const meta = getCategoryById(cat.id)
  return { ...cat, name: meta.name, color: meta.color }
}

onMounted(() => {
  fetchAccounts()
  fetchReport(7)
})
</script>

<template>
  <div class="relative min-h-screen text-right p-3 sm:p-4 md:p-8 lg:p-10 overflow-hidden" dir="rtl">

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
      <div class="flex flex-wrap items-center justify-between gap-3 p-6 rounded-3xl bg-black/40 backdrop-blur-md border border-white/10 shadow-2xl">
        <div>
          <h1 class="text-3xl font-black mb-1 drop-shadow-md">مدیریت امور مالی</h1>
          <p class="text-xs opacity-70">کنترل موجودی، حساب‌های بانکی و تراکنش‌ها</p>
          <p class="text-xs mt-1.5 font-bold" :style="{ color: cEmerald }">محدوده تحلیل: {{ scopeLabel }}</p>
        </div>
        <div class="flex items-center gap-2">
          <div class="px-4 py-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/25 text-left">
            <p class="text-[10px] opacity-70 font-bold">جمع محدوده</p>
            <p class="text-lg font-black" :style="{ color: cEmerald }">{{ formatMoney(scopeTotalBalance) }}</p>
          </div>
          <button @click="openNewAccount" class="px-5 py-3 rounded-2xl font-bold text-white transition flex items-center gap-2 shadow-lg hover:scale-105 active:scale-95" :style="{ background: 'var(--accent)' }">
            <Plus class="w-5 h-5" /> تعریف حساب جدید
          </button>
        </div>
      </div>

      <!-- 🔍 انتخاب محدوده حساب‌ها برای تحلیل -->
      <div class="glass-card p-3 sm:p-4 rounded-2xl border border-white/10 shadow-xl space-y-2">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-black opacity-80">🎯 حساب‌های داخل تحلیل</h2>
          <button v-if="!isScopeAll" @click="resetScope" class="text-[11px] font-bold px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 transition">بازنشانی به همه</button>
        </div>
        <div class="flex flex-wrap gap-1.5 sm:gap-2">
          <button @click="resetScope"
                  class="px-3 py-1.5 rounded-xl text-xs font-black border transition"
                  :style="isScopeAll ? { background: '#9333ea', color: '#fff', borderColor: '#9333ea' } : { borderColor: 'rgba(255,255,255,0.15)', color: cMuted }">
            همه ({{ accounts.filter(a => !a.is_hidden).length }})
          </button>
          <button v-for="acc in accounts" :key="acc.id"
                  @click="toggleScopeAccount(acc.id)"
                  class="px-3 py-1.5 rounded-xl text-xs font-bold border transition flex items-center gap-1.5"
                  :style="selectedAccountIds.includes(acc.id)
                    ? { background: '#0e7490', color: '#fff', borderColor: '#0e7490' }
                    : { borderColor: 'rgba(255,255,255,0.15)', color: cMuted }">
            <span v-if="acc.is_hidden">🙈</span> {{ acc.name }}
          </button>
        </div>
        <p v-if="hiddenCount > 0" class="text-[10px] opacity-50">🙈 {{ hiddenCount }} حساب مخفی از «همه» بیرون است؛ برای تحلیل صریح انتخابش کن.</p>
      </div>

      <!-- 📊 گزارش مدیریت مالی (همیشه باز، الگو از داشبورد) -->
      <div class="glass-card p-3 sm:p-5 md:p-6 rounded-2xl md:rounded-3xl border border-white/10 shadow-2xl space-y-4 sm:space-y-5">

        <!-- هدر گزارش + سوییچر بازه -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 class="text-base sm:text-lg font-black flex items-center gap-2" :style="{ color: 'var(--text-primary)' }">
            <BarChart2 class="w-5 h-5 text-purple-400" /> گزارش مدیریت مالی
            <span v-if="reportLoading" class="opacity-50"><RefreshCw class="w-3 h-3 inline animate-spin" /></span>
          </h2>
          <div class="flex items-center gap-1 p-1 bg-black/40 rounded-xl border border-white/10 self-start sm:self-auto">
            <button v-for="d in [7,30,90]" :key="d"
                    @click="fetchReport(d)"
                    :disabled="reportLoading"
                    class="px-3 py-1.5 rounded-lg text-xs font-bold transition"
                    :style="reportDays === d ? { background: '#9333ea', color: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' } : { color: 'rgba(255,255,255,0.6)' }">
              {{ d === 7 ? '۱ هفته' : d === 30 ? '۱ ماه' : '۳ ماه' }}
            </button>
          </div>
        </div>

        <p class="text-[11px] opacity-60 -mt-3">{{ reportRangeDisplay }} — {{ scopeLabel }}</p>

        <!-- حالت loading -->
        <div v-if="reportLoading && !reportData" class="flex items-center justify-center py-10 opacity-60">
          <RefreshCw class="w-8 h-8 animate-spin" />
        </div>

        <!-- محتوای گزارش -->
        <div v-else-if="reportData" class="space-y-4 sm:space-y-5">

          <!-- ۴ کارت KPI (فشرده در موبایل: 2 ستون) - مثل داشبورد -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-3">
            <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/20">
              <p class="text-[10px] sm:text-xs font-bold opacity-70">مجموع واریز</p>
              <p class="text-base sm:text-xl font-black mt-0.5 truncate" :style="{ color: cEmerald }">+{{ formatMoney(reportData.summary.deposit_total) }}</p>
              <p class="text-[9px] font-bold" :style="{ color: cEmerald }">تومان</p>
            </div>
            <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-gradient-to-br from-rose-500/10 to-red-500/10 border border-rose-500/20">
              <p class="text-[10px] sm:text-xs font-bold opacity-70">مجموع برداشت</p>
              <p class="text-base sm:text-xl font-black mt-0.5 truncate" :style="{ color: cRose }">-{{ formatMoney(reportData.summary.withdraw_total) }}</p>
              <p class="text-[9px] font-bold" :style="{ color: cRose }">تومان</p>
            </div>
            <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl border"
                 :class="reportData.summary.balance_net >= 0 ? 'bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20' : 'bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20'">
              <p class="text-[10px] sm:text-xs font-bold opacity-70">تراز خالص</p>
              <p class="text-base sm:text-xl font-black mt-0.5 truncate"
                 :style="{ color: reportData.summary.balance_net >= 0 ? cBlue : cAmber }">
                {{ reportData.summary.balance_net >= 0 ? '+' : '-' }}{{ formatMoney(reportData.summary.balance_net) }}
              </p>
              <p class="text-[9px] opacity-70 font-bold">تومان</p>
            </div>
            <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
              <p class="text-[10px] sm:text-xs font-bold opacity-70">پرهزینه‌ترین</p>
              <p class="text-sm sm:text-base font-black mt-0.5 truncate" :style="{ color: cPurple }" v-if="reportData.summary.top_category">
                {{ getCategoryById(reportData.summary.top_category.id).name }}
              </p>
              <p class="text-sm sm:text-base font-black mt-0.5" :style="{ color: cPurple }" v-else>—</p>
              <p class="text-[9px] font-bold" :style="{ color: cPurple }" v-if="reportData.summary.top_category">
                {{ reportData.summary.transaction_count }} تراکنش
              </p>
              <p class="text-[9px] font-bold" :style="{ color: cPurple }" v-else>—</p>
            </div>
          </div>

          <!-- نمودار میله‌ای + Donut (در موبایل: عمودی، در دسکتاپ: کنار هم) -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5">

            <!-- نمودار میله‌ای Stacked با روز جاری طلایی (مثل داشبورد) - ۲/۳ عرض -->
            <div class="lg:col-span-2 space-y-2">
              <h3 class="text-sm font-black flex items-center gap-2 opacity-80">
                {{ reportData.bucket === 'week' ? 'نمودار هفتگی واریز و برداشت' : 'نمودار روزانه واریز و برداشت' }}
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 font-bold">
                  {{ reportDays === 7 ? 'هفته شمسی' : reportDays === 30 ? 'ماه اخیر' : '۳ ماه اخیر (هفتگی)' }}
                </span>
              </h3>
              <div class="rounded-2xl bg-black/30 border border-white/5 p-3 sm:p-4">
                <!-- خط میانگین (اگه داده داشته باشیم) -->
                <div v-if="maxDailyAmount > 1" class="relative">
                  <div class="absolute left-0 right-0 border-t border-dashed border-amber-400/40 z-[5] pointer-events-none"
                       :style="{ bottom: ((maxDailyAmount / 2) / maxDailyAmount * 100) + '%' }">
                    <span class="absolute -top-3 right-0 text-[9px] text-amber-400 bg-slate-900/80 px-1.5 py-0.5 rounded font-bold">میانگین</span>
                  </div>
                </div>

                <!-- Stacked: هر بازه یک ستون (سبز=واریز بالا، قرمز=برداشت پایین) - شروع شنبه از راست -->
                <div class="h-40 sm:h-44 flex items-end justify-between gap-1 sm:gap-1.5 pt-6 px-1 relative overflow-x-auto" dir="rtl">
                  <div v-for="(d, idx) in reportData.daily_buckets" :key="idx"
                       class="flex-1 h-full min-w-[14px] flex flex-col items-center justify-end cursor-pointer group relative"
                       @click="openReportDay(d)"
                       :title="`${d.weekday} (${formatDate(d.date)}) - واریز: ${formatNumber(d.deposit)} | برداشت: ${formatNumber(d.withdraw)}`">
                    <!-- فضای میله + نام بازه -->
                    <div class="w-full max-w-[36px] h-full flex flex-col items-center justify-end">
                      <!-- میله Stacked: برداشت (قرمز، پایین) + واریز (سبز، بالا) -->
                      <div class="w-full flex flex-col-reverse items-stretch overflow-hidden rounded-t-md ring-1 transition-all"
                           :class="idx === todayBucketIndex ? 'ring-amber-400/60 shadow-lg shadow-amber-500/30' : 'ring-white/10 group-hover:ring-white/40'"
                           :style="{ height: ((d.deposit + d.withdraw) > 0 ? Math.max(8, ((d.deposit + d.withdraw) / maxDailyAmount) * 100) : 0) + '%', minHeight: ((d.deposit + d.withdraw) > 0 ? '8px' : '0') }">
                        <!-- بخش برداشت (قرمز) - در پایین -->
                        <div v-if="d.withdraw > 0" class="w-full bg-gradient-to-t from-rose-700 to-rose-400 transition-all duration-500"
                             :style="{ height: maxDailyAmount > 0 ? Math.max(2, (d.withdraw / maxDailyAmount) * 100) + '%' : '0%' }"></div>
                        <!-- بخش واریز (سبز) - در بالا -->
                        <div v-if="d.deposit > 0" class="w-full bg-gradient-to-t from-emerald-700 to-emerald-400 transition-all duration-500"
                             :style="{ height: maxDailyAmount > 0 ? Math.max(2, (d.deposit / maxDailyAmount) * 100) + '%' : '0%' }"></div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- محور x: نام بازه‌ها (شنبه راست تا جمعه چپ) -->
                <div class="flex items-start gap-1 mt-2 overflow-x-auto" dir="rtl">
                  <div v-for="(d, idx) in reportData.daily_buckets" :key="idx" class="flex-1 text-center min-w-[14px]">
                    <div class="text-[9px] sm:text-[10px] font-bold truncate"
                         :class="idx === todayBucketIndex ? 'text-amber-400' : 'opacity-50'">
                      {{ d.weekday }}
                    </div>
                    <div class="text-[9px] opacity-30 truncate">{{ bucketSubLabel(d) }}</div>
                  </div>
                </div>

                <!-- راهنما -->
                <div class="flex items-center gap-3 sm:gap-4 mt-3 text-[10px] opacity-60">
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-emerald-500"></span> واریز</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-rose-500"></span> برداشت</span>
                  <span class="flex items-center gap-1 mr-auto"><span class="w-2 h-2 rounded-full bg-amber-400"></span> امروز</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-blue-500/40 ring-1 ring-blue-400/40"></span> کلیک = تفکیک</span>
                </div>
              </div>
            </div>

            <!-- Donut (در موبایل: پایین می‌آید) - ۱/۳ عرض -->
            <div class="space-y-2">
              <h3 class="text-sm font-black flex items-center gap-2 opacity-80">
                <PieChart class="w-4 h-4" /> تفکیک هزینه‌ها
              </h3>
              <div class="rounded-2xl bg-black/30 border border-white/5 p-3 sm:p-4 flex flex-col items-center">
                <!-- SVG Donut -->
                <div class="relative w-32 h-32 sm:w-36 sm:h-36">
                  <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
                    <circle cx="18" cy="18" r="15.9155" fill="transparent" stroke="rgba(255,255,255,0.05)" stroke-width="3" />
                    <circle v-for="(seg, i) in donutSegments" :key="i"
                            cx="18" cy="18" r="15.9155" fill="transparent"
                            :stroke="seg.color"
                            stroke-width="3"
                            :stroke-dasharray="donutPath(seg)"
                            :stroke-dashoffset="(-seg.offset)"
                            class="transition-all"
                            @mouseenter="donutHover = seg.id"
                            @mouseleave="donutHover = null"
                            style="cursor: pointer;" />
                  </svg>
                  <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none px-2 text-center">
                    <p class="text-[9px] sm:text-[10px] opacity-60">کل برداشت</p>
                    <p class="text-[10px] sm:text-xs font-black truncate w-full">{{ formatMoney(reportData.summary.withdraw_total) }}</p>
                  </div>
                </div>
                <!-- لیست دسته‌ها -->
                <div v-if="reportData.category_breakdown.length > 0" class="w-full mt-3 sm:mt-4 space-y-1.5 sm:space-y-2">
                  <div v-for="cat in reportData.category_breakdown.slice(0, 5)" :key="cat.id"
                       class="flex items-center gap-2 text-[10px] sm:text-[11px]"
                       :class="donutHover === cat.id ? 'opacity-100' : 'opacity-80'">
                    <span class="w-2.5 h-2.5 rounded-sm flex-shrink-0" :style="{ background: getCategoryById(cat.id).color }"></span>
                    <span class="flex-1 truncate">{{ getCategoryById(cat.id).name }}</span>
                    <span class="font-bold">{{ Math.round(cat.percent) }}٪</span>
                  </div>
                </div>
                <p v-else class="text-[10px] sm:text-[11px] opacity-50 mt-3 sm:mt-4">هزینه‌ای ثبت نشده</p>
              </div>
            </div>
          </div>

          <!-- تفکیک حساب‌ها در بازه (تحلیل انتخابی) -->
          <div v-if="reportData.account_breakdown && reportData.account_breakdown.length > 0" class="space-y-2">
            <h3 class="text-sm font-black flex items-center gap-2 opacity-80">
              <Wallet class="w-4 h-4 text-cyan-400" /> سهم حساب‌ها در این بازه
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              <div v-for="ab in reportData.account_breakdown" :key="ab.account_id"
                   class="flex items-center justify-between gap-2 px-3 py-2.5 rounded-xl bg-black/30 border border-white/5 text-xs">
                <span class="font-black truncate" :style="{ color: 'var(--text-primary)' }">{{ accountNameById(ab.account_id) }}</span>
                <span class="flex items-center gap-2 font-bold shrink-0">
                  <span :style="{ color: cEmerald }">+{{ formatNumber(ab.deposit) }}</span>
                  <span :style="{ color: cRose }">−{{ formatNumber(ab.withdraw) }}</span>
                  <span class="opacity-50">({{ ab.count }})</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 🔍 Popup مرکزی تفکیک بازه (وقتی روی میله کلیک شد) -->
      <Teleport to="body">
        <Transition name="popup">
          <div v-if="selectedReportDay"
               class="fixed inset-0 z-[400] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
               @click.self="selectedReportDay = null">
            <div class="w-full max-w-xs rounded-3xl p-5 bg-slate-900/98 border border-white/30 backdrop-blur-xl shadow-2xl shadow-black/60 text-white"
                 style="backface-visibility: hidden;">
              <!-- هدر -->
              <div class="flex items-center justify-between mb-3 pb-2 border-b border-white/10">
                <div>
                  <p class="text-xs opacity-60">{{ formatDate(selectedReportDay.date) }}</p>
                  <p class="text-base font-black"
                     :class="selectedReportDay.date === new Date().toISOString().split('T')[0] ? 'text-amber-400' : ''">
                    {{ selectedReportDay.weekday }}
                    <span v-if="selectedReportDay.date === new Date().toISOString().split('T')[0]" class="text-[10px] text-amber-300 font-black mr-1">امروز</span>
                  </p>
                </div>
                <button @click="selectedReportDay = null" class="p-1.5 rounded-lg hover:bg-white/10 transition text-slate-400 hover:text-white">
                  <X class="w-4 h-4" />
                </button>
              </div>
              <!-- تفکیک واریز/برداشت -->
              <div class="space-y-2 text-sm">
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                  <span class="flex items-center gap-2 text-xs font-bold">
                    <span class="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
                    مجموع واریز
                  </span>
                  <span class="font-black dir-ltr text-xs" :style="{ color: cEmerald }">{{ formatMoney(selectedReportDay.deposit) }}</span>
                </div>
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20">
                  <span class="flex items-center gap-2 text-xs font-bold">
                    <span class="w-2.5 h-2.5 rounded-sm bg-rose-500"></span>
                    مجموع برداشت
                  </span>
                  <span class="font-black dir-ltr text-xs" :style="{ color: cRose }">{{ formatMoney(selectedReportDay.withdraw) }}</span>
                </div>
                <div class="flex items-center justify-between p-2.5 rounded-xl border"
                     :class="(selectedReportDay.deposit - selectedReportDay.withdraw) >= 0 ? 'bg-blue-500/10 border-blue-500/20' : 'bg-amber-500/10 border-amber-500/20'">
                  <span class="text-xs font-bold">تراز {{ reportData?.bucket === 'week' ? 'هفته' : 'روز' }}</span>
                  <span class="font-black text-xs dir-ltr"
                        :style="{ color: (selectedReportDay.deposit - selectedReportDay.withdraw) >= 0 ? cBlue : cAmber }">
                    {{ (selectedReportDay.deposit - selectedReportDay.withdraw) >= 0 ? '+' : '-' }}{{ formatMoney(Math.abs(selectedReportDay.deposit - selectedReportDay.withdraw)) }}
                  </span>
                </div>
              </div>
              <!-- راهنما -->
              <p class="text-[10px] text-center opacity-40 mt-3">برای بستن، خارج از کادر کلیک کنید</p>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- داشبورد دارایی و موجودی -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="rounded-3xl p-6 border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center"><Wallet class="w-6 h-6" /></div>
          <div>
            <p class="text-xs opacity-60">مجموع دارایی قابل‌مشاهده</p>
            <p class="text-2xl font-black text-emerald-400">
              {{ formatMoney(accounts.filter(a => !a.is_hidden).reduce((sum, a) => sum + (Number(a.current_balance) || 0), 0)) }}
            </p>
            <p v-if="hiddenCount > 0" class="text-[10px] opacity-50 font-bold mt-0.5">🙈 {{ hiddenCount }} حساب مخفی بیرون از جمع</p>
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
      <!-- گرید کارت‌های بانکی (۲ ستونه در همه سایزها) -->
      <div v-if="accounts.length === 0" class="text-center py-20 opacity-40">
        <Wallet class="w-16 h-16 mx-auto mb-4" />
        <p class="text-lg font-bold">هیچ حسابی تعریف نشده است</p>
        <p class="text-xs mt-2 opacity-60">برای شروع، روی «تعریف حساب جدید» در بالا کلیک کنید</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
        <div v-for="(acc, idx) in accounts" :key="acc.id"
             class="relative rounded-2xl overflow-hidden border shadow-2xl transition-all duration-300 hover:scale-[1.01] hover:shadow-purple-500/20"
             :class="acc.is_hidden ? 'border-dashed border-amber-400/40 opacity-90' : 'border-white/10'"
             :style="{
               background: idx % 2 === 0
                 ? 'linear-gradient(135deg, #1e3a8a 0%, #4c1d95 50%, #831843 100%)'
                 : 'linear-gradient(135deg, #0f766e 0%, #1e3a8a 50%, #4c1d95 100%)'
             }">

          <!-- پترن دکوراتیو کارت بانکی -->
          <div class="absolute top-0 left-0 w-32 h-32 bg-white/10 rounded-full -translate-x-12 -translate-y-12 blur-2xl"></div>
          <div class="absolute bottom-0 right-0 w-40 h-40 bg-white/5 rounded-full translate-x-16 translate-y-16 blur-3xl"></div>

          <!-- هدر کارت: لوگو/شماره کارت (از روی شبا یا ID) — کلیک = صفحه اختصاصی -->
          <div class="relative p-2.5 sm:p-5 flex items-center justify-between cursor-pointer" @click="goToAccount(acc.id)">
            <div class="flex items-center gap-2 sm:gap-3 min-w-0">
              <div class="w-8 h-8 sm:w-11 sm:h-11 rounded-lg sm:rounded-xl bg-white/15 backdrop-blur-md flex items-center justify-center shadow-inner border border-white/20 flex-shrink-0">
                <CreditCard class="w-4 h-4 sm:w-6 sm:h-6 text-amber-300" />
              </div>
              <div class="min-w-0">
                <p class="text-[8px] sm:text-[10px] opacity-70 font-bold uppercase tracking-wider">حساب</p>
                <h3 class="text-[11px] sm:text-base font-black truncate max-w-[160px] sm:max-w-[140px]">{{ acc.name }} <span v-if="acc.is_hidden" title="موجودی مخفی">🙈</span></h3>
              </div>
            </div>
            <div class="text-left min-w-0">
              <p class="text-[8px] sm:text-[9px] opacity-60 font-bold uppercase">بانک</p>
              <p class="text-[10px] sm:text-xs font-black truncate max-w-[50px] sm:max-w-[80px]">{{ acc.bank_name || '—' }}</p>
            </div>
          </div>

          <!-- بدنه: موجودی + شماره شبا -->
          <div class="relative px-2.5 sm:px-5 pb-2 sm:pb-3">
            <p class="text-[8px] sm:text-[10px] opacity-60 font-bold mb-0.5">موجودی فعلی <span v-if="acc.is_hidden" class="text-amber-300">(مخفی از جمع کل)</span></p>
            <p class="text-sm sm:text-2xl font-black mb-1 sm:mb-2 truncate" :class="acc.current_balance >= 0 ? 'text-emerald-300' : 'text-rose-300'">
              {{ formatMoney(acc.current_balance) }}
            </p>
            <div v-if="acc.sheba_number" class="hidden sm:flex items-center gap-1.5 text-[10px] opacity-60" dir="ltr">
              <span class="w-1 h-1 rounded-full bg-white/40"></span>
              <span class="font-mono truncate">{{ acc.sheba_number }}</span>
            </div>
          </div>

          <!-- آمار سریع: تراکنش‌ها -->
          <div class="relative px-2.5 sm:px-5 py-1.5 sm:py-2.5 bg-black/20 backdrop-blur-sm border-t border-white/10 flex items-center justify-between text-[9px] sm:text-[10px] gap-1">
            <div class="flex items-center gap-0.5 sm:gap-1 opacity-80 min-w-0">
              <span class="font-bold">{{ acc.transaction_count || 0 }}</span>
              <span class="opacity-60 truncate">تراکنش</span>
            </div>
            <div class="flex items-center gap-0.5 text-emerald-300 min-w-0">
              <span class="font-bold truncate">+{{ formatMoney(acc.total_deposits || 0) }}</span>
            </div>
            <div class="flex items-center gap-0.5 text-rose-300 min-w-0">
              <span class="font-bold truncate">-{{ formatMoney(acc.total_withdrawals || 0) }}</span>
            </div>
          </div>

          <!-- نوار دکمه‌ها -->
          <div class="relative px-1.5 sm:px-4 py-1.5 sm:py-3 bg-black/30 backdrop-blur-md flex items-center gap-1 sm:gap-2">
            <button @click.stop="openNewTransaction(acc)"
                    class="flex-1 py-1 sm:py-2 rounded-md sm:rounded-lg bg-emerald-500/90 hover:bg-emerald-400 text-white text-[9px] sm:text-xs font-black flex items-center justify-center gap-0.5 sm:gap-1 transition shadow-md"
                    title="تراکنش جدید">
              <Plus class="w-3 h-3 sm:w-4 sm:h-4" /> <span class="truncate">تراکنش</span>
            </button>
            <button @click.stop="toggleTransactions(acc.id)"
                    class="px-1.5 sm:px-3 py-1 sm:py-2 rounded-md sm:rounded-lg bg-white/10 hover:bg-white/20 text-white text-[9px] sm:text-xs font-bold flex items-center justify-center gap-0.5 sm:gap-1 transition"
                    :title="expandedAccounts[acc.id] ? 'بستن تراکنش‌ها' : 'مشاهده تراکنش‌ها'">
              <ChevronUp v-if="expandedAccounts[acc.id]" class="w-3 h-3 sm:w-4 sm:h-4" />
              <ChevronDown v-else class="w-3 h-3 sm:w-4 sm:h-4" />
              <span class="hidden sm:inline">{{ expandedAccounts[acc.id] ? 'بستن' : 'لیست' }}</span>
            </button>
            <button @click.stop="toggleHidden(acc)"
                    class="p-1 sm:p-2 rounded-md sm:rounded-lg transition"
                    :class="acc.is_hidden ? 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30' : 'bg-white/10 hover:bg-white/20 text-white'"
                    :title="acc.is_hidden ? 'خارج کردن از حالت مخفی' : 'مخفی کردن موجودی از جمع کل'">
              <EyeOff v-if="acc.is_hidden" class="w-3 h-3 sm:w-4 sm:h-4" />
              <Eye v-else class="w-3 h-3 sm:w-4 sm:h-4" />
            </button>
            <button @click.stop="openEditAccount(acc)" class="p-1 sm:p-2 rounded-md sm:rounded-lg bg-white/10 hover:bg-white/20 text-white transition" title="ویرایش">
              <Edit3 class="w-3 h-3 sm:w-4 sm:h-4" />
            </button>
            <button @click.stop="deleteAccount(acc.id)" class="p-1 sm:p-2 rounded-md sm:rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition" title="حذف">
              <Trash2 class="w-3 h-3 sm:w-4 sm:h-4" />
            </button>
          </div>

          <!-- لیست تراکنش‌ها (زیر کارت) -->
          <div v-if="expandedAccounts[acc.id]" class="relative bg-black/50 backdrop-blur-md border-t border-white/10">
            <div v-if="acc.transactions && acc.transactions.length > 0" class="divide-y divide-white/5 max-h-96 overflow-y-auto">
              <div v-for="trans in acc.transactions" :key="trans.id" class="flex items-center justify-between p-3 sm:p-4 hover:bg-white/[0.02] group">
                <div class="flex items-center gap-2.5 sm:gap-3 min-w-0 flex-1">
                  <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                       :style="{ background: trans.transaction_type === 'deposit' ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)' }">
                    <component :is="getCategoryIcon(trans.category)" class="w-4 h-4" :style="{ color: getCategoryColor(trans.category) }" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="font-bold text-xs sm:text-sm truncate">{{ trans.description || (trans.transaction_type === 'deposit' ? 'واریز' : 'برداشت') }}</p>
                    <p v-if="trans.items" class="text-[10px] opacity-60 truncate">اقلام: {{ trans.items }}</p>
                    <p class="text-[10px] opacity-50">{{ formatDate(trans.transaction_date) }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
                  <p class="font-black text-sm sm:text-base" :class="trans.transaction_type === 'deposit' ? 'text-emerald-300' : 'text-rose-300'">
                    {{ trans.transaction_type === 'deposit' ? '+' : '-' }} {{ formatMoney(trans.amount) }}
                  </p>
                  <div class="flex gap-1 transition-opacity">
                    <button @click="openEditTransaction(acc, trans)" class="p-1 rounded hover:bg-white/10"><Edit3 class="w-3.5 h-3.5" /></button>
                    <button @click="deleteTransaction(trans.id)" class="p-1 rounded hover:bg-red-500/20 text-red-300"><Trash2 class="w-3.5 h-3.5" /></button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="p-6 text-center text-xs opacity-40">تراکنشی برای این حساب ثبت نشده است.</div>
          </div>

        </div>
      </div>

      <!-- ========== مودال حساب ========== -->
      <div v-if="showAccountForm" class="fixed inset-0 z-[300] flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md" @click.self="showAccountForm = false">
        <div class="w-full max-w-md max-h-[92vh] overflow-y-auto rounded-2xl sm:rounded-3xl p-5 sm:p-7 bg-gray-900/95 border border-white/10 shadow-2xl shadow-black/50 text-white space-y-4 sm:space-y-5">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <h3 class="text-lg sm:text-xl font-black">{{ editingAccount ? 'ویرایش حساب' : 'تعریف حساب جدید' }}</h3>
            <button @click="showAccountForm = false" class="p-1.5 rounded-lg hover:bg-white/10 transition">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="space-y-3 sm:space-y-4 text-right" dir="rtl">
            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">نام حساب (اجباری) *</label>
              <input v-model="accountForm.name" placeholder="مثلاً: کارت اصلی ملت"
                     class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm focus:ring-2 focus:ring-purple-500/50" />
            </div>
            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">نام بانک</label>
              <input v-model="accountForm.bank_name" placeholder="مثلاً: بانک پاسارگاد"
                     class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm focus:ring-2 focus:ring-purple-500/50" />
            </div>
            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">شماره شبا</label>
              <input v-model="accountForm.sheba_number" placeholder="IR..." dir="ltr"
                     class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm focus:ring-2 focus:ring-purple-500/50" />
            </div>
            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">موجودی اولیه (تومان)</label>
              <input :value="formatNumber(accountForm.current_balance)" @input="accountForm.current_balance = parseNumber($event.target.value)"
                     inputmode="numeric"
                     class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-base sm:text-lg font-bold text-emerald-400 focus:ring-2 focus:ring-emerald-500/50" />
              <p class="text-[10px] mt-1 font-medium pr-1 truncate" :style="{ color: cEmerald }">{{ numberToPersianWords(parseNumber(accountForm.current_balance)) }}</p>
            </div>
            <label class="flex items-center gap-2.5 p-3 rounded-xl border cursor-pointer transition"
                   :class="accountForm.is_hidden ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 bg-black/40'">
              <input type="checkbox" v-model="accountForm.is_hidden" class="w-4 h-4 accent-amber-400" />
              <span class="text-xs font-bold">🙈 موجودی مخفی <span class="opacity-60 font-medium">— در جمع کل و تراز لحاظ نشود</span></span>
            </label>
            <div>
              <label class="text-xs mb-1.5 block opacity-70 font-bold">تاریخ ثبت/افتتاح</label>
              <DateInputPersian v-model="accountForm.register_date" />
            </div>
          </div>

          <div class="flex gap-2 sm:gap-3 pt-3">
            <button @click="saveAccount" class="flex-1 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl text-white font-bold text-sm sm:text-base shadow-lg shadow-emerald-500/20"
                    :style="{ background: 'var(--accent)' }">ذخیره حساب</button>
            <button @click="showAccountForm = false" class="px-4 sm:px-6 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl text-sm sm:text-base font-semibold bg-white/10 hover:bg-white/20 transition">انصراف</button>
          </div>
        </div>
      </div>

      <!-- ========== مودال تراکنش ========== -->
      <div v-if="showTransactionForm" class="fixed inset-0 z-[300] flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md" @click.self="showTransactionForm = false">
        <div class="w-full max-w-lg max-h-[92vh] overflow-y-auto rounded-2xl sm:rounded-3xl p-5 sm:p-7 bg-gray-900/95 border border-white/10 shadow-2xl shadow-black/50 text-white space-y-4 sm:space-y-5">
          <!-- هدر مودال -->
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <div>
              <h3 class="text-lg sm:text-xl font-black">{{ editingTransaction ? 'ویرایش تراکنش' : 'ثبت تراکنش جدید' }}</h3>
              <p class="text-[11px] opacity-60 mt-0.5">حساب: {{ selectedAccount?.name }}</p>
            </div>
            <button @click="showTransactionForm = false" class="p-1.5 rounded-lg hover:bg-white/10 transition">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- نوع تراکنش -->
          <div class="flex gap-2 p-1 rounded-2xl bg-black/40 border border-white/10">
            <button @click="transactionForm.transaction_type = 'withdrawal'; transactionForm.category=''"
                    class="flex-1 py-2.5 rounded-xl font-bold transition flex items-center justify-center gap-2 text-xs sm:text-sm"
                    :style="transactionForm.transaction_type === 'withdrawal' ? { background: '#ef4444', color: '#fff', boxShadow: '0 2px 8px rgba(239,68,68,0.3)' } : { color: 'var(--text-secondary)' }">
              <ArrowDown class="w-4 h-4" /> برداشت
            </button>
            <button @click="transactionForm.transaction_type = 'deposit'; transactionForm.category=''"
                    class="flex-1 py-2.5 rounded-xl font-bold transition flex items-center justify-center gap-2 text-xs sm:text-sm"
                    :style="transactionForm.transaction_type === 'deposit' ? { background: '#22c55e', color: '#fff', boxShadow: '0 2px 8px rgba(34,197,94,0.3)' } : { color: 'var(--text-secondary)' }">
              <ArrowUp class="w-4 h-4" /> واریز
            </button>
          </div>

          <!-- دسته‌بندی -->
          <div>
            <label class="text-xs mb-2 block opacity-70 font-bold">انتخاب دسته‌بندی *</label>
            <div class="grid grid-cols-4 gap-1.5 sm:gap-2">
              <button v-for="cat in categories[transactionForm.transaction_type]" :key="cat.id"
                      @click="transactionForm.category = cat.id"
                      class="flex flex-col items-center p-2 sm:p-2.5 rounded-xl sm:rounded-2xl border transition-all hover:scale-105"
                      :style="transactionForm.category === cat.id ? { borderColor: cat.color, background: cat.color + '25' } : { borderColor: 'rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.03)' }">
                <component :is="cat.icon" class="w-4 h-4 sm:w-5 sm:h-5 mb-0.5 sm:mb-1" :style="{ color: cat.color }" />
                <span class="text-[8px] sm:text-[9px] text-center opacity-80 leading-tight">{{ cat.name }}</span>
              </button>
            </div>
          </div>

          <!-- مبلغ -->
          <div>
            <label class="text-xs mb-1.5 block opacity-70 font-bold">مبلغ (تومان) *</label>
            <input :value="formatNumber(transactionForm.amount)" @input="transactionForm.amount = parseNumber($event.target.value)"
                   class="w-full px-4 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl border border-white/10 bg-black/40 font-black text-xl sm:text-2xl text-center outline-none focus:ring-2"
                   :style="{ color: transactionForm.transaction_type === 'deposit' ? '#22c55e' : '#ef4444' }"
                   :class="errors.amount ? 'ring-2 ring-rose-500' : ''"
                   inputmode="numeric" />
            <p class="text-[10px] sm:text-xs mt-1.5 text-center font-bold truncate" :style="{ color: cEmerald }">{{ numberToPersianWords(parseNumber(transactionForm.amount)) }}</p>
          </div>

          <!-- اقلام (فقط برداشت) -->
          <div v-if="transactionForm.transaction_type === 'withdrawal'">
            <label class="text-xs mb-1.5 block opacity-70 font-bold">اقلام خرید</label>
            <input v-model="transactionForm.items" placeholder="مثلاً: شیر، نان، میوه..."
                   class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm focus:ring-2 focus:ring-purple-500/50" />
          </div>

          <!-- توضیحات -->
          <div>
            <label class="text-xs mb-1.5 block opacity-70 font-bold">توضیحات</label>
            <input v-model="transactionForm.description" placeholder="بابتِ..."
                   class="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl border border-white/10 bg-black/40 outline-none text-sm focus:ring-2 focus:ring-purple-500/50" />
          </div>

          <!-- تاریخ تراکنش -->
          <div>
            <label class="text-xs mb-1.5 block opacity-70 font-bold">تاریخ تراکنش</label>
            <DateInputPersian v-model="transactionForm.transaction_date" />
          </div>

          <!-- دکمه‌ها -->
          <div class="flex gap-2 sm:gap-3 pt-2">
            <button @click="saveTransaction" class="flex-1 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl text-white font-bold text-sm sm:text-base shadow-lg"
                    :style="{ background: 'var(--accent)' }">
              {{ editingTransaction ? 'ذخیره تغییرات' : 'ثبت نهایی' }}
            </button>
            <button @click="showTransactionForm = false" class="px-4 sm:px-6 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl text-sm sm:text-base font-semibold bg-white/10 hover:bg-white/20 transition">
              انصراف
            </button>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>
