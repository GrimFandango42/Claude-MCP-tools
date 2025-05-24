@echo off
REM Test Minimal Windows Computer Use MCP Server
REM This script tests the minimal server implementation

echo [windows-computer-use] Starting minimal server test... 1>&2

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

REM Test the minimal server with an initialize request
echo [windows-computer-use] Testing minimal server... 1>&2
echo {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}} | python minimal_server.py

echo [windows-computer-use] Test complete. 1>&2