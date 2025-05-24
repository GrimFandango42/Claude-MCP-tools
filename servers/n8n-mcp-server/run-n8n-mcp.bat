@echo off
REM N8n MCP Server Startup Script
REM This script starts the N8n MCP server for Claude Desktop integration

echo Starting N8n MCP Server...
echo.

REM Change to the server directory
cd /d "%~dp0"

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

REM Start the server
echo Starting server on STDIO...
echo Press Ctrl+C to stop the server
echo.

node server.js

pause
