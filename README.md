# Claude MCP Tools

A comprehensive collection of tools and servers for extending Claude's capabilities through the Model Context Protocol (MCP), enabling desktop automation, file system access, browser control, and more.

![Claude MCP Tools Banner](ClaudeDesktopAgent/screenshots/claude_mcp_tools_banner.png)

## Overview

This project provides a set of tools that extend Claude's capabilities using the Model Context Protocol (MCP), allowing Claude to interact with your computer in various ways. The tools are designed to work with Claude Desktop and provide functionalities such as:

1. Accessing and manipulating the file system
2. Sequential thinking for complex problem-solving
3. Searching the web with Firecrawl
4. Controlling web browsers through Puppeteer
5. Managing GitHub repositories
6. Analyzing financial datasets
7. Interacting with Google Maps
8. Managing Gmail emails and labels
9. Fantasy Premier League data access
10. Document conversion using Pandoc

## Project Structure

The project consists of several components:

📦 Legacy Skills

These skills are no longer actively maintained or supported but are included for archival purposes. See `docs/legacy.md` for more information.

- Blender: 3D modeling with Blender (retired)

### 1. Active MCP Servers

These servers are currently configured and active in the Claude Desktop configuration:

| Server | Function | Description | Type |
|--------|----------|-------------|------|
| filesystem | File system operations | Access and manipulate files and directories | Official NPM Package |
| sequentialthinking | Step-by-step reasoning | Break down complex problems methodically | Official NPM Package |
| firecrawl | Web search | Search and retrieve information from the web | Official NPM Package (via npx) |
| puppeteer | Web automation | Control browsers and interact with websites | Official NPM Package |
| github | GitHub integration | Manage GitHub repositories and perform Git operations | Official NPM Package |
| financial-datasets | Financial analysis | Access and analyze financial data | Custom Implementation (`financial-datasets-mcp`) |
| googlemaps | Maps and location | Access Google Maps data and services | Official NPM Package (via npx) |
| gmail | Gmail integration | Manage Gmail emails and labels | Official NPM Package (via npx) |
| fantasy-pl | Fantasy Premier League data access | Access live and historical FPL data | Custom Implementation (`fpl_mcp`) |
| mcp-pandoc | Document conversion | Convert documents between various formats | Custom Implementation (`mcp-pandoc`) |

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

1. Verify API keys are correctly set in the configuration
2. Check for expired or invalid API keys
3. Ensure environment variables are properly set

#### 3. NPM Package Errors

**Symptoms:**

- Package not found errors
- Version compatibility issues

**Solutions:**

1. Run `npm install -g @modelcontextprotocol/server-name`
2. Check Node.js version (v14+ recommended)
3. Clear NPM cache with `npm cache clean --force`
4. Ensure package versions are compatible

## Future Development

### Potential MCP Servers Under Consideration

1. **Hugging Face Integration**: Local AI model integration using Hugging Face
2. **Vector Database**: Integration with vector databases for RAG applications
3. **Image Generation**: Integration with image generation services
4. Document Processing: Advanced document processing capabilities

## Contributing

Contributions are welcome! Here's how you can contribute to the project:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature/your-feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.