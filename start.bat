@echo off
REM PaddleOCR VL API - Startup Script for Windows

echo Starting PaddleOCR VL API Server...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed
)

REM Check if .env exists
if not exist ".env" (
    echo .env file not found. Using defaults...
    echo Copy .env.example to .env to customize settings
)

REM Start the server
echo.
echo Starting API server...
echo Access API at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
