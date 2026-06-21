@echo off
cd /d "%~dp0.."
set "VENV=%LOCALAPPDATA%\vision\yolo-venv"
if not exist "%VENV%\Scripts\python.exe" (
    echo Сначала: scripts\setup_yolo.bat
    pause
    exit /b 1
)
"%VENV%\Scripts\python.exe" "%~dp0camera_yolo.py" --device cpu --cameras 1,2,3 %*
