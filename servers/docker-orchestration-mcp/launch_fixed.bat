@echo off
REM Docker Orchestration MCP Server - Fixed Launch Script
REM Proper MCP framework implementation with enhanced error handling

echo [docker-orchestration] Starting Docker Orchestration MCP server... 1>&2

REM Set working directory
cd /d "%~dp0"

REM Check if Docker is running
echo [docker-orchestration] Checking Docker daemon... 1>&2
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [docker-orchestration] ERROR: Docker daemon is not running. Please start Docker Desktop. 1>&2
    exit /b 1
)
echo [docker-orchestration] Docker daemon is running 1>&2

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [docker-orchestration] Creating virtual environment... 1>&2
    python -m venv .venv
    if errorlevel 1 (
        echo [docker-orchestration] ERROR: Failed to create virtual environment 1>&2
        exit /b 1
    )
)

REM Activate virtual environment
echo [docker-orchestration] Activating virtual environment... 1>&2
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [docker-orchestration] ERROR: Failed to activate virtual environment 1>&2
    exit /b 1
)

REM Upgrade pip and install dependencies
echo [docker-orchestration] Installing/updating dependencies... 1>&2
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [docker-orchestration] WARNING: Some dependencies may have failed to install 1>&2
)

REM Set environment variables for proper MCP operation
set PYTHONPATH=%~dp0;%~dp0\src
set PYTHONUNBUFFERED=1

REM Launch the server
echo [docker-orchestration] Launching Docker Orchestration server (src\server.py)... 1>&2
python src\server.py

REM If we reach here, the server has exited
echo [docker-orchestration] Server process ended. 1>&2
