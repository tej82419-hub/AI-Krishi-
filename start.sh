#!/bin/bash
# AI Krishi – Quick Start Script
# Run: chmod +x start.sh && ./start.sh

set -e

echo "🌾 Starting AI Krishi – Smart Farming Assistant"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r backend/requirements.txt -q

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   GEMINI_API_KEY    → https://aistudio.google.com/app/apikey (free)"
    echo "   OPENWEATHER_API_KEY → https://openweathermap.org/api (free)"
    echo ""
    echo "   The app works in demo mode without keys, but AI features will be limited."
    echo ""
fi

# Create database directory
mkdir -p database

# Start Flask backend
echo ""
echo "🚀 Starting AI Krishi backend server..."
echo "   URL: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

cd backend
python app.py
