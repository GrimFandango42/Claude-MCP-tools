# Claude MCP Tools

Professional Model Context Protocol (MCP) server ecosystem for Anthropic's Claude Desktop and Claude Code CLI integration.

## 🎯 **Current Status: Production-Ready Multi-Provider AI System** ✅
- **Latest Update**: June 2, 2025
- **Server Count**: 21 operational MCP servers (consolidated from 25)
- **System Status**: Claude Code Integration tested with 100% success rate
- **Achievement**: Comprehensive memory system and enhanced context retention

## Overview

This repository provides a production-ready ecosystem of 21 MCP servers enabling advanced AI-assisted development workflows. The servers facilitate Claude's interaction with external systems, APIs, and development tools through standardized Model Context Protocol implementations.

### Key Capabilities

- **Hybrid AI Development**: Seamless integration between Claude Desktop and Claude Code CLI
- **Multi-Provider AI Routing**: Smart routing between local and cloud AI providers with cost optimization
- **Advanced Memory Management**: Persistent context storage with rich entity-relation graphs
- **Desktop Automation**: Comprehensive GUI automation and testing capabilities
- **Development Workflow Enhancement**: Code analysis, formatting, security scanning, and project management

## Architecture

### Server Ecosystem (21 Servers)

#### **Production Custom Servers (12)**
1. **Claude Code Integration MCP** ⭐ **TESTED & VERIFIED** - Task delegation and project analysis
2. **AgenticSeek MCP** - Multi-provider AI routing (Local DeepSeek, OpenAI, Google Gemini)
3. **Vibetest MCP** - Multi-agent browser QA testing swarm
4. **Code Formatter MCP** - Black/Prettier wrapper for code formatting
5. **Security Scanner MCP** - Vulnerability scanning with pip-audit and npm audit
6. **Windows Computer Use MCP** - Desktop automation with screen capture
7. **Containerized Computer Use MCP** - Docker-isolated GUI automation
8. **API Gateway MCP** - Unified routing for OpenAI and Anthropic APIs
9. **Financial Datasets MCP** - Financial data integration and analysis
10. **N8n Workflow Generator MCP** - Workflow automation platform
11. **Docker Orchestration MCP** - Container lifecycle management
12. **Knowledge Memory MCP** - Vector-based persistent storage

#### **Integrated Third-Party Servers (9)**
13. **GitHub Integration MCP** - Repository management and automation
14. **Firecrawl Custom MCP** - Web scraping and content extraction
15. **ScreenPilot MCP** - Advanced UI element detection and automation
16. **SQLite MCP** - Local database operations
17. **Memory MCP (Official)** - Standard MCP memory implementation
18. **Filesystem MCP** - Secure file operations with path sandboxing
19. **Sequential Thinking MCP** - Structured problem-solving framework
20. **Playwright MCP** - Browser automation and testing
21. **Fantasy Premier League MCP** - Sports analytics and data

### Platform Compatibility

| Server Category | Claude Desktop | Claude Code | Notes |
|----------------|----------------|-------------|-------|
| AI Routing | ✅ | ✅ | Multi-provider smart routing |
| Memory Management | ✅ | ✅ | Shared persistent context |
| Code Intelligence | ✅ | ✅ | Analysis, formatting, security |
| Desktop Automation | ✅ | ❌ | Requires GUI environment |
| API Services | ✅ | ✅ | REST/GraphQL integration |
| Container Management | ✅ | ✅ | Docker orchestration |

## Quick Start

### Prerequisites

- **Python 3.11+** or **Node.js 18+**
- **Claude Desktop** or **Claude Code CLI**
- **FastMCP framework** for custom server development

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/GrimFandango42/Claude-MCP-tools.git
cd Claude-MCP-tools
```

2. **Install core dependencies:**
```bash
# Install FastMCP framework
pip install fastmcp python-json-logger

# Install development tools (optional)
pip install black prettier pip-audit safety
```

3. **Configure Claude Desktop:**
```bash
# Copy configuration template
cp claude_desktop_config_template.json $CLAUDE_CONFIG_PATH

# Edit configuration with your API keys and paths
# Location: %APPDATA%\Claude\claude_desktop_config.json (Windows)
```

4. **Restart Claude Desktop** to load servers

### Verification

Test your setup by asking Claude:
```
"Search memory for server status and show me what MCP servers are available"
```

## Core Features

### Memory-First Architecture
All servers integrate with the Memory MCP system for persistent context:
- **Entity Storage**: Projects, servers, processes, and knowledge
- **Relation Mapping**: Connected information discovery
- **Cross-Session Continuity**: Context preservation across conversations
- **Searchable Knowledge**: Single-keyword search with comprehensive results

### Smart AI Routing
AgenticSeek MCP provides intelligent AI provider selection:
- **Local Processing**: Free, private DeepSeek AI (privacy priority)
- **Cloud APIs**: OpenAI GPT-3.5/4 (speed priority) and Google Gemini (cost priority)
- **Smart Routing**: Automatic provider selection based on task characteristics
- **Cost Optimization**: Transparent cost estimation and optimization

### Development Workflow Enhancement
Comprehensive tools for AI-assisted development:
- **Code Analysis**: AST parsing, complexity metrics, symbol resolution
- **Quality Assurance**: Automated formatting, linting, and security scanning
- **Task Delegation**: Claude Code Integration for complex coding tasks
- **Project Intelligence**: Automated codebase analysis and recommendations

## Server Implementation

### Basic Server Pattern

```python
from fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
async def process_data(input: str, options: dict = None) -> dict:
    """Process data with specified options."""
    # Server implementation
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
        "API_KEY": "your-api-key",
        "LOG_LEVEL": "INFO"
      },
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Memory System Usage

