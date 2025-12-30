@echo off
REM WBS BPKH Launcher Script for Windows
REM Quick start script untuk menjalankan aplikasi di Windows

echo ==========================================
echo 🛡️  WBS BPKH - AI Whistleblowing System
echo    Badan Pengelola Keuangan Haji
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan. Silakan install Python 3.10+
    pause
    exit /b 1
)

echo ✅ Python version:
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/update dependencies
echo 📥 Installing/updating dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
echo ✅ Dependencies installed
echo.

REM Check for .env file
if not exist ".env" (
    echo ⚠️  .env file tidak ditemukan
    echo 📋 Creating .env from .env.example...
    copy .env.example .env
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env file dan tambahkan GROQ_API_KEY
    echo    Get free API key from: https://console.groq.com
    echo.
)

REM Run Streamlit
echo 🚀 Starting WBS BPKH application...
echo    Application will open at: http://localhost:8501
echo.
echo    Press Ctrl+C to stop the application
echo.
echo ==========================================
echo.

streamlit run app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
