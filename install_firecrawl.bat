@echo off
echo Installing firecrawl-mcp package...

rem Set cache directory to avoid APPDATA issues
set npm_config_cache=C:\Users\Nithin\AppData\Local\npm-cache

npm install -g firecrawl-mcp
