# Claude MCP Tools

A comprehensive collection of tools and servers for extending Claude's capabilities through the Model Context Protocol (MCP), enabling desktop automation, file system access, browser control, and more.

<p align="center">
  <img src="ClaudeDesktopAgent/screenshots/claude_mcp_tools_banner.png" alt="Claude MCP Tools Banner" width="800" />
</p>

## 🚀 Overview

This project provides a set of tools that extend Claude's capabilities using the Model Context Protocol (MCP), allowing Claude to interact with your computer in various ways. The tools are designed to work with Claude Desktop and provide functionalities such as:

- Taking screenshots and analyzing them
- Accessing and manipulating the file system
- Controlling web browsers through Puppeteer
- Executing system commands
- Automating desktop actions
- Sequential thinking for complex problem-solving
- Persistent memory across conversations
- Git repository management
- Database operations through SQLite
- And more

## 📂 Project Structure

The project consists of three main components:

### 1. ClaudeDesktopAgent

A framework for extending Claude's capabilities on desktop by providing access to custom tooling and automation features. It includes various MCP server implementations for different purposes.

Key files:
- `basic_mcp_server.py`: Simple implementation of the MCP protocol
- `simple_mcp_server.py`: Screenshot server for desktop analysis
- `http_mcp_server.py`: HTTP-based MCP server
- `ws_mcp_server.py`: WebSocket-based MCP server
- `cmd_mcp_server.py`: Command execution server
- `run_mcp_server.py`: Script to run and manage MCP servers

### 2. ClaudeDesktopBridge

A bridge that connects Claude Desktop to various computer control functionalities through a REST API, enabling advanced automation and system integration.

Key features:
- Docker containerization for easy deployment
- REST API for computer control
- Web automation capabilities
- Cross-platform support
- Streamlit-based UI for management

### 3. Anthropic Quickstarts

A collection of example projects and demos showcasing the capabilities of Claude with MCP:
- Computer Use Demo: Shows how Claude can interact with your computer
- Customer Support Agent: Example of Claude as a customer support agent with access to systems
- Financial Data Analyst: Demo of Claude analyzing financial data using MCP tools

## 🔧 MCP Servers

The project includes various MCP (Model Context Protocol) servers that provide different capabilities to Claude:

| Server | Function | Default Port | Implementation |
|--------|----------|--------------|----------------|
| Screenshot Server | Captures desktop screenshots | 8090 | Python (PyAutoGUI) |
| Filesystem Server | File system operations | 8080 | NPM Package |
| Puppeteer Server | Web automation | 8081 | NPM Package |
| Memory Server | Persistent memory | 8082 | NPM Package |
| Git Server | Git repository operations | 8083 | NPM Package |
| SQLite Server | Database operations | 8084 | NPM Package |
| Sequential Thinking Server | Step-by-step reasoning | 8085 | NPM Package |

Each server implements the Model Context Protocol and provides specific tools that Claude can use to interact with your computer or perform specific tasks.

## 📋 Getting Started

### Prerequisites

- Python 3.9+
- Node.js and npm
- Claude Desktop app
- Git (for version control)
- Administrator privileges (for some operations)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/claude-mcp-tools.git
   cd claude-mcp-tools
   ```

2. **Install Python dependencies for ClaudeDesktopAgent:**
   ```bash
   cd ClaudeDesktopAgent
   pip install -r requirements.txt
   cd ..
   ```

3. **Install Python dependencies for ClaudeDesktopBridge:**
   ```bash
   cd ClaudeDesktopBridge
   pip install -r requirements.txt
   cd ..
   ```

4. **Install MCP server packages globally:**
   ```bash
   install-mcp-servers.bat
   ```
   This will install all required NPM packages for the MCP servers.

### Environment Setup

1. **ClaudeDesktopAgent Environment:**
   - Copy `.env.example` to `.env` in the ClaudeDesktopAgent directory
   - Update the configuration values as needed

2. **ClaudeDesktopBridge Environment:**
   - Copy `.env.example` to `.env` in the ClaudeDesktopBridge directory
   - Modify the settings according to your environment

## ⚙️ Setting Up MCP Servers

The MCP servers need to be running for Claude to access their capabilities. You can run them individually or set them up to start automatically.

### Running Individual MCP Servers

#### Python-based Servers

1. **Screenshot Server:**
   ```bash
   cd ClaudeDesktopAgent
   python simple_mcp_server.py
   ```
   This server will start on port 8090 by default.

2. **HTTP MCP Server:**
   ```bash
   cd ClaudeDesktopAgent
   python http_mcp_server.py
   ```
   This server implements HTTP-based communication for the MCP protocol.

3. **WebSocket MCP Server:**
   ```bash
   cd ClaudeDesktopAgent
   python ws_mcp_server.py
   ```
   This server implements WebSocket-based communication for the MCP protocol.

#### NPM Package Servers

Once you've installed the MCP server packages globally, you can run them with the following commands:

1. **Filesystem Server:**
   ```bash
   npx @modelcontextprotocol/server-filesystem
   ```
   This server starts on port 8080 by default and provides file system operations.

2. **Puppeteer Server:**
   ```bash
   npx @modelcontextprotocol/server-puppeteer
   ```
   This server starts on port 8081 by default and provides web automation capabilities.

3. **Memory Server:**
   ```bash
   npx @modelcontextprotocol/server-memory
   ```
   This server starts on port 8082 by default and provides persistent memory capabilities.

4. **Git Server:**
   ```bash
   npx @modelcontextprotocol/server-git
   ```
   This server starts on port 8083 by default and provides Git repository operations.

5. **SQLite Server:**
   ```bash
   npx @modelcontextprotocol/server-sqlite
   ```
   This server starts on port 8084 by default and provides database operations.

6. **Sequential Thinking Server:**
   ```bash
   npx @modelcontextprotocol/server-sequential-thinking
   ```
   This server starts on port 8085 by default and provides step-by-step reasoning capabilities.

### Running the ClaudeDesktopBridge

#### Standard Method

```bash
cd ClaudeDesktopBridge
python run_ui.py
```

This will start the bridge with a Streamlit UI for management.

#### Docker Method

```bash
cd ClaudeDesktopBridge
docker-compose up -d
```

This will start the bridge in a Docker container.

### Configuring Claude Desktop

To use these MCP servers with Claude Desktop:

1. Open Claude Desktop
2. Go to Settings
3. Navigate to "Advanced" or "Developer" settings
4. Add the MCP server URLs:
   - Filesystem: `ws://localhost:8080`
   - Puppeteer: `ws://localhost:8081`
   - Memory: `ws://localhost:8082`
   - Git: `ws://localhost:8083`
   - SQLite: `ws://localhost:8084`
   - Sequential Thinking: `ws://localhost:8085`
   - Screenshot: `ws://localhost:8090`

