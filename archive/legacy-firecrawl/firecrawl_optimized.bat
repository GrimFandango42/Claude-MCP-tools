@echo off
rem Optimized Firecrawl MCP Server with minimal logging

rem Redirect echo to stderr to avoid breaking JSON-RPC protocol
echo Starting Optimized Firecrawl MCP Server... 1>&2

rem Set required environment variables
set FIRECRAWL_API_KEY=fc-54936f41b9894673bacd606878ce2d54

rem Run the optimized implementation
node C:\AI_Projects\Claude-MCP-tools\firecrawl_optimized.js
