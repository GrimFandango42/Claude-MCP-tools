@echo off

rem Completely silent batch file for strict JSON-RPC compliance
rem All status output redirected to NUL

rem Set environment variables silently
set "FIRECRAWL_API_KEY=fc-54936f41b9894673bacd606878ce2d54" >nul 2>&1

rem Launch Node.js directly with no batch file output
node C:\AI_Projects\Claude-MCP-tools\firecrawl_optimized.js
