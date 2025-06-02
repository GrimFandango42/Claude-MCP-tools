# Windows Fixed MCP Server for Claude Desktop Agent

## Overview
This is a Windows-compatible version of the Claude Desktop Agent MCP server that fixes the async stdin/stdout issues that occur on Windows systems.

## The Problem
The original server used Python's asyncio to handle stdin/stdout, which doesn't work properly on Windows due to how Windows handles pipes differently from Unix systems. This resulted in the error:
```
OSError: [WinError 6] The handle is invalid
```

## The Solution
This Windows-compatible version uses synchronous I/O instead of async, which works reliably on Windows while maintaining full MCP protocol compatibility.

## Installation

1. **Ensure Python is installed** (Python 3.8 or higher)
   ```
   python --version
   ```

2. **Install required packages**:
   ```
   pip install pyautogui pillow
   ```

3. **The Claude Desktop configuration has been updated** to use the new server:
   - Path: `C:\Users\Nithin\AppData\Roaming\Claude\claude_desktop_config.json`
   - Server: `windows_fixed_mcp_server.py`

## Usage

### Method 1: Through Claude Desktop (Recommended)
1. Close Claude Desktop completely
2. Restart Claude Desktop
3. The server will start automatically
4. You can now use the screenshot tool in Claude

### Method 2: Manual Testing
1. Run the test script:
   ```
   python test_windows_server.py
   ```

2. Or start the server manually:
   ```
   python windows_fixed_mcp_server.py
   ```

### Method 3: Using the Batch File
1. Double-click `start_windows_fixed_server.bat`
2. This will check dependencies and start the server

## Available Tools

### take_screenshot
Captures a screenshot of your desktop and saves it to the `screenshots` directory.

**Parameters:**
- `name` (optional): Custom name for the screenshot
- `width` (optional): Width in pixels (default: 1920)
- `height` (optional): Height in pixels (default: 1080)

**Example usage in Claude:**
"Take a screenshot of my desktop"
"Take a screenshot and name it 'error_message'"

## Troubleshooting

### 1. Server Won't Start
- Check the log file: `windows_fixed_mcp_server.log`
- Ensure Python is in your PATH
- Verify pyautogui and PIL are installed

### 2. Screenshot Fails
- Make sure you have proper permissions
- Check if antivirus is blocking pyautogui
- Try running as administrator if needed

### 3. Claude Desktop Doesn't See the Server
- Restart Claude Desktop after configuration changes
- Check that the path in the config file is correct
- Look for errors in Claude Desktop's developer console (Ctrl+Shift+I)

## Log Files
- Server log: `C:\AI_Projects\Claude-MCP-tools\ClaudeDesktopAgent\windows_fixed_mcp_server.log`
- Screenshots directory: `C:\AI_Projects\Claude-MCP-tools\ClaudeDesktopAgent\screenshots\`

## Technical Details

### Key Changes from Original
1. Removed asyncio for stdin/stdout handling
2. Uses synchronous I/O with proper binary mode handling
3. Implements proper Windows pipe handling with msvcrt
4. Maintains full MCP protocol compatibility

### MCP Protocol Implementation
- Supports initialize, tools/list, and tools/call methods
- Proper JSON-RPC 2.0 message handling
- Error handling with appropriate error codes
- Notification support (notifications/initialized)

## Next Steps
After verifying the server works:
1. Restart Claude Desktop
2. Try using the screenshot tool
3. Check the screenshots directory for saved images

If you encounter any issues, check the log file first, as it contains detailed debugging information.
