# Claude-MCP-tools

A collection of custom Model Context Protocol (MCP) servers designed to enhance Claude Desktop's capabilities. This project provides a toolkit for building, testing, maintaining, and extending Claude's functionalities through custom MCP integrations.

## Overview

This repository houses custom MCP servers that extend Claude Desktop's capabilities beyond its built-in tools. Each server adheres to the JSON-RPC 2.0 protocol over STDIO for communication with Claude Desktop's MCP Client, providing specialized tools and context.

### What is MCP?

MCP (Model Context Protocol) follows a client-server model:

- **Hosts** are LLM applications (e.g., Claude Desktop).
- Each Host runs one or more **MCP Clients** managing a 1:1 JSON-RPC/STDIO transport with an MCP Server process.
- **Servers** provide context, tools, and prompts to Clients.
- The transport layer handles message framing over STDIN/STDOUT; diagnostic logs should go to STDERR.
- Key lifecycle phases: `initialize` (capability negotiation), message exchange (tool calls), and `shutdown`/`exit`.

## MCP Server Inventory

### Active Custom Implemented MCP Servers

These servers are actively developed and maintained within this repository:

- **financial-datasets-mcp**: (Python) Accesses financial data via the Financial Datasets API. Features working endpoints for company facts, stock prices, financial statements (income, balance sheet, cash flow), and cryptocurrency data. Implements structured JSON logging, graceful shutdown, and enhanced error handling. Located in `servers/financial-mcp-server`.
- **knowledge-memory-mcp**: (Python) Provides persistent knowledge management with features like note creation, retrieval, update, deletion, tagging, and search (hybrid Zettelkasten/vector approach planned). Follows a local-first, privacy-preserving approach. Located in `servers/knowledge-memory-mcp`.
- **windows-computer-use**: (Python) 🚀 **NEW** Windows Computer Use implementation providing desktop automation and Computer Use API compatibility. Features screenshot capture, mouse/keyboard automation, PowerShell execution, WSL bridge integration, and application control. Designed for coding workflows with Claude Code and VS Code in WSL environments. Located in `servers/windows-computer-use`.

### Experimental MCP Servers

These servers are in early development stages or have been archived:

- **test-automation-mcp**: (Node.js) Originally aimed to provide a proxy-based server for testing Claude Desktop and other MCP servers, with features like application launching and log retrieval. Initial implementations in `servers/test-automation-mcp` faced connection stability challenges. The insights gained contributed to the development of the `mcp-server-template` (see below), which now provides a more reliable foundation and integrated testing capabilities for developing any MCP server, including future iterations of a dedicated test automation server.
- **mcp-nest-control**: (Node.js) Google Nest device control via Smart Device Management API. Currently facing authentication challenges.
- **mcp-pandoc**: (Node.js) Document conversion using Pandoc with support for multiple formats.
- **mcp-http-gateway**: (Kotlin) Work in progress central HTTP gateway for unified service access.
- **custom-win-mgmt-mcp**: (Node.js/TypeScript) Intended to provide Windows management functionalities (system info, process listing). Archived due to persistent 'transport closed unexpectedly' errors after initialization, likely related to `stdin` stream closure, similar to `test-automation-mcp`.

### Standard Configured MCP Servers

These are official or third-party servers configured for use with Claude Desktop:

- **filesystem**: (Official) File operations within allowed directories.
- **firecrawl**: (Official) Web scraping and content extraction.
- **github**: (Official) GitHub repository operations.
- **puppeteer**: (Official) Browser automation.
- **sequentialthinking**: (Official) Step-by-step reasoning framework.
- **pluggedin-mcp-proxy**: (Third-party) Integration with the Plugged API for real-time data access.

## Development Toolkit & Testing

### MCP Server Template

- **Location**: `mcp-server-template/`
- **Description**: A standardized, robust, and testable Node.js (TypeScript) template for rapidly developing new MCP servers. It is built upon the official `@modelcontextprotocol/server` library and includes:
  - Structured project setup with TypeScript.
  - Core server implementation (`src/index.ts`).
  - Utilities for Winston-based structured logging (to `stderr`) and configuration validation.
  - An example server (`src/examples/simple-server.ts`).
  - A Jest testing framework with example unit tests (`test/server.test.ts`).
  - An MCP protocol validation tool (`src/tools/validate-mcp.ts`) to ensure compliance.

- **Purpose**: This template is the recommended starting point for all new MCP server development within this project. It aims to simplify development, ensure adherence to MCP best practices, enhance reliability, and provide a consistent structure across servers.

### Automated Testing Strategy

The approach to MCP server-specific automated testing has evolved to leverage the capabilities integrated within the `mcp-server-template`.

- **Unit Testing**: Each server developed from the template should include comprehensive unit tests using Jest to verify the functionality of its tools and internal logic.
- **Protocol Compliance**: The `validate-mcp.ts` tool within the template can be used to perform automated checks, ensuring the server correctly handles MCP lifecycle messages (initialize, shutdown) and tool calls.
- **Integration Testing**: While the template provides a strong foundation, further integration testing within the Claude Desktop environment remains crucial for each new server.

This structured approach, centered around the `mcp-server-template`, aims to maximize confidence in MCP server implementations and streamline the development process.

## Claude Desktop Configuration Management

The Claude Desktop configuration file is located at `C:\Users\<Username>\AppData\Roaming\Claude\claude_desktop_config.json`. This file contains settings for all MCP servers and must be edited directly to add or modify server configurations.

