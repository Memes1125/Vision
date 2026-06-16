@echo off
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo Создайте venv и установите: pip install -r requirements.txt
    pause
    exit /b 1
)
REM IP ПК с камерами
.venv\Scripts\python.exe scripts\camera_client.py --host 192.168.0.43 --view
pause
