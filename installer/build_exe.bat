@echo off
title RifatCam Pro - Building Desktop Executable
setlocal enabledelayedexpansion

echo ============================================
echo    RifatCam Pro - EXE Builder
echo ============================================
echo.

:: Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [*] Python found: 
python --version

:: Check for venv
if not exist "..\desktop-client\venv" (
    echo [*] Creating virtual environment...
    python -m venv "..\desktop-client\venv"
)

:: Activate venv
echo [*] Activating virtual environment...
call "..\desktop-client\venv\Scripts\activate.bat"

:: Install dependencies
echo [*] Installing dependencies...
pip install --upgrade pip
pip install -r "..\desktop-client\requirements.txt"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

:: Build EXE
echo.
echo [*] Building executable with PyInstaller...
cd /d "..\desktop-client"
pyinstaller --clean --onefile --windowed ^
    --name "RifatCamPro" ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "PyQt6" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "cv2" ^
    --hidden-import "numpy" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "requests" ^
    --hidden-import "qrcode" ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Executable built successfully!
echo Output: ..\desktop-client\dist\RifatCamPro.exe
echo.

:: Optional: Create installer with NSIS
if "%1"=="--installer" (
    echo [*] Creating NSIS installer...
    if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
        "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
        echo [*] Installer created: dist\RifatCamPro_Setup.exe
    ) else (
        echo [!] NSIS not found. Skipping installer creation.
    )
)

echo.
echo Build complete!
pause