### Configuration Patterns

Successful MCP server configurations typically follow these patterns:

#### 1. NPX Direct Execution (Preferred)
```json
{
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-SERVERNAME"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### 2. Environment Variables with API Keys
```json
{
  "command": "cmd",
  "args": [
    "/c",
    "set API_KEY=value && npx -y package-name"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### 3. Direct Node.js Execution
```json
{
  "command": "node",
  "args": [
    "C:\\AI_Projects\\Claude-MCP-tools\\servers\\servername\\server.js"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### 4. Batch File Execution
```json
{
  "command": "cmd",
  "args": [
    "/c",
    "cd /d C:\\AI_Projects\\Claude-MCP-tools\\servers\\servername && batch\\start.bat"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

### Best Practices

- Always include `keepAlive: true` to maintain connections.
- Use `stderrToConsole: true` to capture server logs for debugging.
- After changing the configuration, restart Claude Desktop.

## Log Files and Debugging

Claude Desktop stores log files, including those for MCP servers, in:
`C:\Users\<Username>\AppData\Roaming\Claude\logs\`

Key log files include:
- `mcp-server-<servername>.log` - Logs specific to each MCP server
- `mcp.log` - General MCP system logs

### Common Issues and Solutions

#### Connection Stability Problems

**Symptoms:** "Server transport closed unexpectedly" errors, servers that initialize but quickly disconnect.

**Common Causes:**
1. Premature closure of the stdin stream
2. Uncaught exceptions causing process termination
3. Improper signal handling
4. Process exiting before completing the response

**Solutions:**
1. Use proxy architecture that separates MCP protocol handling from complex functionality
2. Add empty data event handlers (`process.stdin.on('data', () => {})`)
3. Implement comprehensive signal handlers (SIGINT, SIGTERM)
4. Use `keepAlive: true` in MCP configuration
5. For Windows, use batch file wrappers that maintain stdin properly

#### API Authentication Issues

**Symptoms:** 401/403 errors in logs, "Authentication failed" responses, "API key invalid" errors.

**Causes:** Missing or invalid API keys, incorrect environment variable names, encoding issues in configuration files.

**Detectable In:** Server-specific logs, response logs.

**Solutions:**

1. **Check Configuration:** Ensure API keys are correctly set in the `claude_desktop_config.json`, often using the `cmd /c "set KEY=value && npx ..."` pattern. Verify the key name (`API_KEY`, `GITHUB_TOKEN`, `FINANCIAL_DATASETS_API_KEY`, etc.) matches what the server expects.
2. **Verify Key Validity:** Confirm the API key itself is active and has the necessary permissions for the intended actions.
3. **Environment Variables:** If the server relies on system environment variables, ensure they are set correctly *before* Claude Desktop starts the server process. Using the `cmd /c "set ..."` pattern is generally more reliable for MCP configuration.
4. **Check Encoding:** For Python-based servers using .env files, ensure proper UTF-8 encoding without BOM or null bytes between characters.

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/GrimFandango42/Claude-MCP-tools.git
   cd Claude-MCP-tools
   ```

2. **Install Dependencies:** Navigate to individual server directories (e.g., `servers/test-automation-mcp`) and install their dependencies (e.g., `npm install` for Node.js, `pip install -r requirements.txt` or `uv sync` for Python).
3. **Configure Claude Desktop:** Add/update the server configurations in your `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json` as needed (refer to patterns above and specific server READMEs). **Remember to back up this file before editing manually.**
4. **Restart Claude Desktop:** A restart is typically required for Claude Desktop to pick up changes to `claude_desktop_config.json` or recognize newly started servers.
5. **Run Servers:** Start the MCP servers manually (e.g., using their `run-server.bat`, `run_server_claude.bat` or `python server.py` commands) or ensure Claude Desktop is configured to launch them automatically based on your JSON config.

## Examples and Testing

This repository includes comprehensive examples to help you test and explore the capabilities of your MCP server ecosystem:

### Example Files

- **[Comprehensive MCP Examples](examples/comprehensive_mcp_examples.md)**: 10 detailed examples showcasing complex multi-server workflows that demonstrate the full breadth and depth of your MCP capabilities. These examples combine multiple servers to create powerful automation pipelines for real-world use cases like financial analysis, research automation, and business intelligence.

- **[Quick Server Tests](examples/quick_server_tests.md)**: Simple individual server tests to validate that each MCP server is working correctly. Use these first to ensure your servers are operational before attempting complex workflows.

### Getting Started with Examples

1. **Start with Quick Tests**: Use the individual server tests to verify each server is functioning
2. **Progress to Complex Workflows**: Try the comprehensive examples that showcase multi-server integrations
3. **Monitor Performance**: Watch for server connection issues, API rate limits, and output validation
4. **Check Logs**: Monitor Claude Desktop logs at `C:\Users\<Username>\AppData\Roaming\Claude\logs\` for any issues

### Example Categories

The examples cover these key areas:
- **Financial Intelligence**: Market analysis, investment research, competitive intelligence
- **Document Processing**: Web scraping, format conversion, knowledge management
- **Automation**: Desktop monitoring, productivity tracking, workflow optimization
- **Data Analysis**: Sports analytics, business intelligence, research synthesis
- **Content Strategy**: SEO analysis, competitive content research, strategic planning

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflows. Ensure code is well-tested and documented.