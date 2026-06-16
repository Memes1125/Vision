@echo off
cd /d "%~dp0.."
set "VENV=%LOCALAPPDATA%\vision\yolo-venv"
if not exist "%VENV%\Scripts\python.exe" (
    echo Сначала: scripts\setup_yolo.bat
    pause
    exit /b 1
)
REM На Windows workers>0 часто падает: WinError 1455 (файл подкачки / память)
set OMP_NUM_THREADS=1
"%VENV%\Scripts\python.exe" "%~dp0train_yolo.py" %*
pause
