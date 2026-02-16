# Healthcare Management System Startup Script (PowerShell)
# Run this script from the project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Healthcare Management System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required directories exist
if (-not (Test-Path "medml-backend")) {
    Write-Host "ERROR: medml-backend directory not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "medml-frontend")) {
    Write-Host "ERROR: medml-frontend directory not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d medml-backend && python run.py" -WindowStyle Normal
Write-Host "Backend server starting in new window..." -ForegroundColor Green
Write-Host ""

Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8
Write-Host ""

Write-Host "Starting Frontend..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d medml-frontend && streamlit run app.py --server.port 8501" -WindowStyle Normal
Write-Host "Frontend starting in new window..." -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "System Startup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend Server: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Frontend App:   http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Default Credentials:" -ForegroundColor Yellow
Write-Host "Admin:  admin / Admin123!" -ForegroundColor White
Write-Host "Patient: 12345678901234 / 12345678901234@Default123" -ForegroundColor White
Write-Host ""
Write-Host "Check the opened command windows for any errors." -ForegroundColor Yellow
Write-Host "Close this window when done." -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
