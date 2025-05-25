@echo off
echo [containerized-computer-use] Starting Containerized Computer Use MCP Server... 1>&2
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo [containerized-computer-use] Creating virtual environment... 1>&2
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo [containerized-computer-use] Installing dependencies... 1>&2
pip install -r requirements.txt > nul 2>&1

REM Set Python path
set PYTHONPATH=%~dp0
set PYTHONUNBUFFERED=1

REM Check Docker status
docker ps > nul 2>&1
if errorlevel 1 (
    echo [containerized-computer-use] WARNING: Docker is not running. Please start Docker Desktop. 1>&2
)

REM Run the MCP server
echo [containerized-computer-use] Starting MCP server... 1>&2
python containerized_mcp_server.py
