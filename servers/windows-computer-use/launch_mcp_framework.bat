@echo off
REM Windows Computer Use MCP Server - MCP Framework Launch Script
REM Launches the Computer Use API compliant server

echo [windows-computer-use] Starting Computer Use MCP server... 1>&2

REM Set working directory
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [windows-computer-use] Creating virtual environment... 1>&2
    python -m venv .venv
    if errorlevel 1 (
        echo [windows-computer-use] ERROR: Failed to create virtual environment 1>&2
        exit /b 1
    )
)

REM Activate virtual environment
echo [windows-computer-use] Activating virtual environment... 1>&2
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [windows-computer-use] ERROR: Failed to activate virtual environment 1>&2
    exit /b 1
)

REM Install dependencies
echo [windows-computer-use] Installing dependencies... 1>&2
pip install --quiet pyautogui>=0.9.54 pillow>=10.0.0 pywin32>=306
if errorlevel 1 (
    echo [windows-computer-use] WARNING: Some dependencies may have failed to install 1>&2
)

REM Set environment variables
set PYTHONPATH=%~dp0
set PYTHONUNBUFFERED=1

REM Launch the server
echo [windows-computer-use] Launching Computer Use server (server.py)... 1>&2
python server.py

REM If we reach here, the server has exited
echo [windows-computer-use] Server process ended. 1>&2
