@echo off
echo =======================================================
echo   LeetCode AI Intelligence - One-Click Launcher (D:\lc_practice)
echo =======================================================

cd /d "%~dp0"

REM Check if python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

REM Setup virtual environment if not present
if not exist ".venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment (.venv)...
    python -m venv .venv
)

REM Install dependencies
echo [2/4] Checking and installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

REM Check and train models if not already trained
if not exist "models\company_classifier.joblib" (
    echo [3/4] Auto-training ML models on dataset (~15 seconds)...
    python -c "import ml_models; ml_models.main()"
) else (
    echo [3/4] Pre-trained models verified.
)

REM Launch Web App
echo [4/4] Starting LeetCode Intelligence Dashboard at http://localhost:8000 ...
python web_app.py

pause
