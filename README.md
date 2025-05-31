# Claude MCP Tools

A comprehensive collection of Model Context Protocol (MCP) servers designed to enhance Anthropic's Claude Desktop capabilities through specialized integrations, external APIs, and system automation.

## Architecture Overview

This project provides a production-ready ecosystem of **19 operational MCP servers**, enabling advanced automation and integration capabilities. The architecture emphasizes modularity, reliability, and compliance with MCP protocol specifications.

### Current Status

- **Production Servers**: 10 custom-developed MCP servers
- **Integrated Third-Party**: 9 official and community servers
- **Protocol Compliance**: Full MCP framework adherence with async/await patterns
- **System Coverage**: Windows, Linux (containerized), cloud services, and development tools

## Quick Start Guide

### Claude Desktop Configuration

The `claude_desktop_config.json` configuration file is located at:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Essential Configuration Pattern

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["path/to/server.py"],
      "cwd": "working/directory",
      "env": {"API_KEY": "value"},
      "keepAlive": true,
      "stderrToConsole": true,
      "description": "Server purpose and capabilities"
    }
  }
}
```

### Tool Selection Framework

The project implements a hierarchical tool selection strategy optimized for efficiency and capability:

#### Priority 1: Direct API Operations (10-100 tokens)
- **File Operations**: `filesystem` MCP server
- **Database Operations**: `sqlite` MCP server  
- **Code Editing**: `text_editor_20250429`
- **System Commands**: `bash_20250124`
- **Repository Management**: `github` MCP server

#### Priority 2: Specialized Domain APIs (100-500 tokens)
- **Financial Data**: `financial-datasets` MCP
- **Knowledge Management**: `knowledge-memory` MCP
- **Container Orchestration**: `docker-orchestration` MCP
- **AI Provider Routing**: `agenticseek` MCP
- **Workflow Automation**: `n8n-workflow-generator` MCP

#### Priority 3: GUI Automation (500-2000 tokens)
- **Desktop Control**: `computer_20250124` (when API alternatives unavailable)
- **Screen Automation**: `screenpilot` MCP
- **Browser Automation**: `playwright` MCP

## Core Production Servers

### System Integration & Automation

#### **AgenticSeek MCP** (`agenticseek-mcp`) ✅ **RESOLVED**
- **Capabilities**: Multi-provider AI routing with cost optimization and privacy controls
- **Providers**: Local DeepSeek (free/private), OpenAI GPT-3.5/4, Google Gemini
- **Tools**: `smart_routing`, `local_reasoning`, `openai_reasoning`, `google_reasoning`, `get_provider_status`, `estimate_cost`
- **Recent Fix**: Resolved asyncio event loop conflicts for full compatibility

#### **Windows Computer Use MCP** (`windows-computer-use`)
- **Capabilities**: Native Windows desktop automation with full Computer Use API compliance
- **Tools**: `computer_20250124`, `text_editor_20250429`, `bash_20250124`
- **Features**: 16 enhanced actions including advanced mouse/keyboard control, screenshot capture, window management

#### **Claude Desktop Agent** (`claude-desktop-agent`)
- **Capabilities**: Enhanced desktop agent with resilient screenshot capture and secure shell execution
- **Security**: Allowlisted command execution (`git`, `code`, `gcloud`, `kubectl`, etc.)
- **Integration**: Works with system automation frameworks

#### **Containerized Computer Use MCP** (`containerized-computer-use`)
- **Capabilities**: Secure, isolated desktop automation using Docker and VNC
- **Environment**: XVFB + Fluxbox for cross-platform GUI automation
- **Benefits**: Enhanced security isolation for sensitive operations

### Development & Code Management

#### **Claude Code Integration MCP** (`claude-code-integration-mcp`)
- **Capabilities**: Hybrid AI development workflow integrating Claude Desktop (orchestrator) with Claude Code CLI (execution agent)
- **Features**: Task delegation, progress monitoring, context preservation across AI agents
- **Tools**: `analyze_project`, `delegate_coding_task`, `monitor_task_progress`, `get_task_results`

#### **Docker Orchestration MCP** (`docker-orchestration-mcp`)
- **Capabilities**: Comprehensive Docker environment management
- **Tools**: 19+ tools covering container lifecycle, image operations, network/volume configuration
- **Features**: Application stack deployment, health monitoring, resource management

### Data & Intelligence

#### **Financial Datasets MCP** (`financial-mcp-server`)
- **Capabilities**: Financial data access via Financial Datasets API
- **Data Types**: Company facts, stock prices, income statements, market analytics
- **Integration**: Real-time and historical financial data retrieval

#### **Knowledge Memory MCP** (`knowledge-memory-mcp`)  
- **Capabilities**: Persistent knowledge management with vector search
- **Features**: Note CRUD operations, semantic search, tagging, similarity analysis
- **Tools**: `create_note`, `search_notes`, `semantic_search`, `get_similar_notes`

#### **API Gateway MCP** (`api-gateway-mcp`)
- **Capabilities**: Multi-provider AI API management with intelligent routing
- **Features**: Cost optimization, response caching, usage analytics, provider failover
- **Tools**: `call_api`, `list_providers`, `get_usage_stats`, `estimate_cost`

### Workflow & Automation

#### **N8n Workflow MCP** (`n8n-mcp-server`)
- **Capabilities**: N8n automation platform integration
- **Features**: Natural language workflow generation and management
- **Use Cases**: Complex automation chain creation and monitoring

#### **Vibetest MCP** (`vibetest`)
- **Capabilities**: Multi-agent browser QA testing with intelligent bug detection
- **Features**: Automated UI testing, bug severity classification, test result analysis
- **Tools**: `start` (launch testing swarm), `results` (consolidated bug reports)

## Integrated Third-Party Servers

### Official MCP Servers
- **`filesystem`**: File and directory operations within allowed paths
- **`github`**: Repository management, issue tracking, code deployment  
- **`memory`**: Standard persistent context storage
- **`sequentialthinking`**: Step-by-step reasoning and problem decomposition

### Community & Specialized Servers
- **`playwright`**: Browser automation for web interaction and testing
- **`screenpilot`**: Desktop automation with screen analysis
- **`sqlite`**: Database operations for SQLite databases
- **`mcp-pandoc`**: Document format conversion and transformation
- **`firecrawl`**: Advanced web scraping and content extraction
- **`fantasy-pl`**: Sports analytics for Fantasy Premier League

## Development Standards

### MCP Framework Compliance

All custom servers implement the standard MCP pattern for consistency and reliability:

```python
import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

