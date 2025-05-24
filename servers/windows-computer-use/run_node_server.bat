@echo off
REM Windows Computer Use MCP Server - Node.js Implementation Launcher
REM This script launches the Node.js version of the server

echo [windows-computer-use] Starting Node.js Windows Computer Use MCP Server... 1>&2

REM Set script directory as working directory
cd /d "%~dp0"

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [windows-computer-use] ERROR: Node.js is not installed or not in PATH 1>&2
    exit /b 1
)

REM Launch the server
echo [windows-computer-use] Launching Node.js server... 1>&2
node server.js

REM Keep stdin open to prevent premature termination
<nul