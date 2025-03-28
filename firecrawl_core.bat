@echo off
rem Firecrawl MCP Server - Windows Optimized Launcher

echo Starting Firecrawl MCP Server...

rem Create local directory for API key storage if it doesn't exist
if not exist "%USERPROFILE%\.firecrawl" mkdir "%USERPROFILE%\.firecrawl"

rem Set environment variables with proper Windows path handling
rem This prevents path-related issues in Windows environments
set "FIRECRAWL_API_KEY=fc-54936f41b9894673bacd606878ce2d54"
set "NODE_ENV=production"

rem Isolate potentially problematic environment variables
set "ORIGINAL_APPDATA=%APPDATA%"
set "APPDATA="

rem Run Node.js with explicit stdio inheritance flags
node C:\AI_Projects\Claude-MCP-tools\firecrawl_core.js

rem Restore environment
set "APPDATA=%ORIGINAL_APPDATA%"

echo MCP Server process exited.
