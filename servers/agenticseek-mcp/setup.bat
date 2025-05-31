@echo off
echo Creating AgenticSeek MCP Server virtual environment...

python -m venv .venv
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete!
echo.
echo To activate: .venv\Scripts\activate.bat
echo To test: python server.py
