@echo off
echo Installing Vibetest Dependencies...

REM Use Windows Python directly
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m pip install browser-use
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m pip install langchain-google-genai
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m pip install playwright
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m pip install screeninfo
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m pip install fastmcp

REM Install Playwright browsers
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m playwright install chromium

REM Install the vibetest package in development mode
cd /d "C:\AI_Projects\Claude-MCP-tools\servers\vibetest-use"
C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe -m pip install -e .

echo.
echo ✅ Installation complete!
echo.
echo Next steps:
echo 1. Add your GOOGLE_API_KEY to the Claude Desktop config
echo 2. Restart Claude Desktop  
echo 3. Start testing with: "Test https://example.com for UI bugs using 3 agents"
echo.
pause
