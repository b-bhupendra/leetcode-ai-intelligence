# LeetCode AI Intelligence - PowerShell Quickstart Script (D:\lc_practice)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  LeetCode AI Intelligence - PowerShell Launcher" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Virtual Environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[1/3] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Dependencies
Write-Host "[2/3] Checking dependencies from requirements.txt..." -ForegroundColor Yellow
& .venv\Scripts\pip install -r requirements.txt

# 3. Launch Web Application
Write-Host "[3/3] Starting Web Application at http://localhost:8000 ..." -ForegroundColor Green
& .venv\Scripts\python web_app.py
