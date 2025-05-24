@echo off
REM Windows Computer Use MCP Server Restart Script for Fixed Version
REM This script stops Claude Desktop, installs the fixed server, and restarts Claude Desktop

echo [windows-computer-use] Stopping Claude Desktop... 1>&2
wmic process where "name='Claude.exe'" delete >nul 2>&1
taskkill /f /im Claude.exe >nul 2>&1

REM Wait for process to terminate
timeout /t 2 /nobreak >nul

echo [windows-computer-use] Installing fixed server... 1>&2

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [windows-computer-use] ERROR: Failed to activate virtual environment 1>&2
    exit /b 1
)

REM Replace server.py with fixed version
echo [windows-computer-use] Backing up current server... 1>&2
copy /Y server.py server.py.bak >nul 2>&1

echo [windows-computer-use] Installing fixed server... 1>&2
copy /Y server_fixed.py server.py >nul 2>&1

echo [windows-computer-use] Restarting Claude Desktop... 1>&2
start "" "C:\Users\Nithin\AppData\Local\Programs\Claude\Claude.exe"

echo [windows-computer-use] Server update complete! 1>&2
echo [windows-computer-use] Please wait a moment for Claude Desktop to start 1>&2