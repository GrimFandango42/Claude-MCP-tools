# Claude Desktop Agent MCP Server

A simple MCP (Model Context Protocol) server for Claude Desktop that provides screenshot capabilities.

## Features

- **Screenshot Capture**: Take screenshots of the current desktop
- **Windows Compatible**: Uses synchronous I/O for better Windows compatibility
- **MCP Protocol Compliant**: Follows the MCP 2024-11-05 specification
- **File Storage**: Screenshots are saved with timestamps

## Requirements

- Python 3.12 or higher
- pyautogui
- Pillow (PIL)

## Installation

1. Install dependencies:
```bash
pip install pyautogui pillow
```

2. The server is already configured in your Claude Desktop configuration.

## Usage

Once Claude Desktop is restarted, the server will be available. You can use the following tool:

### take_screenshot

Takes a screenshot of the current desktop.

**Parameters:**
- `name` (optional): Custom name for the screenshot file
- `width` (optional): Width in pixels (default: 1920)
- `height` (optional): Height in pixels (default: 1080)

**Example:**
```
Take a screenshot of the current desktop
Take a screenshot named "before_changes"
```

## File Structure

```
ClaudeDesktopAgent/
├── simple_mcp_server.py    # Main server implementation
├── simple_mcp_server.log   # Server logs
├── screenshots/            # Screenshot storage directory
└── README.md              # This file
```

## Troubleshooting

### Check Server Status
1. Look for the claude-desktop-agent in Claude Desktop's MCP servers list
2. Check if it shows as "connected" (green status)

### View Logs
Logs are stored in `simple_mcp_server.log` in the same directory as the server.

### Common Issues

**Server not starting:**
- Ensure Python 3.12 is installed at the specified path
- Check that pyautogui and PIL are installed
- Restart Claude Desktop after configuration changes

**Screenshots not working:**
- Ensure the screenshots directory exists and is writable
- Check that your display is accessible (not locked)
- Review the log file for specific errors

## Technical Details

- **Protocol**: JSON-RPC over stdio
- **MCP Version**: 2024-11-05
- **Communication**: Synchronous I/O (stdin/stdout)
- **Logging**: File-based logging to avoid stderr conflicts

## Development

To modify the server:
1. Edit `simple_mcp_server.py`
2. Test changes outside Claude first
3. Restart Claude Desktop to reload the server

### Adding New Tools

To add a new tool:
1. Add tool definition in `handle_tools_list()`
2. Implement handler in `handle_tools_call()`
3. Update this README with usage instructions
