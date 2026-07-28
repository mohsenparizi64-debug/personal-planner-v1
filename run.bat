@echo off
chcp 65001 >nul
title Personal Planner - Starting...

echo.
echo ========================================
echo     🚀 Personal Planner - در حال اجرا
echo ========================================
echo.

:: بررسی Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python نصب نیست! لطفاً Python 3.10+ نصب کن.
    pause
    exit /b
)

:: بررسی Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js نصب نیست! لطفاً Node.js 18+ نصب کن.
    pause
    exit /b
)

:: بررسی و نصب پکیج‌های بک‌اند
echo 📦 بررسی پکیج‌های بک‌اند...
cd backend
if not exist "venv\" (
    echo 🔧 ساخت محیط مجازی Python...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo ✅ بک‌اند آماده‌ست

:: اجرای بک‌اند
start "Backend" cmd /k "cd /d %cd% && venv\Scripts\activate && python -m uvicorn app.main:app --reload"
echo 🌐 بک‌اند روی http://localhost:8000 اجرا شد

cd ..

:: بررسی و نصب پکیج‌های فرانت
echo.
echo 📦 بررسی پکیج‌های فرانت...
cd frontend
if not exist "node_modules\" (
    echo 🔧 نصب پکیج‌های npm...
    npm install
)
echo ✅ فرانت آماده‌ست

:: اجرای فرانت (استفاده از 127.0.0.1 برای جلوگیری از خطای لوکال‌هاست)
start "Frontend" cmd /k "cd /d %cd% && npm run dev -- --host 127.0.0.1"
echo 🎨 فرانت روی http://127.0.0.1:5173 اجرا شد

:: صبر کن و مرورگر رو با آدرس دقیق باز کن
echo.
echo ⏳ صبر کن تا سرورها آماده بشن...
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5173

echo.
echo ========================================
echo     ✅ همه چیز آماده‌ست!
echo     🌐 آدرس: http://127.0.0.1:5173
echo ========================================
echo.
echo پنجره‌ها رو نبند. برای خروج Ctrl+C بزن.
pause