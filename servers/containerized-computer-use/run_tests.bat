@echo off
echo Running Containerized Computer Use MCP Tests...
echo =========================================

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the test
echo.
echo Starting tests...
echo.
python test_complete_server.py

pause
