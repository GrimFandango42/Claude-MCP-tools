# Claude Desktop Setup Guide

## Prerequisites

- Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- Python 3.11 or higher
- Claude Desktop application installed
- Administrator/sudo access for system integration

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/claude-mcp-tools.git
cd claude-mcp-tools
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

Locate your Claude Desktop configuration file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add MCP server configurations:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "path/to/allowed/directory"],
      "description": "File system operations"
    },
    "github": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      },
      "description": "GitHub repository management"
    }
  }
}
```

### 4. Verify Installation

1. Restart Claude Desktop
2. Check MCP servers panel for connected servers
3. Test with: "List files in the current directory"

## Platform-Specific Servers

### Desktop-Only Servers
These require GUI access and won't work in Claude Code:

- **Windows Computer Use**: Desktop automation
- **Containerized Computer Use**: Isolated GUI automation
- **ScreenPilot**: Screen analysis
- **Playwright**: Browser automation

### Cross-Platform Servers
Work in both Claude Desktop and Claude Code:

- **Filesystem**: File operations
- **GitHub**: Repository management
- **SQLite**: Database operations
- All Code Intelligence servers

## Troubleshooting

### Server Not Connecting
1. Check logs at `%APPDATA%\Claude\logs`
2. Verify Python path in configuration
3. Ensure no firewall blocking

### Permission Errors
1. Run Claude Desktop as administrator (once)
2. Check file system permissions
3. Verify API tokens are valid

## Next Steps

- [Configure individual servers](../servers/README.md)
- [Learn about hybrid workflows](hybrid-workflows.md)
- [Security best practices](../architecture/security-model.md)
