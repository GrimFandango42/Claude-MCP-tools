@echo off
echo Windows Computer Use MCP Server - Quick Test
echo ==========================================
echo.

echo Step 1: Testing virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)
echo ✓ Virtual environment exists

echo.
echo Step 2: Testing Python dependencies...
.venv\Scripts\python.exe -c "import pyautogui; print('✓ pyautogui package available')"
if %errorlevel% neq 0 (
    echo WARNING: pyautogui package may need installation
)

.venv\Scripts\python.exe -c "from PIL import Image; print('✓ PIL package available')"
if %errorlevel% neq 0 (
    echo WARNING: PIL package may need installation
)

echo.
echo Step 3: Testing server module...
.venv\Scripts\python.exe -c "from server import ComputerUseAPI; print('✓ Server module imports successfully')"
if %errorlevel% neq 0 (
    echo ERROR: Server module import failed
    pause
    exit /b 1
)

echo.
echo Step 4: Testing basic Computer Use API...
.venv\Scripts\python.exe -c "from server import ComputerUseAPI; api = ComputerUseAPI(); print('✓ Computer Use API initializes successfully')"
if %errorlevel% neq 0 (
    echo ERROR: Computer Use API initialization failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✓ Computer Use server appears to be working.
echo.
echo Current implementation uses manual JSON-RPC protocol.
echo Consider upgrading to MCP framework for better reliability.
echo.
echo To start the server:
echo   launch_mcp_framework.bat
echo.
echo To test with Claude Desktop:
echo   1. Restart Claude Desktop
echo   2. Try using Computer Use tools
echo ==========================================

pause
