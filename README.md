# Claude-MCP-tools

A collection of custom Model Context Protocol (MCP) servers designed to enhance Claude Desktop's capabilities. This project provides a toolkit for building, testing, maintaining, and extending Claude's functionality through custom MCP servers.

## MCP Server Inventory

### Production Ready Servers

1. **Windows Computer Use MCP Server**
   - **Location**: `servers/windows-computer-use/`
   - **Capabilities**: Full Computer Use API compliance with 16+ enhanced actions
   - **Key Features**: Screenshot capture, mouse/keyboard automation, WSL integration
   - **Status**: Production ready with all Computer Use API compliance tests passing

2. **Financial Datasets MCP Server**
   - **Location**: `servers/financial-mcp-server/`
   - **Capabilities**: Access to financial APIs for company data and market analysis
   - **Key Features**: Company facts, stock price data, financial statements
   - **Status**: Production ready with structured logging and error handling

3. **Docker Orchestration MCP Server**
   - **Location**: `servers/docker-orchestration-mcp/`
   - **Capabilities**: Comprehensive Docker container management and orchestration
   - **Key Features**: 19+ Docker tools for container, network, and volume management
   - **Status**: Production ready with 100% test pass rate

4. **N8n Workflow MCP Server**
   - **Location**: `servers/n8n-mcp-server/`
   - **Capabilities**: N8n workflow generation and management
   - **Key Features**: Workflow creation from natural language, template system
   - **Status**: Production ready with comprehensive documentation

### Configured MCP Servers (Official/Third-Party)

1. **Knowledge Memory** (Official): Persistent memory database for storing and retrieving important context
2. **Filesystem** (Official): File and directory operations within allowed directories
3. **Firecrawl** (Third-party): Web scraping, search, and extraction capabilities
4. **GitHub** (Official): GitHub repository, issue, and PR management
5. **SequentialThinking** (Third-party): Step-by-step reasoning framework
6. **SQLite** (Third-party): SQL database operations and management
7. **PluggedIn** (Third-party): Integration with the Plugged API for real-time data access

### Experimental/Archived MCP Servers

1. **Test Automation MCP**: Archived due to persistent connection stability issues
2. **Nest Control MCP**: Development paused due to stream handling failures
3. **Containerized Computer Use**: Alternative approach for isolation (active development)

## Examples and Testing

A comprehensive set of examples and tests are provided to demonstrate MCP server capabilities:

- **[Quick Server Tests](examples/quick_server_tests.md)**: Simple individual server tests to validate that each MCP server is working correctly. Use these first to ensure your servers are operational before attempting complex workflows.
- **[Comprehensive MCP Examples](examples/comprehensive_mcp_examples.md)**: 10 detailed examples showcasing complex multi-server workflows that demonstrate the full breadth and depth of your MCP capabilities. These examples combine multiple servers to create powerful automation pipelines for real-world use cases like financial analysis, research automation, and business intelligence.

### Example Categories

The examples cover these key areas:
- **Financial Intelligence**: Market analysis, investment research, competitive intelligence
- **Document Processing**: Web scraping, format conversion, knowledge management
- **Automation**: Desktop monitoring, productivity tracking, workflow optimization
- **Data Analysis**: Sports analytics, business intelligence, research synthesis
- **Content Strategy**: SEO analysis, competitive content research, strategic planning
- **Container Orchestration**: Docker container deployment, monitoring, and management
- **Workflow Automation**: N8n workflow creation, optimization, and execution

## Claude 4 Integration Strategy

With Claude 4's enhanced capabilities, our MCP development strategy focuses on complementary value rather than duplicating native features:

### Key Claude 4 Features to Leverage

- **Native Code Execution**: Claude 4's built-in code execution reduces the need for custom execution servers
- **Enhanced File Handling**: Improved document processing workflows significantly enhances document-based servers
- **Improved MCP Connector**: Better connection stability and debugging for all MCP servers

### Strategic Focus Areas

1. **External API Integrations**: Financial data, specialized services, local system access
2. **Domain-Specific Tools**: Industry-specific calculations, protocols, standards
3. **Local System Access**: Windows management, file system operations, hardware control
4. **Computer Use Implementation**: Desktop automation and GUI control with strong isolation
5. **Legacy System Bridges**: Connecting to older systems without modern APIs
6. **Container Orchestration**: Docker container management and orchestration
7. **Workflow Automation**: N8n workflow generation and management

### Implementation Priorities

- **Unique Value Only**: Build servers that provide capabilities Claude 4 cannot
- **Enhanced Integration**: Design for seamless work with native capabilities
- **Local-First**: Emphasize privacy and local control where Claude 4 has limitations
- **Containerization**: Improve isolation and security without sacrificing functionality

## Getting Started

1. **Start with Quick Tests**: Use the individual server tests to verify each server is functioning
2. **Progress to Complex Workflows**: Try the comprehensive examples that showcase multi-server integrations
3. **Monitor Performance**: Watch for server connection issues, API rate limits, and output validation
4. **Check Logs**: Monitor Claude Desktop logs at `C:\Users\<Username>\AppData\Roaming\Claude\logs\` for any issues

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflows. Ensure code is well-tested and documented.
