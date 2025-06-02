@echo off
REM Launcher for Claude Code Integration MCP Server
cd /d "C:\AI_Projects\Claude-MCP-tools\servers\claude-code-integration-mcp"
set CLAUDE_CODE_MOCK=true
set PYTHONPATH=C:\AI_Projects\Claude-MCP-tools\servers\claude-code-integration-mcp\src
"C:\Users\Nithin\AppData\Local\Programs\Python\Python312\python.exe" "src\claude_code_integration\server_fixed.py"