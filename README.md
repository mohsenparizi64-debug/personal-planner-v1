# 🗓️ Personal Planner | پلنر شخصی

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![Vue](https://img.shields.io/badge/vue-3.x-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

یه برنامه‌ریز شخصی کامل و پیشرفته با قابلیت مدیریت تسک‌ها، اهداف، مالی، فیلم‌ها، کتاب‌ها و مکان‌ها. با سه تم مختلف، احراز هویت JWT، پروفایل کاربری و سیستم بکاپ‌گیری.

---

## 📸 پیش‌نمایش

![Dashboard](screenshots/dashboard.png)
![Tasks](screenshots/tasks.png)
![Goals](screenshots/goals.png)

---

## 🚀 قابلیت‌ها

### 🔐 احراز هویت
- ثبت‌نام با نام، ایمیل، موبایل و رمز عبور
- ورود با JWT
- بازیابی رمز عبور (دو مرحله‌ای)
- پروفایل کاربری با آواتار
- خروج با تأیید

### 📋 تسک‌ها (۱۱ فیلد)
- تاریخ ثبت، عنوان، مهلت، دسته‌بندی
- ماهیت (متصل به اهداف کلان)
- تاریخ آخرین اقدام، وضعیت
- دوره تکرار (روزانه/هفتگی/ماهانه/سالیانه)
- اهمیت (عادی/مهم/اضطراری)
- فیلترهای پیشرفته

### 🎯 اهداف کلان
- ۸ فیلد شامل وضعیت فعلی، موانع، گام بعدی
- تاریخچه کامل تغییرات (Audit Log)
- معیارهای موفقیت

### 🗺️ نقشه راه
- زیرهدف‌ها با تسک‌های قابل چک
- KPI با نوار پیشرفت
- اتصال به اهداف کلان

### 💰 مدیریت مالی
- حساب‌های بانکی با شبا و موجودی
- تراکنش‌های واریز/برداشت
- محاسبه خودکار مانده

### 🎬 فیلم‌ها | 📚 کتاب‌ها | 📍 مکان‌ها
- افزودن، ویرایش، حذف
- فیلتر و جستجو
- امتیازدهی
- وضعیت دیده/خوانده/رفته

### 💾 بکاپ و بازیابی
- خروجی JSON از تمام اطلاعات
- بازیابی با نگاشت صحیح IDها

### 🎨 سه تم
| تم | رنگ اصلی |
|----|----------|
| 🌙 مدرن تاریک | بنفش #8b5cf6 |
| 🏛️ کلاسیک ایرانی | طلایی #c9a84c |
| 🤖 رباتیک دیجیتال | سبز نئون #00ff88 |

### 🕐 امکانات UI
- ساعت آنالوگ Canvas-based
- تاریخ شمسی و میلادی
- راست‌چین کامل (RTL)
- ریسپانسیو (موبایل و دسکتاپ)
- اعلان‌های Toast

---

## 🛠️ تکنولوژی‌ها

### بک‌اند
- **Python 3.13** + **FastAPI**
- **SQLAlchemy 2.0** (async)
- **SQLite** (قابل ارتقا به PostgreSQL)
- **JWT** احراز هویت
- **Alembic** migrations

### فرانت‌اند
- **Vue 3** (Composition API)
- **Vite 5**
- **Tailwind CSS 3**
- **Pinia** state management
- **Vue Router 4**
- **Axios**

---

## 📂 ساختار پروژه
personal-planner/
├── backend/
│ ├── app/
│ │ ├── api/v1/ # API endpoints
│ │ ├── core/ # تنظیمات و امنیت
│ │ ├── crud/ # عملیات دیتابیس
│ │ ├── models/ # مدل‌های SQLAlchemy
│ │ ├── schemas/ # Pydantic models
│ │ └── main.py # اپلیکیشن اصلی
│ └── requirements.txt
├── frontend/
│ ├── src/
│ │ ├── components/ # کامپوننت‌های مشترک
│ │ ├── pages/ # صفحات برنامه
│ │ ├── router/ # مسیرها
│ │ ├── stores/ # Pinia stores
│ │ └── services/ # API client
│ └── package.json
└── run.bat # اجرای یک‌کلیکی


---

## 🚀 اجرای سریع

### پیش‌نیازها
- Python 3.10+
- Node.js 18+

### روش ۱: یک کلیکی (Windows)
```bash
run.bat

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

cd frontend
npm install
npm run dev

فرانت‌اند: http://localhost:5173

بک‌اند: http://localhost:8000

مستندات API: http://localhost:8000/docs

📡 API Endpoints
Module	Base URL
Auth	/api/v1/auth
Tasks	/api/v1/tasks
Goals	/api/v1/goals
Roadmap	/api/v1/roadmap
Finance	/api/v1/finance
Movies	/api/v1/movies
Books	/api/v1/books
Places	/api/v1/places
Backup	/api/v1/backup
مستندات کامل Swagger در http://localhost:8000/docs

