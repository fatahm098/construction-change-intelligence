@echo off
REM Jalankan backend (FastAPI :8000) dan frontend (Next.js :3000) sekaligus.
REM Klik dua kali file ini, lalu tunggu jendela browser terbuka.

set "ROOT=%~dp0"

if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo [X] Virtualenv backend belum ada. Jalankan dulu:
  echo       cd backend
  echo       python -m venv .venv
  echo       .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "%ROOT%frontend\node_modules" (
  echo [X] Dependensi frontend belum ada. Jalankan dulu:
  echo       cd frontend
  echo       npm install
  pause
  exit /b 1
)

echo Menyalakan backend di http://localhost:8000 ...
start "CCI Backend" /D "%ROOT%backend" cmd /k .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

echo Menyalakan frontend di http://localhost:3000 ...
start "CCI Frontend" /D "%ROOT%frontend" cmd /k npm run dev

echo Menunggu server siap...
timeout /t 12 /nobreak >nul
start http://localhost:3000

echo.
echo Selesai. Tutup kedua jendela terminal untuk mematikan server.
