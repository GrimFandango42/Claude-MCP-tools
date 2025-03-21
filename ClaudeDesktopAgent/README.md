# Claude Desktop Agent

A framework for extending Claude's capabilities on desktop by providing access to custom tooling and automation features.

## Overview

This system enables Claude to interact with your computer through a custom bridge that connects the Claude desktop app to various computer control functions via the Agent API. The agent provides Claude with abilities such as:

- Taking screenshots and analyzing them
- Browsing the web
- Launching applications
- Navigating the file system
- Executing code

## Architecture

- **Claude Integration Layer**: Interfaces with Claude desktop app via Agent API
- **Core Agent Service**: Central API server that handles incoming tool use requests
- **Computer Control Modules**: Specialized modules for different computer interactions
- **MCP Server**: Model Context Protocol server that provides custom capabilities to Claude
- **Debugging & Monitoring Framework**: Tools for logging and diagnostics

## Getting Started

### Prerequisites

- Python 3.9+
- Claude desktop app
- Anthropic API key with Vision capabilities

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Run the server:
   ```
   python -m app.main
   ```

### Running the MCP Server

The MCP (Model Context Protocol) server provides custom capabilities to Claude Desktop:

1. Run the MCP server:
   ```
   python run_mcp_server.py
   ```
2. The MCP server will start on port 8090 by default (configurable in .env)
3. Connect Claude Desktop to the MCP server by configuring the MCP URL in Claude settings

## Modules

### Screenshot Module

Captures desktop screenshots and uses Claude Vision API to analyze content.

### MCP Capabilities

The MCP server provides the following capabilities to Claude:

- **Screenshot Tool**: Capture screenshots of your desktop or specific regions
- **Screenshot Analysis**: Analyze screenshots using Claude Vision API
- More capabilities coming soon!

### Web Browser Module (Planned)

Allows Claude to browse the web, extract content, and perform searches.

### Application Launcher (Planned)

Enables Claude to launch and manage desktop applications.

## Development Roadmap

1. **Phase 1**: Core Infrastructure and Screenshot Module
2. **Phase 2**: MCP Integration and Custom Capabilities
3. **Phase 3**: Web Browser Module
4. **Phase 4**: Application Launcher and File System Navigation
5. **Phase 5**: Input Control and Window Management
6. **Phase 6**: Code Execution Integration

## Security Considerations

This agent runs locally and has access to your computer. Please review the code and understand the security implications before running it.

## License

MIT
