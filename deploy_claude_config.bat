@echo off
echo ========================================
echo Claude Desktop Configuration Deployment
echo ========================================

echo.
echo Deploying MCP Server Configuration...

REM Get the username
set USERNAME=%USERNAME%

REM Define paths
set SOURCE_CONFIG=C:\AI_Projects\Claude-MCP-tools\ClaudeDesktopAgent\claude_desktop_config.json
set TARGET_DIR=C:\Users\%USERNAME%\AppData\Roaming\Claude
set TARGET_CONFIG=%TARGET_DIR%\claude_desktop_config.json

echo Source: %SOURCE_CONFIG%
echo Target: %TARGET_CONFIG%

REM Create target directory if it doesn't exist
if not exist "%TARGET_DIR%" (
    echo Creating Claude configuration directory...
    mkdir "%TARGET_DIR%"
)

REM Backup existing configuration if it exists
if exist "%TARGET_CONFIG%" (
    echo Backing up existing configuration...
    copy "%TARGET_CONFIG%" "%TARGET_CONFIG%.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
)

REM Copy new configuration
echo Deploying new configuration...
copy "%SOURCE_CONFIG%" "%TARGET_CONFIG%"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Configuration deployed successfully!
    echo.
    echo Next steps:
    echo 1. Restart Claude Desktop completely
    echo 2. Check logs at: %TARGET_DIR%\logs\
    echo 3. Test Computer Use and Docker tools
    echo.
    echo Configuration includes:
    echo - Windows Computer Use (computer_20250124, text_editor_20250429, bash_20250124)
    echo - Docker Orchestration (19+ Docker management tools)
    echo - Financial Datasets (company data, stock prices)
    echo - Knowledge Memory (persistent notes and memory)
    echo - N8n Workflow Generator (automation workflows)
    echo - Filesystem (file operations)
) else (
    echo ❌ Configuration deployment failed!
    echo Check file paths and permissions.
)

echo.
echo Press any key to continue...
pause >nul
