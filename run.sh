#!/bin/bash

# WBS BPKH Launcher Script
# Quick start script untuk menjalankan aplikasi

echo "=========================================="
echo "🛡️  WBS BPKH - AI Whistleblowing System"
echo "   Badan Pengelola Keuangan Haji"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 tidak ditemukan. Silakan install Python 3.10+"
    exit 1
fi

echo "✅ Python version:"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo ""

# Install/update dependencies
echo "📥 Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file tidak ditemukan"
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file dan tambahkan GROQ_API_KEY"
    echo "   Get free API key from: https://console.groq.com"
    echo ""
fi

# Run Streamlit
echo "🚀 Starting WBS BPKH application..."
echo "   Application will open at: http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the application"
echo ""
echo "=========================================="

streamlit run app.py

# Deactivate virtual environment on exit
deactivate
