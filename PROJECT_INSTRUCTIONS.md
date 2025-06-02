# Claude Desktop Project Instructions: Claude-MCP-Tools

## 🎯 Project Overview
You are working as a development assistant for the **Claude-MCP-tools repository**, a comprehensive ecosystem of Model Context Protocol (MCP) servers for Claude Desktop and Claude Code integration.

## 📍 Key Project Details

### Repository Information
- **Location**: `C:\AI_Projects\Claude-MCP-tools`
- **GitHub**: `GrimFandango42/Claude-MCP-tools`
- **Branch**: `master`
- **Server Count**: 21 operational MCP servers (consolidated from 25 in June 2025)
- **Status**: Production-ready multi-provider AI routing system

### Core Components
- **AgenticSeek MCP**: Multi-provider AI routing (Local DeepSeek, OpenAI, Google Gemini)
- **Claude Code Integration MCP**: Bridge between Claude Desktop and Claude Code CLI
- **Windows Computer Use MCP**: Desktop automation with screen capture and control
- **Memory MCP**: Persistent context storage (shared between tools)
- **Vibetest MCP**: Multi-agent browser QA testing swarm
- **Financial Datasets MCP**: Financial data integration and analysis
- **API Gateway MCP**: Unified routing with caching and cost optimization

## 🛠️ Development Guidelines

### MCP Server Architecture
- **Framework**: FastMCP with stdio transport for Claude Desktop integration
- **Logging**: Use stderr only (stdout reserved for JSON-RPC communication)
- **Structure**: Follow patterns in `CLAUDE.md` for consistency
- **Testing**: Test servers independently before Claude Desktop integration

### File Structure Conventions
```
servers/{name}-mcp-server/
├── server.py          # Entry point/launcher
├── pyproject.toml     # Dependencies and metadata
├── README.md          # Setup and usage
└── src/               # Source code (complex servers)
```

### Key Commands
- **Python**: `pip install -e .` for setup, `python server.py` to run
- **Node.js**: `npm install` for setup, `node server.js` to run  
- **Testing**: `pytest` for Python, `npm test` for Node.js
- **Linting**: `black .` and `isort .` for Python formatting

## 🧠 Memory Management

### Memory MCP Server Usage
You have access to a persistent Memory MCP server that stores entities, relations, and observations. Use it to:

1. **Search existing context**: `mcp__memory__search_nodes` before starting work
2. **Create new entities**: Document new components, processes, or discoveries
3. **Add observations**: Update existing entities with new information  
4. **Create relations**: Link related components for better context discovery

### Session Workflow
1. **Start**: Search memory for relevant context using keywords
2. **Work**: Document decisions and discoveries in memory
3. **End**: Add session summary and update project status

## 📚 Key Documentation

### Primary References
- **CLAUDE.md**: Core development guidelines and build commands
- **PROJECT_STATUS.md**: Current status with complete server inventory
- **CONFIG_UPDATE_COMPLETE.md**: Recent configuration changes and fixes
- **Server READMEs**: Individual setup guides for each MCP server

### Configuration Files
- **Claude Desktop Config**: `C:\Users\Nithin\AppData\Roaming\Claude\claude_desktop_config.json`
- **Contains**: 21 active MCP servers with proper paths and environment variables
- **Shared**: Configuration works for both Claude Desktop and Claude Code

## 🔧 Common Tasks & Patterns

### Server Development
1. Create new server directory following naming convention
2. Implement using FastMCP framework with proper async patterns
3. Add structured logging to stderr with JsonFormatter
4. Test independently, then add to Claude Desktop config
5. Document in README and update PROJECT_STATUS.md

### Troubleshooting
1. Check logs at `%APPDATA%\Claude\logs\mcp-server-{name}.log`
2. Verify FastMCP is installed in system site-packages
3. Ensure proper paths in Claude Desktop configuration
4. Test server startup independently before debugging integration

### Memory Best Practices
- Use single keywords for searches ("consolidation", "FastMCP", "server")
- Create entities with rich observations for better searchability
- Establish relations between connected components
- Update existing entities rather than creating duplicates

## 🎯 Current Focus Areas

### Recent Achievements (June 2025)
- ✅ Server consolidation from 25 to 21 servers completed
- ✅ AgenticSeek MCP asyncio event loop conflicts resolved
- ✅ Claude Code Integration MCP FastMCP dependency fixed
- ✅ Comprehensive memory structure established

### Active Priorities
- Memory system optimization and usage patterns
- Enhanced documentation and context retention
- Cross-tool integration between Claude Code and Claude Desktop
- Server performance monitoring and optimization

## 💡 Key Reminders

- **Memory First**: Always search memory before starting new work
- **Document Everything**: Add important discoveries to memory for future reference
- **Test Thoroughly**: MCP servers must work independently before integration
- **Follow Conventions**: Use established patterns from CLAUDE.md and existing servers
- **Share Context**: Memory is shared between Claude Code and Claude Desktop

This project represents a comprehensive MCP ecosystem enabling advanced AI-assisted development workflows. Focus on maintaining the high quality standards established and leveraging the persistent memory system for optimal productivity.