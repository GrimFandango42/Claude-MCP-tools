# Claude Desktop Configuration Update Instructions

## ⚠️ IMPORTANT: Manual Update Required

The Claude Desktop configuration needs to be updated to reflect our server consolidation.

## Removed Servers (DELETE these from your config):
- ❌ `code-analysis`
- ❌ `code-quality` 
- ❌ `refactoring`
- ❌ `test-intelligence`
- ❌ `dependency-analysis`
- ❌ `code-intelligence-core`
- ❌ `knowledge-memory`
- ❌ `claude-desktop-agent`

## Updated Servers (CHANGE these entries):

### 1. Claude Code Integration (UPDATE PATH)
```json
"claude-code-integration": {
  "command": "python",
  "args": ["C:/AI_Projects/Claude-MCP-tools/servers/claude-code-integration-mcp/src/claude_code_integration/server_fixed.py"],
  "env": {
    "CLAUDE_CODE_MOCK": "true"
  },
  "description": "Claude Code CLI integration (fixed version)",
  "keepAlive": true,
  "stderrToConsole": true
}
```

### 2. AgenticSeek (UPDATE PATH)
```json
"agenticseek": {
  "command": "python",
  "args": ["C:/AI_Projects/Claude-MCP-tools/servers/agenticseek-mcp/server_fastmcp_fixed.py"],
  "env": {
    "OPENAI_API_KEY": "your-key-here",
    "GOOGLE_API_KEY": "your-key-here"
  },
  "description": "Multi-provider AI routing with cost optimization",
  "keepAlive": true,
  "stderrToConsole": true
}
```

## New Servers (ADD these entries):

### 1. Code Formatter
```json
"code-formatter": {
  "command": "python",
  "args": ["C:/AI_Projects/Claude-MCP-tools/servers/code-formatter-mcp/server.py"],
  "description": "Simple code formatting (black, prettier)",
  "keepAlive": true,
  "stderrToConsole": true
}
```

### 2. Security Scanner
```json
"security-scanner": {
  "command": "python",
  "args": ["C:/AI_Projects/Claude-MCP-tools/servers/security-scanner-mcp/server.py"],
  "description": "Dependency vulnerability scanning",
  "keepAlive": true,
  "stderrToConsole": true
}
```

## Update Steps:

1. **Open Claude Desktop config**:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Remove the 8 deleted server entries**

3. **Update the 2 server paths** (claude-code-integration and agenticseek)

4. **Add the 2 new server entries** (code-formatter and security-scanner)

5. **Save the file**

6. **Restart Claude Desktop**

## Alternative: Use the Consolidated Config

A complete, updated configuration is available at:
`claude_desktop_config_consolidated.json`

You can review this file and merge the relevant entries into your existing config.

## Verification

After restarting Claude Desktop:
1. Check that removed servers are no longer listed
2. Verify new servers show as "connected"
3. Test a simple command like: "Format a Python file"

## Troubleshooting

If servers don't connect:
1. Check file paths are correct for your system
2. Ensure Python is in PATH
3. Install FastMCP: `pip install fastmcp`
4. Check logs at `%APPDATA%\Claude\logs\`