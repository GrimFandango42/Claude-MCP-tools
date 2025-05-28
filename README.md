# Claude MCP Tools

A comprehensive collection of Model Context Protocol (MCP) servers designed to enhance Anthropic's Claude Desktop capabilities through custom integrations, external APIs, and system automation.

## 📊 Current Status

This project provides a robust ecosystem of **18 operational MCP servers**, enabling a wide range of advanced automation and integration scenarios. Recent key achievements include:

- **Full Computer Use API Compliance**: The `Windows Computer Use MCP` now fully supports all 16 enhanced actions.
- **Claude Code Integration**: A new `Claude Code Integration MCP` facilitates a hybrid AI development system, bridging Claude Desktop with specialized code execution agents.
- **API Gateway Deployment**: The `API Gateway MCP` is operational, managing access to multiple AI provider APIs.

### Server Breakdown

- ✅ **9 Custom Production Servers**: Developed specifically for this project.
- ✅ **9 Third-party & Official Servers**: Integrated and configured for use.

## 📁 Project Structure

```text
Claude-MCP-tools/
├── .github/                    # GitHub Actions workflows and issue templates
├── .vscode/                    # VSCode workspace settings and launch configurations
├── examples/                   # Usage examples and test workflows for MCP servers
│   ├── comprehensive_mcp_examples.md
│   └── quick_server_tests.md
├── scripts/                    # Utility scripts (testing, deployment, validation)
│   ├── validate_servers.py
│   └── deploy_all.sh
├── servers/                    # Source code for all MCP servers
│   ├── claude-code-integration-mcp/  # ✨ NEW
│   ├── windows-computer-use/
│   ├── containerized-computer-use/
│   ├── api-gateway-mcp/
│   ├── docker-orchestration-mcp/
│   ├── financial-mcp-server/
│   ├── knowledge-memory-mcp/
│   ├── n8n-mcp-server/
│   └── firecrawl-mcp-custom/
├── .gitignore                  # Specifies intentionally untracked files
├── claude_desktop_config.json  # Example configuration for Claude Desktop
├── LICENSE                     # Project license (e.g., MIT, Apache 2.0)
├── PROJECT_MEMORY_COMPREHENSIVE.md # Detailed project memory and knowledge base
├── PROJECT_STATUS.md           # Current project status and milestones
├── README.md                   # This file: Overview, setup, and usage guide
├── UPDATED_ROADMAP_MAY_2025.md # Roadmap and future development plans
└── SERVER_INVENTORY.md         # Catalog of all servers
```

## 🚀 Core Custom Servers

### 1. **Claude Code Integration MCP** (`claude-code-integration-mcp`) ✨ **NEW**

- **Capabilities**: Enables a hybrid AI development workflow by integrating Claude Desktop (strategic orchestrator) with a specialized Claude Code CLI (execution agent) for local/remote repository operations.
- **Features**: Task delegation, monitoring, and context preservation across AI agents for software development tasks.

### 2. **Windows Computer Use MCP** (`windows-computer-use`)

- **Capabilities**: Provides native Windows desktop automation. Fully compliant with Anthropic's Computer Use API, supporting all 16 enhanced actions including advanced mouse/keyboard control, screenshot capture, and window management.
- **Tools**: `computer_20250124`, `text_editor_20250429`, `bash_20250124` (WSL integration).

### 3. **Containerized Computer Use MCP** (`containerized-computer-use`)

- **Capabilities**: Offers a secure, isolated environment for desktop automation using Docker and VNC (XVFB + Fluxbox). Also Computer Use API compliant.
- **Benefits**: Cross-platform compatibility, enhanced security for sensitive operations.

### 4. **API Gateway MCP** (`api-gateway-mcp`)

- **Capabilities**: Manages access to multiple AI provider APIs (e.g., OpenAI, Anthropic) with intelligent routing, cost optimization, response caching, and usage analytics.
- **Tools**: `call_api`, `list_providers`, `get_usage_stats`, `estimate_cost`, `manage_cache`, `gateway_status`.

### 5. **Docker Orchestration MCP** (`docker-orchestration-mcp`)

- **Capabilities**: Provides comprehensive control over Docker environments, including container lifecycle management, image operations, and network/volume configuration (19+ tools).

### 6. **Financial Datasets MCP** (`financial-mcp-server`)

- **Capabilities**: Accesses financial data via the Financial Datasets API, including company facts, stock prices, and income statements.

### 7. **Knowledge Memory MCP** (`knowledge-memory-mcp`)

- **Capabilities**: Offers persistent knowledge management with vector search, note CRUD operations, tagging, and semantic search capabilities.

### 8. **N8n Workflow MCP** (`n8n-mcp-server`)

- **Capabilities**: Integrates with the N8n automation platform, enabling natural language generation and management of complex workflows.

