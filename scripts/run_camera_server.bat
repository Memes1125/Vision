@echo off
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo Создайте venv и установите: pip install -r requirements.txt
    pause
    exit /b 1
)
echo Запуск сервера камер на этом ПК (для удаленного доступа по IP)
.venv\Scripts\python.exe scripts\camera_server.py --host 0.0.0.0 --port 8765 --cameras 0,1,2
pause
