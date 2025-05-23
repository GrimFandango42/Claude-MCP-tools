# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

### Python MCP Servers (servers/ directory)
- **Setup**: `pip install -e .` or `uv sync` in each server directory
- **Run server**: `python server.py` (FastMCP servers use stdio transport)
- **Testing**: `pytest` (when test dependencies included in pyproject.toml)
- **Linting**: `black .` and `isort .` (for servers with dev dependencies)

### Node.js MCP Servers
- **Setup**: `npm install` in server directory
- **Run server**: `npm start` or `node server.js`
- **Testing**: `npm test`

### FastAPI Applications (ClaudeDesktopAgent, ClaudeDesktopBridge)
- **Setup**: `pip install -r requirements.txt`
- **Run**: `python app/main.py` or `uvicorn app.main:app --reload`
- **Testing**: `pytest tests/`
- **UI (Bridge only)**: `streamlit run app/ui/streamlit_app.py`

## MCP Server Architecture

### Core Patterns
This codebase implements Model Context Protocol (MCP) servers that communicate with Claude Desktop via JSON-RPC over stdio. The architecture follows these key patterns:

**FastMCP Framework (Recommended)**:
- Entry point: `from fastmcp import FastMCPServer` or similar
- Tool registration: `@mcp.tool()` decorators with type hints
- Transport: `mcp.run(transport="stdio")` for Claude Desktop integration
- Configuration via environment variables

**Logging Requirements**:
- **Critical**: All MCP servers must log to stderr only (stdout reserved for JSON-RPC)
- Use structured JSON logging: `python-json-logger` with JsonFormatter
- Set `logger.propagate = False` to prevent stdout pollution

**File Structure Conventions**:
```
servers/{name}-mcp-server/
├── server.py          # Entry point/launcher
├── mcp_server.py      # Main server implementation (simple servers)
├── src/               # Source code (complex servers)
│   ├── server.py      # Main server
│   ├── storage/       # Persistence layer
│   └── domain/        # Business logic modules
├── pyproject.toml     # Dependencies and metadata
└── README.md          # Setup and usage
```

### Dependencies and Configuration
**Standard MCP Dependencies**:
- `fastmcp>=0.1.0` - Core MCP framework
- `python-json-logger>=2.0.0` - Structured logging
- Domain-specific libraries (httpx, numpy, etc.)

**Claude Desktop Integration**:
- Servers are registered in `claude_desktop_config.json`
- Use `keepAlive: true` and `stderrToConsole: true` in configuration
- Environment variables passed via `cmd /c "set VAR=value && python server.py"`

## Application Architecture

### Desktop Agent & Bridge Applications
These are FastAPI applications that extend Claude's capabilities beyond standard MCP:

**ClaudeDesktopAgent**: MCP server with screenshot and desktop automation
**ClaudeDesktopBridge**: HTTP bridge with Streamlit UI for system integration

**Common FastAPI Patterns**:
- API routes in `app/api/routes/` with domain separation
- Utilities in `app/utils/` (config, logger, security)
- Modules in `app/modules/` or `app/mcp/` for business logic
- Global exception handlers and health check endpoints

## Development Guidelines

### MCP Tool Development
- Tools should have descriptive docstrings (shown to Claude)
- Use type hints for automatic JSON schema generation
- Handle errors gracefully and return structured responses
- Follow naming: `{domain}_{action}` (e.g., `memory_create`, `git_status`)

### Error Handling Patterns
- Signal handling for graceful shutdown (SIGINT, SIGTERM)
- Import fallbacks for optional dependencies
- Structured error responses with context

### Testing Strategies
- Unit tests with pytest for Python servers
- Node.js servers use package.json test scripts
- Integration testing with actual Claude Desktop for MCP protocol compliance

## Configuration Management

### Environment Variables
- API keys and sensitive data via environment variables
- Data directories: `os.path.expanduser("~/.app-name")` pattern
- Configuration validation at startup

### Claude Desktop Setup
- Config file: `C:\Users\<Username>\AppData\Roaming\Claude\claude_desktop_config.json`
- Logs: `C:\Users\<Username>\AppData\Roaming\Claude\logs/`
- Always restart Claude Desktop after config changes

## Common Development Tasks

### Adding New MCP Server
1. Create `servers/{name}-mcp-server/` directory
2. Implement using FastMCP framework with stdio transport
3. Add structured logging to stderr only
4. Create pyproject.toml with fastmcp dependency
5. Add configuration to claude_desktop_config.json
6. Test integration with Claude Desktop

### Extending Existing Server
1. Add tools using `@mcp.tool()` decorator
2. Follow type hints for automatic schema generation
3. Update README.md with new capabilities
4. Test new tools in Claude Desktop environment

### Debugging MCP Servers
- Check stderr logs in Claude Desktop logs directory
- Verify stdout only contains JSON-RPC messages
- Use `stderrToConsole: true` in Claude Desktop config for real-time logs
- Test servers independently with `python server.py` before Claude Desktop integration