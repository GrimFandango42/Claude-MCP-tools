@echo off
REM Firecrawl MCP wrapper for Windows
REM This script fixes environment variable issues and ensures proper initialization

SET FIRECRAWL_API_KEY=fc-54936f41b9894673bacd606878ce2d54
SET NPM_CONFIG_CACHE=%APPDATA%\npm-cache

REM Clear any existing APPDATA environment variable to avoid conflicts
SET APP_DATA_TEMP=%APPDATA%
SET APPDATA=

echo Starting Firecrawl MCP Server...

REM Run the firecrawl-mcp package
npx -y firecrawl-mcp

REM Restore APPDATA if needed
SET APPDATA=%APP_DATA_TEMP%
