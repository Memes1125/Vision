@echo off
REM Установка YOLO (Ultralytics + PyTorch CUDA). venv в ASCII-пути.
cd /d "%~dp0.."
set "VENV=%LOCALAPPDATA%\vision\yolo-venv"

if not exist "%VENV%\Scripts\python.exe" (
    echo Создаю виртуальное окружение: %VENV%
    py -3.12 -m venv "%VENV%"
    if errorlevel 1 (
        echo Не удалось создать venv. Установите Python 3.12+.
        pause
        exit /b 1
    )
)

echo Обновляю pip...
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip

echo Устанавливаю PyTorch с CUDA...
"%VENV%\Scripts\pip.exe" install torch torchvision --index-url https://download.pytorch.org/whl/cu124
if errorlevel 1 (
    echo Не удалось поставить CUDA-сборку, пробую стандартный pip...
    "%VENV%\Scripts\pip.exe" install torch torchvision
)

echo Устанавливаю Ultralytics и зависимости...
"%VENV%\Scripts\pip.exe" install -r requirements-yolo.txt
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo Проверка GPU...
"%VENV%\Scripts\python.exe" -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"

echo.
echo Готово.
echo   Подготовка датасета: scripts\prepare_yolo_dataset.bat
echo   Обучение:            scripts\train_yolo.bat
pause
