@echo off
REM Запуск labelImg
cd /d "%~dp0.."
set "VENV=%LOCALAPPDATA%\vision\venv"

if not exist "%VENV%\Scripts\labelImg.exe" (
    echo Сначала установите: scripts\setup_labelimg.bat
    pause
    exit /b 1
)

"%VENV%\Scripts\python.exe" "%~dp0patch_labelimg.py" >nul 2>&1

REM Опционально: run_labelimg.bat dataset\images dataset\classes.txt
if "%~1"=="" (
    start "" "%VENV%\Scripts\labelImg.exe"
) else if "%~2"=="" (
    start "" "%VENV%\Scripts\labelImg.exe" "%~1"
) else (
    start "" "%VENV%\Scripts\labelImg.exe" "%~1" "%~2"
)
