@echo off
cd /d "%~dp0"
echo Activating virtual environment...
if exist ".venv2\Scripts\activate.bat" (
    call .venv2\Scripts\activate.bat
) else (
    echo Error: .venv2\Scripts\activate.bat not found!
    echo Attempting to recreate venv...
    rmdir /s /q .venv2
    python -m venv .venv2
    call .venv2\Scripts\activate.bat
)

echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Pip install failed!
    pause
    exit /b %ERRORLEVEL%
)

echo Starting Shadee Mosaic...
python src/ai/app.py
pause
