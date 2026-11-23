@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dependencies
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    python --version >nul 2>&1
    if errorlevel 1 goto missing_python
    python -m venv .venv
)
if errorlevel 1 goto failed
:dependencies
".venv\Scripts\python.exe" -c "from PySide6.QtWidgets import QApplication" >nul 2>&1
if not errorlevel 1 goto launch
echo Setting up AI Text Summarizer for the first time...
echo This step needs an internet connection. Later launches work offline.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
:launch
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto failed
exit /b 0
:missing_python
echo Please install Python 3.10 or newer from https://www.python.org/downloads/
echo Select Add Python to PATH during installation, then run this file again.
pause
exit /b 1
:failed
echo.
echo The app could not start. Read the error above.
echo Check that Python 3.10 or newer is installed and try again.
pause
exit /b 1