class StandardMCPServer(Server):
    async def handle_tool_call(self, name: str, arguments: dict):
        try:
            # Tool implementation with proper error handling
            result = await self.process_tool(name, arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            # Log to stderr with server identification
            print(f"[{self.name}] Error: {e}", file=sys.stderr)
            raise

async def main():
    server = StandardMCPServer("server-name")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Implementation Requirements

- **Async Compliance**: Use `async/await` patterns with proper event loop management
- **Error Handling**: Comprehensive exception handling with stderr logging
- **Response Format**: Return `TextContent` objects for tool responses
- **Framework Usage**: Utilize MCP framework classes to avoid JSON-RPC validation errors
- **Environment Management**: Virtual environments with `requirements.txt` dependency specification
- **Security**: Secure API key management and input validation

## Technical Architecture

### Protocol Implementation
- **Transport**: stdio-based JSON-RPC communication
- **Message Format**: MCP-compliant request/response structures
- **Error Handling**: Structured error responses with appropriate HTTP status codes
- **Concurrency**: Async/await patterns for non-blocking operations

### Deployment Patterns
- **Launch Scripts**: Batch files for consistent server startup
- **Environment Isolation**: Virtual environments for dependency management  
- **Configuration Management**: Centralized configuration through `claude_desktop_config.json`
- **Logging**: Structured logging to stderr with server identification

### Integration Points
- **Claude Desktop**: Primary client interface through MCP connector
- **External APIs**: RESTful API integrations with authentication management
- **System Resources**: Secure access to filesystem, databases, and system commands
- **Container Orchestration**: Docker integration for isolated execution environments

## Use Cases & Capabilities

### AI-Assisted Development
- Hybrid development workflows combining strategic oversight with specialized execution
- Automated code generation, testing, and deployment
- Multi-repository management and synchronization

### System Administration  
- Comprehensive desktop automation across Windows and Linux environments
- Container lifecycle management and orchestration
- Secure command execution with allowlisted operations

### Data Intelligence
- Financial market analysis and investment research
- Knowledge base management with semantic search
- Web intelligence gathering and content extraction

### Workflow Orchestration
- Complex automation chain creation and management
- Multi-system integration and data pipeline development
- Process monitoring and optimization

## Troubleshooting Guide

### Common Issues

**Server Transport Errors**: 
- Verify MCP framework usage (avoid manual JSON-RPC)
- Check async/await implementation patterns
- Review error handling and logging

**Validation Errors**:
- Ensure proper `TextContent` response format
- Validate tool parameter schemas
- Check JSON serialization compatibility

**Dependency Issues**:
- Verify virtual environment activation
- Install all `requirements.txt` dependencies
- Check Python version compatibility

**Configuration Problems**:
- Validate `claude_desktop_config.json` syntax
- Verify file paths and command arguments
- Check environment variable configuration

### Diagnostic Tools
- **Server Validation**: `scripts/validate_servers.py`
- **Claude Desktop Logs**: `%APPDATA%\Claude\logs\` (Windows)
- **Individual Server Logs**: stderr output with server identification

## Project Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)**: Current development status and milestones
- **[SERVER_INVENTORY.md](SERVER_INVENTORY.md)**: Complete server catalog with capabilities
- **[examples/](examples/)**: Implementation examples and test workflows
- **[scripts/](scripts/)**: Utility scripts for deployment and validation

## Future Development

### Planned Enhancements
- **Database Analytics MCP**: Enterprise database integration (PostgreSQL, MySQL, MongoDB)
- **Cloud Infrastructure MCP**: Multi-cloud resource management (AWS, Azure, GCP)
- **Home Automation Hub**: IoT device control across protocols (MQTT, Zigbee, Z-Wave)
- **Advanced Workflow Engine**: Enhanced multi-agent orchestration capabilities

### Architecture Evolution
- **Tool Context Bridge**: Context sharing between Claude instances
- **Enhanced Security Framework**: Advanced authentication and authorization
- **Performance Optimization**: Caching strategies and response optimization
- **Monitoring & Analytics**: Comprehensive usage tracking and performance metrics
