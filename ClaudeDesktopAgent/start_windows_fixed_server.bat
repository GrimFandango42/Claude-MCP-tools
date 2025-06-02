@echo off
REM Start Windows-Compatible Fixed MCP Server

echo Starting Windows-Compatible Fixed MCP Server...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import pyautogui" >nul 2>&1
if errorlevel 1 (
    echo Installing pyautogui...
    pip install pyautogui
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow...
    pip install Pillow
)

echo.
echo Starting server...
echo To stop the server, press Ctrl+C
echo.

REM Run the Windows-compatible server
python windows_fixed_mcp_server.py

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start!
    echo Check windows_fixed_mcp_server.log for details.
)

pause
