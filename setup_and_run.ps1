# LeetCode AI Intelligence - PowerShell Quickstart Script (D:\lc_practice)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  LeetCode AI Intelligence - PowerShell Launcher" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Virtual Environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[1/4] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Dependencies
Write-Host "[2/4] Checking dependencies from requirements.txt..." -ForegroundColor Yellow
& .venv\Scripts\pip install -r requirements.txt

# 3. Model Verification & Auto-training
if (-not (Test-Path "models\company_classifier.joblib")) {
    Write-Host "[3/4] Auto-training ML models on dataset (~15 seconds)..." -ForegroundColor Yellow
    & .venv\Scripts\python -c "import ml_models; ml_models.main()"
} else {
    Write-Host "[3/4] Pre-trained models verified." -ForegroundColor Green
}

# 4. Launch Web Application
Write-Host "[4/4] Starting Web Application at http://localhost:8000 ..." -ForegroundColor Green
& .venv\Scripts\python web_app.py
