# Claude-MCP-tools

A collection of custom Model Context Protocol (MCP) servers for enhancing Claude Desktop capabilities. This project serves as a comprehensive toolkit for building, maintaining, and extending Claude's abilities through custom MCP servers.

## Overview

This repository contains custom MCP servers that extend Claude Desktop's capabilities beyond the built-in tools. Each server follows the JSON-RPC protocol to communicate with Claude, providing specialized tools and contexts that Claude can access.

### What is MCP?

MCP (Model Context Protocol) follows a client-server model:

- **Hosts** are LLM applications (e.g., Claude Desktop)
- Each Host runs one or more **MCP Clients** that maintain a 1:1 JSON-RPC/STDIO transport with an MCP Server process
- **Servers** provide context, tools, and prompts to Clients
- Transport layer handles message framing over STDIN/STDOUT; logs go to STDERR
- Lifecycle phases: initialize (capability negotiation), message exchange (tool calls), shutdown/exit

## MCP Server Inventory

### Custom Implemented MCP Servers

- **financial-datasets-mcp**: (Python) Accesses financial data (stocks, statements, crypto, economic indicators). Features structured JSON logging, graceful shutdown, and `pytest` testing. Located in `mcp-servers/financial-datasets-mcp`.
- **firecrawl-mcp**: (Node.js - *Assumed*) Hybrid implementation with process-based execution and fallback mechanism for web scraping/search. (Location TBC - may be integrated elsewhere or archived).
- **google-drive-mcp**: (Node.js - *Assumed*) Custom wrapper for Google Drive API with enhanced capabilities for downloading files. (Location TBC - may be integrated elsewhere or archived).
- **knowledge-memory-mcp**: (Python) Provides persistent knowledge management with hybrid Zettelkasten and vector search capabilities. Follows local-first, privacy-preserving approach. Located in `servers/knowledge-memory-mcp`.
- **mcp-nest-control**: (Node.js/NestJS) Controls Nest devices (thermostat, etc.). Located in `mcp-nest-control`.
- **test-automation-mcp**: (Node.js) Enables end-to-end browser and app testing using Playwright. Features screenshot capture, test step execution, and performance metrics collection. Located in `servers/test-automation-mcp`.

### Standard Configured MCP Servers

These are official or third-party MCP servers configured directly in Claude Desktop (via `claude_desktop_config.json`) without custom code maintenance in *this* repo:

- **filesystem**: Standard MCP server for file system operations.
- **sequentialthinking**: Provides structured thinking tools.
- **puppeteer**: Browser automation and web interaction.
- **firecrawl**: Standard web scraping and searching (distinct from the custom hybrid implementation potentially listed above).
- **github**: GitHub repository integration.
- **gmail**: Email operations via Gmail API.
- **googlemaps**: Google Maps integration.
- **pluggedin-mcp-proxy**: API proxy server (potentially custom but managed outside this repo structure, or a standard integration).

### Experimental/Archived MCP Servers

These servers were prototyped or explored but are not actively maintained or have been superseded:

- **blender-mcp**: Addon for Blender 3D. Found in `archive/blender-mcp`.
- **http4k-mcp**: Experimental central HTTP-based service gateway.

## Configuration

Claude Desktop configuration file location:
`C:\Users\[Username]\AppData\Roaming\Claude\claude_desktop_config.json`

This file contains custom MCP server configurations and settings for standard servers.

### Filesystem MCP Allowed Directories

The filesystem MCP server (mcp0) has restricted access. Common allowed directories include:

- `C:\Users\[Username]\Downloads`
- `C:\Users\[Username]\OneDrive\Desktop` *(Path may vary)*
- `C:\Users\[Username]\AppData\Roaming\Claude`
- `C:\AI_Projects` *(Based on project structure)*

*Note: Check your specific `claude_desktop_config.json` for the exact allowed paths.* Tools will fail if the target path is outside these allowed directories.

## Troubleshooting

### Common Issues and Solutions

#### 1. MCP Server Connection Failed

**Symptoms:**

- Claude reports it cannot connect to the MCP server
- "Tool Not Available" error in Claude
- Server refuses connection

**Solutions:**

1. Ensure the server is running (check process list)
2. Verify the correct port is being used (check configuration)
3. Check for port conflicts (use `netstat -ano` to see all open ports)
4. Verify firewall settings are not blocking the connection
5. Restart the server with administrator privileges

#### 2. API Key Errors

**Symptoms:**

- Authentication failures
- API key not recognized
- Server returns permission denied errors

**Solutions:**

1. Verify API keys are correctly set in the `.env` file
2. Check for expired or invalid API keys
3. Ensure environment variables are properly loaded