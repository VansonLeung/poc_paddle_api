#!/bin/bash

# PaddleOCR VL API - Startup Script

echo "🚀 Starting PaddleOCR VL API Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Using defaults..."
    echo "   Copy .env.example to .env to customize settings"
fi

# Start the server
echo ""
echo "🎉 Starting API server..."
echo "   Access API at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Use venv python explicitly
./venv/bin/python app.py
