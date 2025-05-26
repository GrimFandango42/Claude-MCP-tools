@echo off
rem Firecrawl MCP Server Wrapper
rem This batch file ensures the Node.js process stays alive

echo Starting Firecrawl MCP Server...

rem Set environment variables
set FIRECRAWL_API_KEY=fc-54936f41b9894673bacd606878ce2d54
set npm_config_cache=C:\Users\Nithin\AppData\Local\firecrawl-cache

rem Preserve original APPDATA and clear it for the Node process
set ORIGINAL_APPDATA=%APPDATA%
set APPDATA=

rem Run the Node.js process with stdio inheritance
node C:\AI_Projects\Claude-MCP-tools\firecrawl_standalone.js

rem Restore original APPDATA
set APPDATA=%ORIGINAL_APPDATA%
