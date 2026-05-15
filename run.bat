@echo off
title RifatCam Pro
cd /d "%~dp0desktop-client"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

python main.py
pause