### 9. **Firecrawl Custom MCP** (`firecrawl-mcp-custom`)

- **Capabilities**: A customized version of Firecrawl for advanced web scraping and content extraction tasks.

## 🔧 Integrated Third-Party & Official Servers

This ecosystem also integrates the following operational servers:

- **`filesystem`**: File and directory operations within allowed paths.
- **`github`**: Repository management, issue tracking, and code deployment.
- **`memory` (Official)**: Standard MCP server for persistent context storage.
- **`sequentialthinking`**: Framework for step-by-step reasoning and problem decomposition.
- **`playwright`**: Browser automation for web interaction, form filling, and testing.
- **`screenpilot`**: Desktop automation with screen analysis and element detection.
- **`sqlite`**: Database operations for SQLite databases.
- **`mcp-pandoc`**: Document format conversion and content transformation.
- **`fantasy-pl`**: Sports analytics for Fantasy Premier League management.

## 🛠️ Claude Code CLI Utilities

This project includes utilities to interact with and test the **Claude Code CLI**, a separate command-line tool from Anthropic. These utilities are located in the `claude-code-integration-mcp/` directory.

**Important:** These are *not* MCP servers that Claude Desktop connects to directly. They are helper scripts for developers working with the Claude Code CLI.

### 1. Claude Code Wrapper (`claude_code_wrapper.py`)

- **Purpose**: Provides a Python wrapper to execute Claude Code CLI tasks. It's designed to mitigate `asyncio` event loop conflicts that can occur when calling the CLI from other asynchronous Python applications.
- **Functionality**:
  - Automatically attempts to locate the `claude-code` executable in common installation paths.
  - Executes CLI commands synchronously using `subprocess.run`.
  - Can be used as a Python module or directly from the command line.
- **Usage (Command Line)**:

  ```bash
  python claude-code-integration-mcp/claude_code_wrapper.py "<task_description>" [optional_project_path]
  ```

- **Prerequisites**: Requires the Claude Code CLI to be installed and accessible in the system's PATH or one of the searched locations.

### 2. Claude Code Integration Test (`claude_code_integration_test.py`)

- **Purpose**: A Python-based test suite to verify the installation and basic functionality of the Claude Code CLI.
- **Functionality**:
  - Checks for Node.js, NPM, and Claude Code CLI installations and their versions (assumes they are in the system PATH).
  - Tests basic CLI commands like `claude --help`.
  - Sets up a temporary test project and attempts to run a simple task using `claude --print`.
  - Cleans up the test project directory after execution.
- **Usage**:

  ```bash
  python claude-code-integration-mcp/claude_code_integration_test.py
  ```

- **Prerequisites**: Requires the Claude Code CLI to be installed, configured (including authentication if needed), and accessible in the system's PATH.

## 🚀 Key Capabilities

This MCP server ecosystem unlocks a wide range of capabilities:

### AI-Assisted Development

- **Hybrid Development Model**: Integrate Claude Desktop's strategic oversight with specialized code execution agents (`Claude Code Integration MCP`).
- **Automated Coding Tasks**: Leverage Computer Use API compliance for automating IDE interactions, code generation, and testing (`Windows Computer Use MCP`, `Containerized Computer Use MCP`).

### System Administration & Automation

- **Comprehensive Desktop Automation**: Full GUI control, application management on Windows and in isolated Linux environments.
- **Dockerized Operations**: Full lifecycle management of Docker containers, images, networks, and volumes.
- **Cross-Platform Development**: WSL integration for bridging Windows and Linux environments.

### Data Intelligence & Analysis

- **Financial Analysis**: Access to market data, company research, and investment insights.
- **Knowledge Management**: Persistent, searchable knowledge bases with semantic capabilities.
- **Web Intelligence**: Advanced web scraping and content extraction for research and data gathering.
- **Database Interaction**: Query and manage SQLite databases, with plans for broader DB support.

### Workflow Orchestration & Productivity

- **Process Automation**: Generate and manage complex workflows using N8n integration.
- **Multi-System Integration**: Combine tools from various servers to create sophisticated automation chains.
- **Document Processing**: Convert and manage documents in various formats.

## 🛠️ Development Guidelines & Best Practices

Adherence to established MCP framework patterns is critical for server stability and compatibility.

### Core MCP Framework Pattern (Python Example)

