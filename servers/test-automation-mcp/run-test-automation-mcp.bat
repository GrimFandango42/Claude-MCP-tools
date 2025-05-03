@echo off
REM Test Automation MCP Server Launch Script
REM This batch file handles environment setup and launches the MCP server

SETLOCAL EnableDelayedExpansion

REM Set up environment variables
SET TEST_AUTOMATION_ARTIFACTS_DIR=C:\AI_Projects\Claude-MCP-tools\servers\test-automation-mcp\artifacts
SET PLAYWRIGHT_BROWSERS_PATH=0

REM Create the artifacts directory if it doesn't exist
IF NOT EXIST "%TEST_AUTOMATION_ARTIFACTS_DIR%" (
  MKDIR "%TEST_AUTOMATION_ARTIFACTS_DIR%"
  ECHO Created artifacts directory: %TEST_AUTOMATION_ARTIFACTS_DIR%
)

REM Ensure Playwright is installed
IF NOT EXIST "%APPDATA%\npm\node_modules\@playwright\test" (
  ECHO Installing Playwright...
  npx playwright install --with-deps chromium
)

REM Launch the MCP server
ECHO Starting Test Automation MCP Server...
node "%~dp0server.js"

ECHO Server stopped with exit code %ERRORLEVEL%

ENDLOCAL