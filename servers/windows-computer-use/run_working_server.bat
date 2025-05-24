@echo off
REM Windows Computer Use MCP Server - Known Working Version Launcher
REM This script runs the previously working Computer Use API compliant server

echo [windows-computer-use] Starting known working Windows Computer Use MCP Server... 1>&2

REM Set script directory as working directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo [windows-computer-use] Creating virtual environment... 1>&2
    python -m venv .venv
    if errorlevel 1 (
        echo [windows-computer-use] ERROR: Failed to create virtual environment 1>&2
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [windows-computer-use] ERROR: Failed to activate virtual environment 1>&2
    exit /b 1
)

REM Install dependencies
echo [windows-computer-use] Installing dependencies... 1>&2
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [windows-computer-use] ERROR: Failed to install dependencies 1>&2
    exit /b 1
)

REM Launch the known working server
echo [windows-computer-use] Launching known working server... 1>&2
python server_computer_use_api.py <nul

REM Keep stdin open to prevent premature termination
