@echo off
echo Installing MCP servers for Claude Desktop...

:: Create directories if they don't exist
if not exist "%APPDATA%\Claude" mkdir "%APPDATA%\Claude"

:: Install NPM packages globally
echo Installing MCP server packages...
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sqlite
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-puppeteer
npm install -g @modelcontextprotocol/server-filesystem

echo MCP server installation completed.
echo Please restart Claude Desktop to apply the changes.
pause
