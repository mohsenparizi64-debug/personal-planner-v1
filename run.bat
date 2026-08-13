@echo off
cd /d "%~dp0"
title Personal Planner Launcher

echo ===================================================
echo   Personal Planner Launcher
echo ===================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not added to PATH!
    pause
    exit /b 1
)

:: 2. Check Node.js
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not added to PATH!
    pause
    exit /b 1
)

:: 3. Check Folders
if not exist backend (
    echo ERROR: Folder backend not found!
    pause
    exit /b 1
)

if not exist frontend (
    echo ERROR: Folder frontend not found!
    pause
    exit /b 1
)

:: 4. Setup Backend
echo [1/4] Preparing Python Backend...
cd /d "%~dp0backend"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

:: 5. Setup Frontend
echo.
echo [2/4] Preparing Frontend...
cd /d "%~dp0frontend"

if not exist node_modules (
    echo Installing npm dependencies...
    call npm install
)

:: 6. Start FastAPI Backend Server
echo.
echo [3/4] Starting FastAPI Backend on port 8000...
start "Planner Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 7. Start Vue Frontend Server
echo.
echo [4/4] Starting Vue 3 Frontend on port 5173...
start "Planner Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 0.0.0.0"

:: 8. Launch Browser
echo.
echo ===================================================
echo   Application started successfully!
echo   Opening http://localhost:5173 in 5 seconds...
echo ===================================================
timeout /t 5
start http://localhost:5173

pause