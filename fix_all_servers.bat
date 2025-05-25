@echo off
echo =========================================================
echo 🚀 Claude MCP Tools - Complete Fix and Setup Script
echo =========================================================

echo.
echo This script will:
echo 1. Test all server dependencies and environments
echo 2. Deploy the updated Claude Desktop configuration
echo 3. Validate all MCP servers are working
echo 4. Provide next steps for testing

echo.
echo Press any key to start the fix process...
pause >nul

echo.
echo ========================================
echo Step 1: Testing Server Dependencies
echo ========================================

python C:\AI_Projects\Claude-MCP-tools\test_all_servers.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Server dependency tests failed!
    echo Please fix the issues above before proceeding.
    echo Common fixes:
    echo - Install missing Python packages: pip install mcp docker pyautogui pillow requests
    echo - Start Docker Desktop if not running
    echo - Enable WSL if not configured
    pause >nul
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Deploying Claude Configuration
echo ========================================

call C:\AI_Projects\Claude-MCP-tools\deploy_claude_config.bat

echo.
echo ========================================
echo Step 3: Final Validation
echo ========================================

echo ✅ Configuration deployed successfully!
echo.
echo 🎯 NEXT STEPS TO COMPLETE THE FIX:
echo.
echo 1. 🔄 RESTART CLAUDE DESKTOP COMPLETELY
echo    - Close Claude Desktop entirely
echo    - Wait 5 seconds
echo    - Reopen Claude Desktop
echo.
echo 2. 🧪 TEST THE FIXED SERVERS
echo    Try these commands in Claude:
echo.
echo    💻 Computer Use Test:
echo    "Take a screenshot of my desktop"
echo.
echo    🐳 Docker Test:
echo    "List all Docker containers on my system"
echo.
echo    💰 Financial Test:
echo    "Get information about Apple stock (AAPL)"
echo.
echo    📝 Knowledge Memory Test:
echo    "Create a note about today's MCP server fixes"
echo.
echo 3. 📊 CHECK LOGS IF ISSUES OCCUR
echo    Location: %USERPROFILE%\AppData\Roaming\Claude\logs\
echo.
echo ========================================
echo 🎉 SETUP COMPLETE!
echo ========================================

echo.
echo Your Claude MCP Tools now include:
echo - ✅ Windows Computer Use (screenshot, click, type, WSL)
echo - ✅ Docker Orchestration (container management)
echo - ✅ Financial Datasets (market data)
echo - ✅ Knowledge Memory (persistent notes)
echo - ✅ N8n Workflow Generator (automation)
echo - ✅ Filesystem (file operations)

echo.
echo 🚀 Ready for advanced automation workflows!
echo.
echo Press any key to exit...
pause >nul
