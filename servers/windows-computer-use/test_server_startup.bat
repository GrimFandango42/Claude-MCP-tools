@echo off
REM Quick test of the Computer Use server

echo Testing Computer Use server startup...
cd /d "%~dp0"

REM Activate virtual environment
if exist ".venv" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found, using system Python
)

REM Test server startup
echo Testing server.py...
python -c "import sys; print('Python executable:', sys.executable)"
python -c "import pyautogui; print('pyautogui available:', pyautogui.__version__)"
python -c "from PIL import ImageGrab; print('PIL ImageGrab available')"

echo.
echo If no errors above, the server should work. 
echo You may need to restart Claude Desktop to load the new launcher.
pause
