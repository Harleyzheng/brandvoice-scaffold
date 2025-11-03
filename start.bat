@echo off
REM BrandVoice Studio - Quick Start Script (Windows)

echo 🎭 BrandVoice Studio - Starting Application
echo ===========================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)

REM Check if Node is available
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install Node.js 16+
    exit /b 1
)

REM Check if backend dependencies are installed
echo 📦 Checking backend dependencies...
python -c "import fastapi" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing backend dependencies...
    pip install -r api\requirements.txt
)

REM Check if frontend dependencies are installed
echo 📦 Checking frontend dependencies...
if not exist "web\node_modules\" (
    echo Installing frontend dependencies...
    cd web
    call npm install
    cd ..
)

echo.
echo ✅ All dependencies ready!
echo.
echo Starting servers...
echo - Backend API will run on http://localhost:8000
echo - Frontend UI will run on http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start backend in new window
echo 🚀 Starting backend...
start "BrandVoice Backend" cmd /k python api\server.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo 🚀 Starting frontend...
cd web
start "BrandVoice Frontend" cmd /k npm start
cd ..

echo.
echo ✅ Servers started!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the server windows to stop the application.
pause


