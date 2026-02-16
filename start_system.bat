@echo off
echo ========================================
echo Healthcare Management System Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required directories exist
if not exist "medml-backend" (
    echo ERROR: medml-backend directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "medml-frontend" (
    echo ERROR: medml-frontend directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d medml-backend && python run.py"
echo Backend server starting in new window...
echo.

echo Waiting for backend to initialize...
timeout /t 8 /nobreak > nul
echo.

echo Starting Frontend...
start "Frontend" cmd /k "cd /d medml-frontend && streamlit run app.py --server.port 8501"
echo Frontend starting in new window...
echo.

echo ========================================
echo System Startup Complete!
echo ========================================
echo.
echo Backend Server: http://127.0.0.1:5000
echo Frontend App:   http://localhost:8501
echo.
echo Default Credentials:
echo Admin:  admin / Admin123!
echo Patient: 12345678901234 / 12345678901234@Default123
echo.
echo Check the opened command windows for any errors.
echo Close this window when done.
echo.
pause