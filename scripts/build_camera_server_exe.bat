@echo off
REM Сборка папки dist\camera_server\ для ПК с камерами (без Python на целевом ПК)
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo Create venv: python -m venv .venv
    pause
    exit /b 1
)
echo Installing build deps (numpy 1.x + opencv)...
.venv\Scripts\pip install -q -r requirements-build.txt
echo Building onedir (more stable than onefile on remote PCs)...
.venv\Scripts\pyinstaller.exe --noconfirm --onedir --console ^
    --name camera_server ^
    --collect-all cv2 ^
    --collect-all numpy ^
    --hidden-import=cv2 ^
    scripts\camera_server.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)
echo.
copy /Y "dist\run_camera_server_exe.bat" "dist\camera_server\run_camera_server_exe.bat" >nul
echo OK: copy the WHOLE folder to the camera PC:
echo   dist\camera_server\
echo   (all files inside - not only .exe)
echo.
pause
