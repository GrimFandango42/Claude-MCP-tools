@echo off
echo [api-gateway] Starting API Gateway MCP Server... 1>&2
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo [api-gateway] Creating virtual environment... 1>&2
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo [api-gateway] Installing dependencies... 1>&2
pip install -r requirements.txt > nul 2>&1

REM Set Python path and environment
set PYTHONPATH=%~dp0
set PYTHONUNBUFFERED=1

REM Check for API keys
if "%OPENAI_API_KEY%"=="" (
    echo [api-gateway] WARNING: OPENAI_API_KEY environment variable not set 1>&2
)

if "%ANTHROPIC_API_KEY%"=="" (
    echo [api-gateway] WARNING: ANTHROPIC_API_KEY environment variable not set 1>&2
)

REM Run the MCP server
echo [api-gateway] Starting API Gateway MCP server... 1>&2
python server.py