```python
import asyncio
import sys
from mcp.common.text_content import TextContent
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Ensure logs go to stderr and are prefixed
logger = lambda message: print(f"[my-server-name] {message}", file=sys.stderr)

class MyServer(Server):
    async def tool_example_tool(self, params):
        logger(f"tool_example_tool called with: {params}")
        try:
            # ... your tool logic here ...
            result = f"Processed: {params.get('input_data', '')}"
            return TextContent(text=result)  # Always return TextContent
        except Exception as e:
            logger(f"Error in tool_example_tool: {e}")
            # Return a structured error if possible, or let framework handle
            raise

async def main():
    logger("Starting MyServer...")
    server = MyServer()
    async with stdio_server() as (read_stream, write_stream):
        logger("stdio_server streams obtained, running server loop.")
        await server.run(read_stream, write_stream)
    logger("MyServer finished.")

if __name__ == "__main__":
    # Keep stdin open for Windows batch file execution
    # if sys.platform == "win32":
    #     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
```

### Key Principles

- **Always use the `mcp.server.Server` framework**: Avoid manual JSON-RPC parsing to prevent validation errors (e.g., Zod errors).
- **Implement Asynchronous Patterns**: Utilize `async/await` and the `stdio_server()` context manager for non-blocking operations.
- **Standardized Responses**: Return `TextContent` objects with JSON-serialized text for tool calls.
- **Error Handling**: Implement comprehensive `try/catch` blocks. Log all errors and diagnostic information to `stderr`, prefixed with the server name (e.g., `[server-name]`). Stdout must be reserved for JSON-RPC messages only.
- **Dependency Management**: Maintain a `requirements.txt` for Python projects and ensure virtual environments are used.
- **Launch Scripts**: Use batch files or shell scripts for consistent server startup, including environment setup.
- **Configuration**: Store API keys and sensitive data securely (e.g., environment variables, or non-versioned config files) and not directly in versioned code. Reference placeholders in committed files.

For more detailed patterns and lessons learned, refer to `PROJECT_MEMORY_COMPREHENSIVE.md`.

## 💡 Integration with Claude 4

This MCP toolkit is designed to complement and extend Anthropic's Claude 4 capabilities:

- **Leveraging Native Features**: Where Claude 4 provides native code execution or file handling, MCP servers focus on specialized tasks, external API access, or local system interactions that go beyond these native functions.
- **Enhanced MCP Connector**: The servers are built to work with Claude's evolving MCP connector, aiming for improved stability and richer interactions.
- **Specialized Tools**: Provides a broader set of tools than available natively, enabling more complex and domain-specific automation.

## 📖 Examples & Use Cases

This project includes a variety of examples to demonstrate server capabilities and multi-server workflows:

- **Quick Server Tests**: Validate individual server functionality. See `examples/quick_server_tests.md`.
- **Comprehensive Workflows**: Explore complex use cases combining multiple servers for tasks like financial research, document intelligence, and competitive analysis. See `examples/comprehensive_mcp_examples.md`.

## 🗺️ Roadmap & Future Development

The following areas are priorities for future development:

1. **Database Analytics MCP**: Extend database capabilities beyond SQLite to include enterprise systems like PostgreSQL, MySQL, and MongoDB, offering advanced query optimization, schema analysis, and data visualization tools.
2. **Tool Context Bridge Development**: Design a mechanism to allow context and tool outputs to be seamlessly shared between different Claude instances or agents (e.g., Claude Desktop and Claude Code agents).
3. **Advanced Workflow Orchestration**: Enhance capabilities for defining, managing, and monitoring complex, multi-step, multi-agent workflows.
4. **Home Automation Hub MCP**: Develop a generic IoT hub for controlling smart home devices across various protocols (MQTT, Zigbee, Z-Wave).
5. **Cloud Infrastructure MCP**: Introduce capabilities for managing resources on major cloud platforms (AWS, Azure, GCP), including provisioning, monitoring, and cost management.

## 📚 Documentation & Support

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)**: Detailed overview of the current project status.
- **[SERVER_INVENTORY.md](SERVER_INVENTORY.md)**: A complete catalog of all MCP servers.
- **[examples/](examples/)**: Directory containing usage examples and test workflows.
- **[scripts/](scripts/)**: Utility scripts for testing, deployment, and validation.
- **Individual Server READMEs**: Located within each server's directory in `servers/` for specific details.
- **Claude Desktop Logs**: For troubleshooting, check `C:\Users\<Username>\AppData\Roaming\Claude\logs\`.

## 🔧 Troubleshooting

Common issues and initial troubleshooting steps:

1. **Server Transport Closed Unexpectedly**: Often due to not using the MCP framework correctly or synchronous code blocking. Review server implementation against the recommended patterns.
2. **Zod Validation Errors**: Typically indicates issues with JSON-RPC message formatting, often a symptom of manual JSON handling instead of using the MCP framework, or incorrect async/await patterns.
3. **Dependency Issues**: Ensure virtual environments are correctly set up and all packages in `requirements.txt` are installed.
4. **Configuration Errors**: Double-check paths, command arguments, and environment variables in `claude_desktop_config.json`.

For detailed troubleshooting, refer to individual server logs and the validation scripts in the `scripts/` directory.
