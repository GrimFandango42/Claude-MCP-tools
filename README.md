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
9. And more

## Project Structure

The project consists of several components:

### 1. Active MCP Servers

These servers are currently configured and active in the Claude Desktop configuration:

| Server | Function | Description | Type |
|--------|----------|-------------|------|
| filesystem | File system operations | Access and manipulate files and directories | Official NPM Package |
| sequentialthinking | Step-by-step reasoning | Break down complex problems methodically | Official NPM Package |
| firecrawl | Web search | Search and retrieve information from the web | Custom with API Key |
| puppeteer | Web automation | Control browsers and interact with websites | Official NPM Package |
| github | GitHub integration | Manage GitHub repositories and perform Git operations | Official NPM Package |
| financial-datasets | Financial analysis | Access and analyze financial data | Custom Implementation |
| googlemaps | Maps and location | Access Google Maps data and services | Official NPM Package |
| gmail | Email management | Access and manage Gmail emails and labels | Third-party NPM Package |

### 2. Additional MCP Implementations

Implementations that are available in the repository but not currently active in the Claude Desktop configuration:

- **hfspace-mcp**: Hugging Face Space integration (experimental)
- **http4k-mcp**: HTTP toolkit for MCP servers
- **mcp-gdrive**: Google Drive integration

## MCP Server Setup

### Prerequisites

- Node.js and npm
- Claude Desktop app
- API keys for specific services (Firecrawl, GitHub, Google Maps, Gmail)
- Windows environment

### Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/claude-mcp-tools.git
cd claude-mcp-tools
```

1. Install MCP server packages:

```bash
install-mcp-servers.bat
```

This will install all required NPM packages for the MCP servers.

1. Configure API Keys:

- For services requiring API keys, update the batch files or configuration with your API keys

### MCP Server Configuration

The current working configuration for Claude Desktop integrates eight MCP servers:

#### Filesystem Server

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "<path1>",
    "<path2>",
    "<path3>",
    "<path4>"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### Sequential Thinking Server

```json
"sequentialthinking": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-sequential-thinking"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### Firecrawl Server

```json
"firecrawl": {
  "command": "cmd",
  "args": [
    "/c",
    "set FIRECRAWL_API_KEY=your_api_key && npx -y firecrawl-mcp"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### Puppeteer Server

```json
"puppeteer": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-puppeteer"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### GitHub Server

```json
"github": {
  "command": "cmd",
  "args": [
    "/c",
    "set GITHUB_PERSONAL_ACCESS_TOKEN=your_token && npx -y @modelcontextprotocol/server-github"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### Financial Datasets Server

```json
"financial-datasets": {
  "command": "cmd",
  "args": [
    "/c",
    "C:\\AI_Projects\\Claude-MCP-tools\\financial-datasets-mcp\\run_server_claude.bat"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### Google Maps Server

```json
"googlemaps": {
  "command": "cmd",
  "args": [
    "/c",
    "set GOOGLE_MAPS_API_KEY=your_api_key && npx -y @modelcontextprotocol/server-google-maps"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

#### Gmail Server

```json
"gmail": {
  "command": "cmd",
  "args": [
    "/c",
    "npx -y @gongrzhe/server-gmail-autoauth-mcp"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

## Usage Examples

### File System Operations

Use the filesystem server to access files and directories:

```text
Can you list all files in my Documents directory?
```

### Sequential Thinking

Perform methodical step-by-step reasoning for complex problems:

```text
Can you help me solve this programming problem using sequential thinking?
```

### Web Search with Firecrawl

Search for information on the web:

```text
Can you search for current information about machine learning advancements?
```

### Web Automation with Puppeteer

Automate browser tasks:

```text
Can you navigate to a website and extract specific information for me?
```

### GitHub Repository Management

Manage GitHub repositories and perform Git operations:

```text
Can you help me create a new GitHub repository and push my project to it?
```

### Financial Data Analysis

Access and analyze financial data:

```text
Can you analyze recent stock market trends for major tech companies?
```

### Google Maps Integration

Use Google Maps capabilities:

```text
Can you find restaurants near my location and provide directions?
```

### Gmail Management

Access and manage Gmail emails and labels:

```text
Can you show me my unread emails in the inbox?
```

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
4. **Document Processing**: Advanced document processing capabilities

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
