@echo off
title Personal Planner
echo [!] Starting Backend...
start "Backend" cmd /k "cd /d C:\Users\Instrumentation\Desktop\personal-planner\personal-planner-v1\backend && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo [!] Starting Frontend...
start "Frontend" cmd /k "cd /d C:\Users\Instrumentation\Desktop\personal-planner\personal-planner-v1\frontend && npm run dev -- --host 0.0.0.0"
echo.
echo [!] Backend: http://localhost:8000/docs
echo [!] Frontend: http://localhost:5173
pause