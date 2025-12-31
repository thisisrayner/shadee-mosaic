@echo off
REM Clear any lingering VIRTUAL_ENV variables that might confuse python
set VIRTUAL_ENV=
cd /d "%~dp0"
echo Starting Shadee Mosaic (Global Python)...
python src/ai/app.py
pause
