@echo off
echo Restarting Windows Computer Use MCP Server...
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting server with current Python environment...
echo Virtual Environment: %VIRTUAL_ENV%
echo Python Version: 
python --version
echo.

echo Running server.py...
python server.py