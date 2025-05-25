# Claude-MCP-tools

A collection of Model Context Protocol (MCP) servers designed to enhance Claude Desktop's capabilities through custom integrations, external APIs, and system automation. This repository provides both custom implementations and configuration references for official and third-party MCP servers.

## MCP Server Ecosystem

### Custom Production-Ready Implementations

1. **Windows Computer Use MCP Server**
   - **Location**: `servers/windows-computer-use/`
   - **Implementation**: Custom Python with MCP framework integration
   - **Capabilities**: Full Computer Use API compliance with 16+ enhanced actions
   - **Key Features**: Screenshot capture, mouse/keyboard automation, WSL integration
   - **Status**: Production ready (all Computer Use API compliance tests passing)
   - **Usage**: Desktop automation, application control, cross-environment development

2. **Financial Datasets MCP Server**
   - **Location**: `servers/financial-mcp-server/`
   - **Implementation**: Python with FastMCP framework
   - **Capabilities**: Financial market data and company analysis through API integration
   - **Key Features**: Company facts, stock prices, income statements
   - **API Integration**: [Financial Datasets API](https://api.financialdatasets.ai/)
   - **Status**: Production ready with structured JSON logging and error handling

3. **Docker Orchestration MCP Server**
   - **Location**: `servers/docker-orchestration-mcp/`
   - **Implementation**: Python with MCP server framework
   - **Capabilities**: Comprehensive Docker container management
   - **Key Features**: Container lifecycle management, network/volume control, health monitoring
   - **Library Integration**: [Docker SDK for Python](https://docker-py.readthedocs.io/)
   - **Status**: Production ready with enhanced async stream handling

4. **N8n Workflow MCP Server**
   - **Location**: `servers/n8n-mcp-server/`
   - **Implementation**: Node.js
   - **Capabilities**: N8n workflow generation and management via API
   - **Key Features**: Natural language workflow creation, template system
   - **Integration**: [N8n Automation Platform](https://n8n.io/)
   - **Status**: Production ready with comprehensive documentation

5. **Knowledge Memory MCP Server**
   - **Location**: `servers/knowledge-memory-mcp/`
   - **Implementation**: Python with SQLite and vector store
   - **Capabilities**: Persistent memory with semantic search capabilities
   - **Key Features**: Context storage, vector similarity search, tagging system
   - **Status**: Production ready with structured logging
   - **Note**: Custom implementation complementing the official memory server

6. **Firecrawl MCP Custom Wrapper**
   - **Location**: `servers/firecrawl-mcp-custom/`
   - **Implementation**: Node.js wrapper with fallback mode
   - **Capabilities**: Enhanced web scraping with local processing fallback
   - **Integration**: [Firecrawl API](https://firecrawl.dev/)
   - **Key Features**: Hybrid implementation with automatic minimal mode, environment variable sanitization
   - **Status**: Production ready with comprehensive error handling

### Official MCP Servers (Configured)

1. **Filesystem**
   - **Source**: [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
   - **Capabilities**: File and directory operations within allowed directories
   - **Configuration**: Multi-directory support for secure file access

2. **GitHub**
   - **Source**: [@modelcontextprotocol/server-github](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
   - **Capabilities**: Complete GitHub repository, issue, and PR management
   - **Status**: Fully configured with authentication

3. **Memory**
   - **Source**: [@modelcontextprotocol/server-memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
   - **Capabilities**: Persistent memory storage with metadata and management
   - **Note**: Used alongside our custom Knowledge Memory implementation

### Third-Party MCP Servers (Configured)

1. **SequentialThinking**
   - **Source**: [@modelcontextprotocol/server-sequential-thinking](https://github.com/modelcontextprotocol/server-sequential-thinking)
   - **Capabilities**: Advanced step-by-step reasoning framework
   - **Usage**: Complex problem decomposition and verification

2. **Playwright**
   - **Source**: [@automatalabs/mcp-server-playwright](https://github.com/AutomataLabs/mcp-server-playwright)
   - **Capabilities**: Browser automation and testing
   - **Usage**: Web scraping, UI testing, form automation

3. **ScreenPilot**
   - **Location**: External implementation
   - **Capabilities**: Desktop automation with screen capture and control
   - **Note**: Alternative to Windows Computer Use for specific scenarios

4. **SQLite**
   - **Source**: [mcp-server-sqlite-npx](https://www.npmjs.com/package/mcp-server-sqlite-npx)
   - **Capabilities**: Database operations and SQL queries
   - **Usage**: Local data storage and analysis

5. **Pandoc**
   - **Source**: [mcp-pandoc](https://github.com/mckaywrigley/mcp-pandoc)
   - **Capabilities**: Document format conversion
   - **Usage**: File transformation between various formats

6. **Fantasy Premier League**
   - **Source**: [fpl_mcp](https://pypi.org/project/fpl-mcp/)
   - **Capabilities**: Fantasy Premier League data and analysis
   - **Usage**: Sports analytics and strategy recommendations

### Experimental/Archived MCP Servers

1. **Containerized Computer Use**
   - **Location**: `servers/containerized-computer-use/`
   - **Status**: Active development
   - **Goal**: Isolated environment for Computer Use execution with Docker
   - **Architecture**: Docker containers with VNC for GUI access

2. **Test Automation MCP**
   - **Location**: `servers/test-automation-mcp/`
   - **Status**: Archived due to connection stability issues
   - **Note**: Functionality now partially covered by Playwright integration

3. **Nest Control MCP**
   - **Status**: Development paused due to stream handling failures
   - **Note**: Home automation integration to be revisited

## Testing and Validation

This repository includes comprehensive testing tools and examples to validate MCP servers and demonstrate their capabilities in both isolated and integrated scenarios.

### Test Framework

- **[test_all_servers.py](test_all_servers.py)**: System-wide validation script that checks connectivity and basic functionality for all configured MCP servers
- **Server-specific tests**: Each server directory contains specialized tests:
  - `quick_test.py`: Validates basic server functionality
  - `test_startup.py`: Tests proper initialization and stream handling
  - `manual_test.py`: Interactive validation for complex servers

### Usage Examples

- **[Quick Server Tests](examples/quick_server_tests.md)**: Individual server validation tests with expected outputs and troubleshooting guidance
- **[Comprehensive MCP Examples](examples/comprehensive_mcp_examples.md)**: 10 detailed multi-server workflows for real-world use cases

### Example Categories

The examples cover these key functional areas:

- **Financial Intelligence**
  - Market analysis combining Financial Datasets and web scraping
  - Investment research with SQL data storage and KnowledgeMemory
  - Competitive intelligence pipelines with multi-source data integration

- **Document Processing**
  - Web scraping with Firecrawl and content extraction
  - Format conversion using Pandoc and filesystem operations
  - Knowledge management with vector-based memory storage

- **Desktop Automation**
  - Windows Computer Use for cross-application workflows
  - WSL integration for development environment automation
  - Screenshot analysis and GUI automation

- **Container Management**
  - Docker deployment with volume and network configuration
  - Container monitoring and health checks
  - Multi-container application orchestration

- **Workflow Automation**
  - N8n workflow generation from natural language
  - API integration between disparate systems
  - Scheduled task management and monitoring

### Test-Driven Development

The repository follows test-driven development principles for MCP servers:

1. **Validation Tests**: Comprehensive test coverage for each server
2. **Stream Handling Tests**: Specialized tests for MCP transport stability
3. **Integration Tests**: Multi-server workflows that validate interoperability
4. **Regression Testing**: Automated verification to prevent regressions

## Claude 4 Integration Strategy

This project adopts a strategic approach to MCP server development in the Claude 4 era, focusing on complementary capabilities that extend Claude's native functionality rather than duplicating built-in features.

### Claude 4 Capabilities and Our Extensions

1. **Native Code Execution**
   - **Claude 4 Capability**: Built-in code execution for Python, JavaScript, and other languages
   - **Our Extension**: WSL integration for cross-environment development, Docker orchestration for containerized execution, and specialized development tools
   - **Reference**: [Claude 4 Code Execution Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool)

2. **Enhanced File Handling**
   - **Claude 4 Capability**: Improved document processing and file manipulation
   - **Our Extension**: Multi-directory filesystem access, specialized format conversion with Pandoc, and document intelligence pipelines
   - **Reference**: [Claude 4 File Handling Documentation](https://docs.anthropic.com/en/docs/build-with-claude/files)

3. **Improved MCP Connector**
   - **Claude 4 Capability**: Enhanced stability and debugging for MCP server connections
   - **Our Implementation**: Structured JSON logging, reliable stream handling, and comprehensive error recovery
   - **Reference**: [MCP Connector Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)

### Strategic Focus Areas

1. **External API Integrations**
   - Financial data access through the Financial Datasets MCP
   - Fantasy Premier League analytics via specialized API
   - Web intelligence gathering with Firecrawl's enhanced capabilities
   - Structured database operations with SQLite integration

2. **Desktop Automation and Local System Access**
   - Full Computer Use API implementation for Windows
   - WSL bridge for Linux command execution
   - GUI automation with screenshot capture and analysis
   - Application control across environments

3. **Containerization and Orchestration**
   - Docker container lifecycle management
   - Application deployment and monitoring
   - Network and volume control
   - Isolated execution environments

4. **Workflow Automation**
   - N8n workflow generation from natural language
   - Process automation across multiple systems
   - Integration between disparate tools and platforms

5. **Memory and Knowledge Management**
   - Dual-layer memory architecture (official + custom implementation)
   - Vector-based semantic search capabilities
   - Structured knowledge organization and retrieval

### Implementation Architecture

 Our MCP server implementations follow specific architectural patterns for reliability:

```python
# Core architectural pattern for Python MCP servers
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

class CustomMCPServer:
    def __init__(self, server_name):
        self.server = Server(server_name)
        self._register_tools()
        # Initialize resources here
    
    def _register_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            # Return tools definition
            pass
            
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            # Implement tool execution logic
            pass

async def main():
    server = CustomMCPServer('server-name')
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(read_stream, write_stream,
                              server.server.create_initialization_options())

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

### Local-First Implementation Strategy

We prioritize local execution and privacy by design:

1. **Private Data Processing**: All data processing occurs locally within MCP servers
2. **Minimal API Dependencies**: External APIs used only when providing unique value
3. **Configurable Authentication**: Secure credential management for external services
4. **Isolation Mechanisms**: Container-based isolation for sensitive operations
5. **Transparent Implementation**: All server code is open for inspection and modification

## Setup and Configuration

### Prerequisites

- **Claude Desktop**: Latest version with MCP support
- **Development Environment**:
  - Python 3.10+ (for Python-based servers)
  - Node.js 18+ (for JavaScript-based servers)
  - Docker Desktop (for container orchestration)
  - WSL2 (for Linux integration)

### Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/GrimFandango42/Claude-MCP-tools.git
   cd Claude-MCP-tools
   ```

2. **Setup server environments**:

   ```bash
   # Run the setup script for all servers
   ./setup_all_servers.bat
   
   # Or set up individual servers
   cd servers/windows-computer-use
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Claude Desktop**:
   - Update your Claude Desktop configuration at:
     `C:\Users\<Username>\AppData\Roaming\Claude\claude_desktop_config.json`
   - Use the provided configuration snippets in each server directory
   - Restart Claude Desktop after configuration changes

### Configuration Patterns

#### Python MCP Server

```json
{
  "server-name": {
    "command": "path\to\python.exe",
    "args": [
      "path\to\server.py"
    ],
    "cwd": "path\to\server",
    "env": {
      "PYTHONPATH": "path\to\server"
    },
    "keepAlive": true,
    "stderrToConsole": true
  }
}
```

#### Node.js MCP Server

```json
{
  "server-name": {
    "command": "node",
    "args": [
      "path\to\server.js"
    ],
    "cwd": "path\to\server",
    "keepAlive": true,
    "stderrToConsole": true
  }
}
```

#### NPX-based MCP Server

```json
{
  "server-name": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-name@latest"
    ],
    "keepAlive": true,
    "stderrToConsole": true
  }
}
```

### Troubleshooting

#### Common Issues

1. **"Server transport closed unexpectedly"**
   - Check that your server implementation has proper stream handling
   - Ensure `keepAlive: true` is set in configuration
   - Add `<nul` to batch files that launch Python servers
   - Implement proper signal handlers

2. **"Method not found"**
   - Implement all required MCP protocol methods
   - Add handlers for optional methods like `resources/list`

3. **API Authentication Failures**
   - Verify API keys are correctly set in environment variables
   - Check that credentials have not expired
   - Ensure proper environment variable sanitization

#### Log Files

Claude Desktop logs are stored at:
`C:\Users\<Username>\AppData\Roaming\Claude\logs\`

Key log files:

- `mcp-server-<servername>.log` - Server-specific logs
- `mcp.log` - General MCP system logs

## Development and Contributing

### Development Best Practices

1. **Check Community Resources First**
   - Review [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) before building custom solutions
   - Follow established patterns from successful implementations

2. **MCP Protocol Compliance**
   - Strictly adhere to JSON-RPC 2.0 specification
   - Keep stdout exclusively for JSON-RPC messages
   - Direct all logging and debugging output to stderr
   - Prefix stderr logs with server name (e.g., `[server-name]`)

3. **Stream Handling**
   - Implement proper stdin/stdout stream management
   - Use explicit signal handlers for SIGINT and SIGTERM
   - Never allow the process to exit prematurely
   - Implement proper try/catch blocks around all operations

4. **Testing Requirements**
   - Create comprehensive unit and integration tests
   - Validate proper stream handling and protocol compliance
   - Test with actual Claude Desktop integration
   - Verify error handling and recovery mechanisms

### Pull Request Guidelines

1. **Code Quality**
   - Follow language-specific style guides and best practices
   - Add comprehensive error handling and logging
   - Include detailed comments for complex logic

2. **Documentation**
   - Update README.md with new server details
   - Document all tools and their parameters
   - Add usage examples in the examples directory
   - Create/update test files for the new functionality

3. **Testing**
   - Include unit tests for core functionality
   - Add integration tests for Claude Desktop compatibility
   - Verify backward compatibility with existing configurations
   - Test with different operating system environments if relevant
