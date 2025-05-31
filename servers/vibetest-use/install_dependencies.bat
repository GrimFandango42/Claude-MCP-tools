@echo off
echo Installing Vibetest Dependencies...

REM Install Python packages using Windows Python
pip install browser-use langchain-google-genai playwright screeninfo fastmcp

REM Install Playwright browsers
python -m playwright install chromium

REM Install the vibetest package in development mode
pip install -e .

echo.
echo ✅ Installation complete!
echo.
echo Next steps:
echo 1. Add your GOOGLE_API_KEY to the Claude Desktop config
echo 2. Restart Claude Desktop
echo 3. Start testing with the vibetest tools!
echo.
pause
