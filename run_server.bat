@echo off
title Personal Planner Life OS Server Launcher
color 0A
chcp 65001 > nul

echo ========================================================
echo   Starting Personal Planner (Life OS)
echo   Backend: Port 8000 (Host: 0.0.0.0)
echo   Frontend: Port 3000
echo ========================================================
echo.

:: 1. بررسی و اجرای FastAPI / Uvicorn Backend
echo [1/2] Launching FastAPI Backend Server on Port 8000...
start "Backend FastAPI" cmd /k "cd /d %~dp0backend && (if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat) && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. بررسی و اجرای Vue 3 Frontend
echo [2/2] Launching Vue 3 Frontend Production Server on Port 3000...
start "Frontend Vue" cmd /k "cd /d %~dp0frontend && npx serve -s dist -l tcp://0.0.0.0:3000"

echo.
echo ========================================================
echo   SERVER LAUNCHED SUCCESSFULLY!
echo.
echo   Local Access (Inside VPS):
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000/docs
echo.
echo   Remote / Mobile Access:
echo   - Application: http://YOUR_SERVER_IP:3000
echo   - API Base:    http://YOUR_SERVER_IP:8000/api/v1
echo ========================================================
echo.
pause