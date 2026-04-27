@echo off
echo ============================================
echo  NOBIAS - AI Bias Auditing Platform
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.9+ from python.org
    pause
    exit /b 1
)

REM Install backend dependencies
echo Checking backend dependencies...
pip install unbiased==0.0.0 fastapi "uvicorn[standard]" python-multipart pandas openpyxl imbalanced-learn aiohttp >nul 2>&1
echo Done.
echo.

REM Start backend
echo Starting backend server...
start "Nobias Backend" /B python backend/main.py
timeout /t 3 /nobreak >nul

REM Check backend health
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=3); print('Backend OK')" 2>nul
if errorlevel 1 (
    echo WARNING: Backend may still be starting. Check the backend window for errors.
) else (
    echo Backend running on http://127.0.0.1:8000
)
echo.

REM Start frontend
echo Starting frontend dev server...
echo Open http://localhost:5173 in your browser
echo.
npm run dev
