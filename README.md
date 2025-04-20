# Claude Desktop MCP Skills Tracker

A comprehensive reference for all Model Context Protocol (MCP) skills integrated with Claude Desktop, including both standard and custom implementations.

## Overview

This project serves as a central repository and reference for all Model Context Protocol (MCP) skills integrated with Claude Desktop, focusing on robust, local-first custom implementations alongside standard skills.

## MCP Skills Reference

### Standard MCP Skills (Configured in Claude Desktop)

These skills are configured directly in the Claude Desktop configuration file located at `C:\Users\Nithin\AppData\Roaming\Claude`.

| Server | Function | Description | Configuration Type |
|--------|----------|-------------|-------------------|
| filesystem | File system operations | Access and manipulate files and directories | Official NPM Package |
| sequentialthinking | Step-by-step reasoning | Break down complex problems methodically | Official NPM Package |
| firecrawl | Web search | Search and retrieve information from the web | Official NPM Package (via npx) |
| puppeteer | Web automation | Control browsers and interact with websites | Official NPM Package |
| github | GitHub integration | Manage GitHub repositories and perform Git operations | Official NPM Package |
| gmail | Email management | Access and manage Gmail emails and labels | Official NPM Package |
| googlemaps | Maps and location | Access Google Maps data and services | Official NPM Package |

### Custom MCP Skills (Implemented in this Repository)

| Server | Function | Description | Implementation |
|--------|----------|-------------|---------------|
| financial-datasets | Financial analysis | Access and analyze financial data including stocks, crypto, and economic indicators | Custom Python MCP Server |
| blender-mcp | 3D Modeling | Create and manipulate basic 3D objects in Blender | Custom Python Addon |
| gdrive-mcp-wrapper | Google Drive Access | Securely search and download files from Google Drive, converting formats locally | Custom Node.js Wrapper |
| firecrawl | Web Scraping/Search | Enhanced web scraping and search with local processing and fallback | Custom Node.js Hybrid (using official package) |

## Financial Datasets MCP Server

The Financial Datasets MCP server provides Claude Desktop with access to comprehensive financial data including:

- Company financial statements (income statements, balance sheets, cash flow)
- Stock price data and technical indicators
- Economic indicators and market data
- Cryptocurrency prices and market data
- Financial news and sentiment analysis

### Setup Instructions

Setup instructions vary per custom MCP server. Refer to the specific directory for each server (e.g., `financial-datasets-mcp`, `blender-mcp`, etc.) for detailed setup guides.

## Development Best Practices

Based on integration experience, the following best practices are recommended for developing custom MCP servers for Claude Desktop on Windows:

- **Prioritize Official Packages:** Use official MCP server packages (`npx -y @package/name`) whenever possible.
- **Robust Process Management:** Employ wrappers (e.g., batch files, PM2 for Node.js) for stability and environment setup.
- **Stable Communication:** Prefer direct stdin/stdout over WebSockets and ensure clean JSON-RPC communication.
- **Windows Compatibility:** Handle Windows-specifics like signal handling, port management, and path formats carefully.
- **Secure Authentication:** Use secure methods like Windows Credential Manager where applicable.
- **Comprehensive Logging:** Implement structured logging to aid debugging (check `C:\Users\Nithin\AppData\Roaming\Claude\logs\`).
- **MCP Compliance:** Strictly adhere to JSON-RPC 2.0 and MCP specifications (initialize, shutdown, capabilities).

Refer to the project memories for more detailed guidelines.

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

**Solutions:**

1. Verify API keys are correctly set in the `.env` file
2. Check for expired or invalid API keys
3. Ensure environment variables are properly loaded

#### 3. Filesystem Access Denied

**Symptoms:**

- MCP server reports "Access denied" or similar errors when trying to read/write files.

**Solutions:**

1. Verify the target path is within the allowed directories configured for the `filesystem` MCP server in Claude Desktop.
2. Ensure exact path matching, including correct case and backslashes (`\`) for Windows.
3. Use canonical absolute paths as returned by `mcp0_list_allowed_directories`.
4. Check Claude Desktop logs (`C:\Users\Nithin\AppData\Roaming\Claude\logs\`) for specific error details.

## Future Development

Future plans include:

- Ongoing maintenance and enhancement of existing custom MCPs.
- Exploration of an `http4k`-based central gateway to integrate various HTTP services.
- Tracking and integrating new standard MCP skills as they become available.

## GitHub Repository Status

The repository currently has 0 open issues. This status is regularly monitored and updated.

| Category | Count |
|----------|-------|
| Open Issues | 0 |
| Closed Issues | 0 |
| Total Issues | 0 |

## References

- [Model Context Protocol Official Documentation](https://modelcontextprotocol.io/)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- [MCP Examples](https://modelcontextprotocol.io/examples)