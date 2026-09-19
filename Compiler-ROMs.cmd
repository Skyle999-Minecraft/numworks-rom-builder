@echo off
setlocal
python -B "%~dp0rom-builder\app.py"
if errorlevel 1 (
    echo.
    echo Impossible de lancer ROM Builder. Verifiez Python 3.10+ avec tkinter.
    pause
)