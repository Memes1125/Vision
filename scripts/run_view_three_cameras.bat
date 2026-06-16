@echo off
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe scripts\view_three_cameras.py %*
) else (
    python scripts\view_three_cameras.py %*
)
