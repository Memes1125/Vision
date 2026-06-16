@echo off
REM Установка labelImg (один раз). venv — в ASCII-пути, иначе PyQt5 на Windows падает.
cd /d "%~dp0.."
set "VENV=%LOCALAPPDATA%\vision\venv"

if not exist "%VENV%\Scripts\python.exe" (
    echo Создаю виртуальное окружение: %VENV%
    py -3.12 -m venv "%VENV%"
    if errorlevel 1 (
        echo Не удалось создать venv. Установите Python 3.12+.
        pause
        exit /b 1
    )
)

echo Устанавливаю пакеты...
"%VENV%\Scripts\pip.exe" install -r requirements-label.txt
if errorlevel 1 (
    pause
    exit /b 1
)

echo Патч для Python 3.12...
"%VENV%\Scripts\python.exe" "%~dp0patch_labelimg.py"
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo Готово. Запуск: scripts\run_labelimg.bat
pause
