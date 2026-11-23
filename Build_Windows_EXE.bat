@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run Start_Windows.bat once before building the executable.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install pyinstaller==6.17.0
if errorlevel 1 goto failed
".venv\Scripts\python.exe" build_desktop.py
if errorlevel 1 goto failed
echo.
echo Finished. Open dist\AI_Text_Summarizer\AI_Text_Summarizer.exe
echo To copy the app, copy the entire dist\AI_Text_Summarizer folder.
pause
exit /b 0
:failed
echo Build failed. Read the error above.
pause
exit /b 1
