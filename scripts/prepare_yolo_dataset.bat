@echo off
cd /d "%~dp0.."
set "VENV=%LOCALAPPDATA%\vision\yolo-venv"
if not exist "%VENV%\Scripts\python.exe" (
    echo Сначала: scripts\setup_yolo.bat
    pause
    exit /b 1
)
"%VENV%\Scripts\python.exe" "%~dp0prepare_yolo_dataset.py" %*
pause
