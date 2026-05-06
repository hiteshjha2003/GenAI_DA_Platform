@echo off
REM GenAI Data Analytics Platform - Backend Server Startup Script (Windows)
REM This script starts the FastAPI backend server

echo.
echo ============================================
echo GenAI Data Analytics Platform
echo Backend Server Startup Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

REM Change to backend directory
cd /d "%~dp0"

echo Installing/updating dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================
echo Starting Backend Server...
echo ============================================
echo.
echo API will be available at: http://localhost:8000
echo Health check at: http://localhost:8000/health
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
