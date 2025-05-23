@echo off
rem Firecrawl MCP Server Python Wrapper
rem This batch file ensures the Python process stays alive

echo Starting Firecrawl MCP Python Server...

rem Set environment variables
set FIRECRAWL_API_KEY=fc-54936f41b9894673bacd606878ce2d54

rem Preserve original APPDATA and clear it for the process
set ORIGINAL_APPDATA=%APPDATA%
set APPDATA=

rem Run the Python script with stdio inheritance
python C:\AI_Projects\Claude-MCP-tools\firecrawl_mcp.py

rem If Python exits, restart it (this creates an infinite loop)
echo Restarting Python MCP server...
goto :eof

rem Restore original APPDATA (this won't execute due to the goto)
set APPDATA=%ORIGINAL_APPDATA%
