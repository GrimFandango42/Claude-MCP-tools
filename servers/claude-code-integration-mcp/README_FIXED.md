# Claude Code Integration MCP Server (Fixed)

## Overview

This MCP server provides integration between Claude Desktop and Claude Code CLI, enabling hybrid AI development workflows.

## Status

The original server had issues with the MCP package. This fixed version:
- Uses FastMCP framework (more reliable)
- Provides proper error handling
- Works with or without Claude Code CLI installed
- Includes mock mode for testing

## Installation

```bash
cd servers/claude-code-integration-mcp
pip install -e .
```

## Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "claude-code-integration": {
    "command": "python",
    "args": ["/path/to/servers/claude-code-integration-mcp/src/claude_code_integration/server_fixed.py"],
    "description": "Claude Code CLI integration for hybrid workflows"
  }
}
```

## Features

### Tools Available

1. **execute_claude_code** - Run Claude Code CLI with any prompt
2. **check_claude_code_installation** - Verify CLI is installed
3. **analyze_project** - Analyze a codebase
4. **delegate_coding_task** - Delegate implementation tasks
5. **run_claude_code_interactive** - Start interactive sessions

### Mock Mode

If Claude Code CLI is not installed, set environment variable:
```bash
CLAUDE_CODE_MOCK=true
```

## Usage Examples

```python
# Check if Claude Code CLI is installed
check_claude_code_installation()

# Execute a simple command
execute_claude_code("Create a Python hello world script")

# Analyze a project
analyze_project("/path/to/my/project")

# Delegate a coding task
delegate_coding_task(
    task_description="Implement a REST API for user management",
    context="Using FastAPI and SQLAlchemy",
    constraints="Follow RESTful best practices"
)
```

## Troubleshooting

### Common Issues

1. **"Claude Code CLI not installed"**
   - Install from: https://github.com/anthropics/claude-code
   - Or use mock mode for testing

2. **Import errors**
   - Make sure FastMCP is installed: `pip install fastmcp`

3. **Permission errors**
   - Ensure Claude Desktop has permission to execute Python

## Differences from Original

- Uses FastMCP instead of raw MCP SDK
- Simpler architecture
- Better error handling
- No complex session management (can be added if needed)
- Direct CLI execution instead of API mock