## 📋 Example Usage Scenarios

### 1. Taking and Analyzing Screenshots

Claude can capture screenshots of your desktop and analyze them:

```
Can you take a screenshot of my desktop and tell me what you see?
```

Claude will use the Screenshot Server to capture your desktop and analyze the content, providing a detailed description of what it sees.

### 2. File System Operations

Claude can help you work with files and directories:

```
Can you list all Python files in my current directory and show me their content?
```

Claude will use the Filesystem Server to:
1. List all files in the current directory
2. Filter for Python files (.py extension)
3. Read and display the content of each Python file

### 3. Web Automation

Claude can browse the web and extract information:

```
Can you navigate to wikipedia.org, search for "artificial intelligence" and summarize the first paragraph?
```

Claude will use the Puppeteer Server to:
1. Open a new browser instance
2. Navigate to wikipedia.org
3. Search for "artificial intelligence"
4. Extract and summarize the first paragraph of the article

### 4. Sequential Thinking

Claude can break down complex problems into steps and solve them methodically:

```
Using sequential thinking, can you help me diagnose why my application keeps crashing?
```

Claude will use the Sequential Thinking Server to:
1. Break down the problem into logical steps
2. Consider possible causes of the crash
3. Suggest diagnostic steps to identify the issue
4. Provide potential solutions based on the findings

### 5. Git Repository Management

Claude can help you manage Git repositories:

```
Can you help me create a new Git repository for my project, add all files, and push it to GitHub?
```

Claude will use the Git Server to:
1. Initialize a new Git repository
2. Add all files to the repository
3. Create an initial commit
4. Guide you through connecting to GitHub
5. Push the repository to GitHub

### 6. Database Operations

Claude can help you work with SQLite databases:

```
Can you create a new database for my contacts, add a table for names and phone numbers, and insert some sample data?
```

Claude will use the SQLite Server to:
1. Create a new SQLite database
2. Define a schema for contacts
3. Create tables for storing contact information
4. Insert sample data
5. Execute queries to verify the data

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. MCP Server Connection Failed

**Symptoms:**
- Claude reports it cannot connect to the MCP server
- "Tool Not Available" error in Claude
- Server refuses connection

**Solutions:**
- Ensure the server is running (check process list)
- Verify the correct port is being used (check configuration)
- Check for port conflicts (use `netstat -ano` to see all open ports)
- Verify firewall settings are not blocking the connection
- Restart the server with administrator privileges

#### 2. Permission Errors

**Symptoms:**
- Operations fail with "Access Denied" errors
- File operations cannot complete
- Screenshots cannot be taken

**Solutions:**
- Run the command prompt or terminal as administrator
- Check file and directory permissions
- Ensure the user running the server has necessary permissions
- Add explicit permissions for the required directories

#### 3. Tool Not Found Error

**Symptoms:**
- Claude reports "Tool not found" when trying to use a specific capability
- Function calls fail with missing tool errors

**Solutions:**
- Make sure the tool is registered and the server is properly configured
- Check that the server URL is correctly entered in Claude Desktop settings
- Verify the tool implementation in the server code
- Restart the server and Claude Desktop

#### 4. Node.js Package Errors

**Symptoms:**
- NPM servers fail to start
- Package not found errors
- Version compatibility issues

**Solutions:**
- Reinstall the packages with `npm install -g @modelcontextprotocol/server-name`
- Check Node.js version (v14+ recommended)
- Clear NPM cache with `npm cache clean --force`
- Check for version compatibility issues in the package.json files

#### 5. Python Environment Issues

**Symptoms:**
- Import errors when running Python servers
- Missing module errors
- Version conflicts

**Solutions:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Create a new virtual environment: `python -m venv .venv`
- Activate the virtual environment before running servers
- Check Python version (3.9+ recommended)

### Log Files and Debugging

Check the following log files for more information:

- ClaudeDesktopAgent: `ClaudeDesktopAgent/logs/mcp_server.log`
- Screenshot Server: `ClaudeDesktopAgent/screenshot_server.log`
- Calculator Server: `ClaudeDesktopAgent/calculator_server.log`

Enable debug logging by setting the `DEBUG` environment variable to `true` in the `.env` file.

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute to the project:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `cd ClaudeDesktopAgent && pytest`
5. Commit your changes: `git commit -m 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Anthropic](https://www.anthropic.com/) for Claude and the MCP protocol
- [Model Context Protocol](https://github.com/modelcontextprotocol) for the MCP server implementations
- All contributors who have helped improve this project

## 📚 Further Reading

- [Claude Documentation](https://docs.anthropic.com/)
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/mcp)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
