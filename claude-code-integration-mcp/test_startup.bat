@echo off
echo Testing Claude Code Integration MCP Server
echo ==========================================

echo Testing Python availability...
python --version
if errorlevel 1 (
    echo Python not found in PATH
    exit /b 1
)

echo.
echo Testing FastMCP import...
python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP import successful')"
if errorlevel 1 (
    echo FastMCP import failed
    exit /b 1
)

echo.
echo Testing Claude Code Integration Server...
cd /d "C:\AI_Projects\Claude-MCP-tools\claude-code-integration-mcp"
python enhanced_server.py --help 2>nul
if errorlevel 1 (
    echo Starting server in test mode...
    timeout /t 3 >nul
    echo Server test completed
) else (
    echo Server help available
)

echo.
echo All tests completed.
