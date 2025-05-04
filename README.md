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

- **financial-datasets-mcp**: (Python) Accesses financial data (stocks, statements, crypto, economic indicators). Features structured JSON logging, graceful shutdown, and `pytest` testing. Located in `servers/financial-datasets-mcp`.
- **knowledge-memory-mcp**: (Python) Provides persistent knowledge management with features like note creation, retrieval, update, deletion, tagging, and search (hybrid Zettelkasten/vector approach planned). Follows a local-first, privacy-preserving approach. Located in `servers/knowledge-memory-mcp`.
- **mcp-nest-control**: (Node.js/NestJS) Controls Google Nest devices (thermostat, etc.). Located in `servers/mcp-nest-control`.
- **test-automation-mcp**: (Node.js) Enables end-to-end browser testing using Playwright. Features browser launch, navigation, interaction (clicks, fills), screenshot capture, assertions, and potential for performance metrics. Located in `servers/test-automation-mcp`.

### Standard Configured MCP Servers

These are official or third-party MCP servers configured directly in Claude Desktop (via its configuration file) without custom code maintenance *in this specific repo*:

- **filesystem**: Standard MCP server for file system operations (provided by Claude Desktop).
- **sequentialthinking**: Provides structured thinking tools (provided by Claude Desktop).
- **puppeteer**: Browser automation and web interaction (likely using `@modelcontextprotocol/server-puppeteer`).
- **firecrawl**: Web scraping and searching (likely using `@modelcontextprotocol/server-firecrawl`).
- **github**: GitHub repository integration (likely using `@modelcontextprotocol/server-github`).
- **gmail**: Email operations via Gmail API (potentially using `@gongrzhe/server-gmail-autoauth-mcp` or similar).
- **googlemaps**: Google Maps integration (likely using `@modelcontextprotocol/server-google-maps`).
- **pluggedin-mcp-proxy**: Purpose TBD - likely an API proxy server (potentially custom but managed elsewhere, or a standard integration).

### Archived / Experimental MCP Servers

These servers were prototyped or explored but are not currently active or maintained within the main `servers` directory:

- **blender-mcp**: Addon for Blender 3D. Found in `archive/blender-mcp`.
- **firecrawl-mcp**: (Node.js - *Archived?*) Previous custom implementation attempt for web scraping/search. May exist in Git history or `archive`.
- **google-drive-mcp**: (Node.js - *Archived?*) Previous custom wrapper for Google Drive API. May exist in Git history or `archive`.
- **http4k-mcp**: Experimental central HTTP-based service gateway. Likely archived.

## Configuration

Claude Desktop configuration file location (Windows):
`C:\Users\[Username]\AppData\Roaming\Claude\claude_desktop_config.json`

This file contains custom MCP server configurations (command, arguments, keepAlive settings) and settings for standard servers.

### Filesystem MCP Allowed Directories

The standard `filesystem` MCP server (mcp0) has restricted access. Common allowed directories include:

- `C:\Users\[Username]\Downloads`
- `C:\Users\[Username]\OneDrive\Desktop` *(Path may vary depending on OneDrive setup)*
- `C:\Users\[Username]\AppData\Roaming\Claude`
- `C:\AI_Projects` *(Based on common project structure in this workspace)*

*Note: Always check your specific `claude_desktop_config.json` for the exact allowed paths configured for the filesystem server. Tools will fail if the target path is outside these allowed directories.* Paths must be canonical and correctly cased.

## Development Workflow

This project follows a local-first development philosophy.

1.  **Branching**: New features or significant changes should be developed on separate feature branches (e.g., `feature/test-automation-mcp`).
2.  **Committing**: Commit changes locally frequently.
3.  **Syncing (Local as Source of Truth)**: To update the remote repository (GitHub) to match your local state completely, use a force push:

   ```bash
   # Ensure you are on the correct branch (e.g., master or main)
   git checkout master
   # Force push local state to remote, overwriting remote changes
   git push origin master --force
   ```

   *Use `--force` with caution, as it overwrites remote history.*
4.  **Pull Requests**: For collaborative review or merging feature branches into the main branch, create Pull Requests on GitHub.

## Troubleshooting

### Common Issues and Solutions

#### 1. MCP Server Connection Failed

**Symptoms:**

- Claude reports it cannot connect to the MCP server.
- "Tool Not Available" error message in Claude.
- Server process might not be running or is unresponsive.

**Solutions:**

1.  **Verify Server Process:** Ensure the server executable/script is running (check Task Manager or use `tasklist | findstr "node"` / `tasklist | findstr "python"`).
2.  **Check Configuration:** Double-check the `command` and `args` in `claude_desktop_config.json` are correct (path, executable name, flags).
3.  **Review Logs:** Examine the server's specific log file in `C:\Users\[Username]\AppData\Roaming\Claude\logs\` (e.g., `mcp-server-test-automation.log`) and the general `mcp.log` for errors.
4.  **Port Conflicts:** If the server uses a specific port (less common for STDIO MCP), check for conflicts using `netstat -ano | findstr "LISTENING"`.
5.  **Firewall:** Ensure Windows Defender Firewall or other security software isn't blocking Node.js or Python execution.
6.  **Restart Claude:** Sometimes a simple restart of Claude Desktop resolves connection glitches.

#### 2. Filesystem MCP Access Denied

**Symptoms:**

- Tools like `mcp0_read_file` or `mcp0_write_file` fail with an "Access denied" or "path outside allowed directories" error.

**Solutions:**

1.  **Verify Path:** Ensure the target file path is *exactly* within one of the configured `allowedWritePaths` or `allowedReadPaths` in `claude_desktop_config.json` for the filesystem server.
2.  **Check Casing/Separators:** Windows paths can be case-insensitive, but the MCP server might be strict. Use canonical paths (e.g., `C:\AI_Projects\...` not `c:/ai_projects/...`).
3.  **Path Normalization Issues:** Occasionally, the MCP server might struggle with certain path formats. If a path *should* be allowed but fails, try accessing the file using a different tool (like Cascade's built-in `view_file` if applicable) as a workaround or investigate the server configuration further.

#### 3. API Key Errors

**Symptoms:**

- Authentication failures for servers requiring API keys (e.g., Firecrawl, GitHub).
- Server logs indicate missing or invalid credentials.

**Solutions:**

1.  **Check Configuration:** Ensure API keys are correctly set in the `claude_desktop_config.json`, often using the `cmd /c "set KEY=value && npx ..."` pattern.
2.  **Verify Key Validity:** Confirm the API key itself is active and has the necessary permissions.
3.  **Environment Variables:** If the server relies on system environment variables, ensure they are set correctly *before* Claude Desktop starts the server process.

## Getting Started

1.  **Clone the repository:**

   ```bash
   git clone https://github.com/GrimFandango42/Claude-MCP-tools.git
   cd Claude-MCP-tools
   ```

2.  **Install Dependencies:** Navigate to individual server directories (e.g., `servers/test-automation-mcp`) and install their dependencies (e.g., `npm install` for Node.js, `pip install -r requirements.txt` or `uv sync` for Python).
3.  **Configure Claude Desktop:** Add/update the server configurations in your `claude_desktop_config.json` as needed.
4.  **Run Servers:** Start the MCP servers manually or ensure Claude Desktop is configured to launch them.
5.  **Restart Claude Desktop:** Apply configuration changes.