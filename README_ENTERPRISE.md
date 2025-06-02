# Claude MCP Tools

Enterprise-grade Model Context Protocol (MCP) servers for Anthropic's Claude Desktop and Claude Code CLI.

## Overview

This repository provides 25 production-ready MCP servers enabling Claude to interact with external systems, APIs, and development tools through standardized protocols.

### Key Features

- **Platform Support**: Servers optimized for Claude Desktop (GUI) and Claude Code (CLI)
- **Protocol Compliance**: Full MCP specification adherence with JSON-RPC over stdio
- **Security**: Sandboxed operations, input validation, and configurable permissions
- **Performance**: Async operations, caching, and resource optimization
- **Extensibility**: Modular architecture supporting custom server development

## Platform Compatibility

| Server Category | Claude Desktop | Claude Code | Notes |
|----------------|----------------|-------------|-------|
| File Operations | ✅ | ✅ | Cross-platform stdio |
| Code Intelligence | ✅ | ✅ | AST analysis, refactoring |
| API Services | ✅ | ✅ | REST/GraphQL clients |
| Desktop Automation | ✅ | ❌ | Requires GUI environment |
| Container Management | ✅ | ✅* | *Limited without GUI |

## Quick Start

### Prerequisites

- Python 3.11+ or Node.js 18+
- Claude Desktop or Claude Code CLI
- Platform-specific requirements per server

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/claude-mcp-tools.git
cd claude-mcp-tools
```

2. Configure Claude Desktop:
```bash
# Location varies by platform - see docs/getting-started/
cp claude_desktop_config.json $CLAUDE_CONFIG_PATH
```

3. Restart Claude Desktop to load servers

### Basic Usage

```python
# Example: Using filesystem MCP
"Read all Python files in the src directory"

# Example: Using code analysis MCP  
"Analyze the complexity of functions in main.py"

# Example: Using GitHub MCP
"Create a pull request with the recent changes"
```

## Server Categories

### Development Tools (10 servers)
- **Filesystem**: Secure file operations with path sandboxing
- **GitHub**: Repository management via GitHub API
- **Code Analysis**: AST parsing, symbol resolution, complexity metrics
- **Code Quality**: Multi-tool linting and formatting
- **Refactoring**: Safe code transformations with git integration
- **Test Intelligence**: Automated test generation and coverage analysis
- **Dependency Analysis**: Security scanning and license compliance
- **Docker Orchestration**: Container lifecycle management
- **SQLite**: Local database operations
- **Sequential Thinking**: Structured problem-solving framework

### Desktop Automation (5 servers)
- **Windows Computer Use**: Native Windows automation with Computer Use API
- **Containerized Computer Use**: Docker-isolated GUI automation
- **ScreenPilot**: Advanced screen analysis and interaction
- **Playwright**: Browser automation and testing
- **Vibetest**: Multi-agent browser QA testing

### API Services (6 servers)
- **AgenticSeek**: Multi-provider AI routing with cost optimization
- **API Gateway**: Unified API management with caching
- **Financial Datasets**: Market data and financial analytics
- **Firecrawl**: Web scraping and content extraction
- **N8n Workflow**: Workflow automation platform integration
- **Pandoc**: Document format conversion

### Knowledge Management (4 servers)
- **Knowledge Memory**: Vector-based persistent storage
- **Memory (Official)**: Standard MCP memory implementation
- **Claude Code Integration**: Hybrid AI development workflows
- **Fantasy Premier League**: Sports analytics (specialized)

## Architecture

### Server Implementation Pattern

```python
from fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
async def process_data(input: str, options: dict) -> dict:
    """Process data with specified options."""
    # Implementation
    return {"status": "success", "result": processed_data}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Configuration Schema

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["path/to/server.py"],
      "cwd": "working/directory",
      "env": {
        "API_KEY": "${OPENAI_API_KEY}",
        "LOG_LEVEL": "INFO"
      },
      "transport": "stdio",
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Security Considerations

- **File Access**: Configurable allowed paths with traversal prevention
- **API Keys**: Environment variable management, never in code
- **Input Validation**: Type checking and sanitization on all inputs
- **Rate Limiting**: Built-in throttling for API-based servers
- **Logging**: Structured logging to stderr, audit trails available

## Performance Optimization

### Resource Usage Guidelines

| Operation Type | Target Latency | Memory Usage | CPU Usage |
|---------------|----------------|--------------|-----------|
| File Operations | <50ms | <100MB | <5% |
| API Calls | <500ms | <200MB | <10% |
| Code Analysis | <1s | <500MB | <25% |
| Desktop Automation | <2s | <1GB | <50% |

### Best Practices

1. Use appropriate tool selection hierarchy (API > File > GUI)
2. Enable caching for repeated operations
3. Batch operations when possible
4. Monitor resource usage in production

## Development

### Adding a New Server

```bash
# Use the server template
cp -r templates/mcp-server-template servers/my-new-server
cd servers/my-new-server
pip install -e .
```

### Testing

```bash
# Unit tests
pytest servers/my-server/tests/

# Integration tests
python scripts/test_all_servers.py

# Load testing
mcp-bench --server my-server --concurrent 10
```

### Contributing

See [CONTRIBUTING.md](docs/development/contributing.md) for:
- Code style guidelines
- Testing requirements
- PR process
- Documentation standards

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Server not connecting | Check logs at `%APPDATA%/Claude/logs/` |
| Permission denied | Verify allowed paths in configuration |
| High memory usage | Enable resource limits in server config |
| API rate limits | Implement exponential backoff |

### Debug Mode

```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
python server.py

# Protocol inspection
claude-desktop --mcp-debug
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-org/claude-mcp-tools/issues)
- Security: security@your-org.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.