### Session Workflow
1. **Start sessions** by searching memory for relevant context
2. **Document discoveries** in memory during work
3. **Create relations** between connected components
4. **End sessions** by updating memory with outcomes

### Effective Search Patterns
```python
# Search for project context
mcp__memory__search_nodes("server")
mcp__memory__search_nodes("consolidation") 
mcp__memory__search_nodes("FastMCP")

# Search by entity type
mcp__memory__search_nodes("configuration")
mcp__memory__search_nodes("documentation")
```

## Development Guidelines

### Server Development Standards
- **FastMCP Framework**: Use for all new MCP servers
- **Async Patterns**: Proper async/await implementation
- **Error Handling**: Comprehensive error management and logging
- **Memory Integration**: Document discoveries in Memory MCP
- **Testing**: Independent testing before Claude Desktop integration

### Code Quality Standards
- **Logging**: Structured logging to stderr only (stdout reserved for JSON-RPC)
- **Type Hints**: Full type annotation for better tooling
- **Documentation**: Rich docstrings for tools and functions
- **Security**: Input validation and secure API key management

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Server not connecting | Check logs at `%APPDATA%\Claude\logs\mcp-server-{name}.log` |
| FastMCP import errors | Install to system site-packages: `pip install --target system fastmcp` |
| Memory search inconsistency | Use single keywords instead of multi-word phrases |
| Configuration not loading | Restart Claude Desktop after config changes |
| AsyncIO event loop conflicts | Use proper async/await patterns, avoid `asyncio.run()` |

### Debug Configuration
```json
{
  "stderrToConsole": true,
  "env": {
    "MCP_LOG_LEVEL": "DEBUG",
    "CLAUDE_CODE_MOCK": "true"
  }
}
```

## Recent Achievements

### June 2, 2025 - Memory System & Claude Code Integration ✅
- **Comprehensive Memory Structure**: 27 entities, 31 relations for project knowledge
- **Claude Code Integration Testing**: 100% success rate (2/2 tasks completed)
- **Enhanced Documentation**: Professional system instructions and workflow templates
- **Server Consolidation**: Optimized from 25 to 21 servers with improved efficiency

### May 31, 2025 - AI Routing System Complete ✅
- **AgenticSeek MCP Server**: AsyncIO bug resolution with 100% operational success
- **Multi-Provider Integration**: Local DeepSeek, OpenAI GPT-3.5/4, Google Gemini
- **Smart Cost Optimization**: Intelligent provider selection based on task characteristics

## Project Structure

```
Claude-MCP-tools/
├── servers/                    # MCP server implementations
│   ├── agenticseek-mcp/       # Multi-provider AI routing
│   ├── claude-code-integration-mcp/  # Claude Code CLI bridge
│   ├── windows-computer-use/   # Desktop automation
│   └── ...                    # Additional servers
├── docs/                      # Comprehensive documentation
├── scripts/                   # Deployment and testing scripts
├── archive/                   # Historical and deprecated files
├── CLAUDE.md                  # Development guidelines
├── PROJECT_STATUS_UPDATED.md  # Current project status
└── CONFIG_UPDATE_COMPLETE.md  # Configuration management guide
```

## Contributing

We welcome contributions! Please see our development guidelines:

1. **Follow FastMCP patterns** for server development
2. **Use Memory MCP** to document discoveries and solutions
3. **Test independently** before Claude Desktop integration
4. **Update documentation** with new capabilities

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support & Resources

- **Documentation**: Comprehensive guides in `/docs/` directory
- **Development Guidelines**: See `CLAUDE.md` for standards and patterns
- **Project Status**: Current status in `PROJECT_STATUS_UPDATED.md`
- **Memory Workflow**: `MEMORY_WORKFLOW_GUIDE.md` for context management
- **Session Templates**: `SESSION_CONTEXT_TEMPLATE.md` for structured work

## Acknowledgments

Built on the Model Context Protocol specification by Anthropic. Leverages FastMCP framework for efficient server implementation and the official Memory MCP server for persistent context storage.

---
**Status**: Production Ready | **Last Updated**: June 2, 2025 | **Servers**: 21 Operational