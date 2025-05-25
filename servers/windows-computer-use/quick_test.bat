@echo off
echo Testing Windows Computer Use MCP Server...
cd /d "%~dp0"

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Running test suite...
python test_server.py

echo.
echo Test completed.
pause
