#!/usr/bin/env python3
"""
Documentation improvement script for Claude MCP Tools.
Creates enterprise-grade documentation structure and templates.
"""

import os
from pathlib import Path
from datetime import datetime

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"

# Documentation structure
DOCS_STRUCTURE = {
    "getting-started": [
        "claude-desktop-setup.md",
        "claude-code-setup.md", 
        "hybrid-workflows.md",
        "quick-start.md",
    ],
    "architecture": [
        "mcp-protocol.md",
        "server-patterns.md",
        "security-model.md",
        "platform-comparison.md",
    ],
    "api-reference": [
        "README.md",  # Will be auto-generated
    ],
    "deployment": [
        "production-checklist.md",
        "monitoring.md",
        "scaling.md",
        "troubleshooting.md",
    ],
    "development": [
        "contributing.md",
        "testing.md",
        "release-process.md",
        "coding-standards.md",
    ],
    "servers": [
        "README.md",  # Index of all servers
    ]
}

# Template content for various documentation files
TEMPLATES = {
    "claude-desktop-setup.md": """# Claude Desktop Setup Guide

## Prerequisites

- Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- Python 3.11 or higher
- Claude Desktop application installed
- Administrator/sudo access for system integration

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/claude-mcp-tools.git
cd claude-mcp-tools
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install core dependencies
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

Locate your Claude Desktop configuration file:

- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add MCP server configurations:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "path/to/allowed/directory"],
      "description": "File system operations"
    },
    "github": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      },
      "description": "GitHub repository management"
    }
  }
}
```

### 4. Verify Installation

1. Restart Claude Desktop
2. Check MCP servers panel for connected servers
3. Test with: "List files in the current directory"

## Platform-Specific Servers

### Desktop-Only Servers
These require GUI access and won't work in Claude Code:

- **Windows Computer Use**: Desktop automation
- **Containerized Computer Use**: Isolated GUI automation
- **ScreenPilot**: Screen analysis
- **Playwright**: Browser automation

### Cross-Platform Servers
Work in both Claude Desktop and Claude Code:

- **Filesystem**: File operations
- **GitHub**: Repository management
- **SQLite**: Database operations
- All Code Intelligence servers

## Troubleshooting

### Server Not Connecting
1. Check logs at `%APPDATA%\\Claude\\logs`
2. Verify Python path in configuration
3. Ensure no firewall blocking

### Permission Errors
1. Run Claude Desktop as administrator (once)
2. Check file system permissions
3. Verify API tokens are valid

## Next Steps

- [Configure individual servers](../servers/README.md)
- [Learn about hybrid workflows](hybrid-workflows.md)
- [Security best practices](../architecture/security-model.md)
""",

    "claude-code-setup.md": """# Claude Code Setup Guide

## Overview

Claude Code is the CLI version of Claude, optimized for development tasks. This guide covers setting up MCP servers compatible with Claude Code's text-based interface.

## Compatible Servers

### Core Development
- **Filesystem MCP**: File operations
- **GitHub MCP**: Repository management  
- **SQLite MCP**: Database queries

### Code Intelligence
- **Code Analysis MCP**: AST parsing, symbol resolution
- **Code Quality MCP**: Linting, formatting
- **Refactoring MCP**: Safe code transformations
- **Test Intelligence MCP**: Test generation, coverage
- **Dependency Analysis MCP**: Security scanning

### API Services
- **AgenticSeek MCP**: Multi-provider AI routing
- **API Gateway MCP**: API management
- **Financial Datasets MCP**: Market data
- **Firecrawl MCP**: Web scraping

## Installation

### 1. Install Claude Code CLI

```bash
# Install via npm (recommended)
npm install -g @anthropic-ai/claude-code

# Or via pip
pip install claude-code-cli
```

### 2. Configure MCP Servers

Create `~/.claude-code/config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "transport": "stdio"
    },
    "code-analysis": {
      "command": "python",
      "args": ["/path/to/servers/code-analysis-mcp/server.py"],
      "transport": "stdio"
    }
  }
}
```

### 3. Verify Setup

```bash
claude-code --list-servers
```

## Usage Examples

### File Operations
```
claude-code "Read the README.md file and summarize its contents"
```

### Code Analysis
```
claude-code "Analyze the complexity of functions in src/main.py"
```

### Multi-Server Workflow
```
claude-code "Analyze dependencies in package.json and check for security vulnerabilities"
```

## Performance Optimization

### 1. Use Local Servers
Prefer stdio-based servers over network protocols for lower latency.

### 2. Cache Results
Enable caching for expensive operations:

```json
{
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}
```

### 3. Batch Operations
Combine multiple operations in single requests when possible.

## Limitations

Claude Code cannot use:
- GUI automation servers (Windows Computer Use, etc.)
- Browser-based servers (Playwright, Vibetest)  
- Visual output servers (Screenshot tools)

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Code Analysis
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Claude Code Analysis
        run: |
          claude-code "Analyze code quality and generate report" > analysis.md
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: code-analysis
          path: analysis.md
```

## Next Steps

- [API Reference](../api-reference/README.md)
- [Hybrid Workflows with Claude Desktop](hybrid-workflows.md)
- [Developing Custom MCP Servers](../development/contributing.md)
""",

    "mcp-protocol.md": """# MCP Protocol Architecture

## Overview

The Model Context Protocol (MCP) enables structured communication between AI models and external tools through a standardized JSON-RPC interface.

## Protocol Layers

### 1. Transport Layer
- **stdio**: Default for local servers (stdin/stdout)
- **HTTP**: For network-based servers
- **WebSocket**: For bidirectional streaming

### 2. Message Layer
JSON-RPC 2.0 messages with MCP extensions:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "path": "/path/to/file.txt"
    }
  },
  "id": 1
}
```

### 3. Protocol Methods

#### Lifecycle
- `initialize`: Establish connection and capabilities
- `initialized`: Confirm initialization
- `shutdown`: Graceful termination

#### Discovery
- `tools/list`: Available tools
- `resources/list`: Available resources
- `prompts/list`: Available prompts

#### Execution
- `tools/call`: Execute a tool
- `resources/read`: Read a resource
- `prompts/get`: Get a prompt template

## Server Implementation Pattern

### Using FastMCP (Recommended)

```python
from fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
async def read_file(path: str) -> str:
    \"\"\"Read contents of a file.\"\"\"
    with open(path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Manual Implementation

```python
import json
import sys

class MCPServer:
    def __init__(self):
        self.tools = {}
    
    def handle_message(self, message):
        method = message.get("method")
        if method == "tools/list":
            return self.list_tools()
        elif method == "tools/call":
            return self.call_tool(message["params"])
    
    def run(self):
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            message = json.loads(line)
            response = self.handle_message(message)
            
            sys.stdout.write(json.dumps(response) + "\\n")
            sys.stdout.flush()
```

## Best Practices

### 1. Error Handling
Always return structured errors:

```python
{
    "error": {
        "code": -32603,
        "message": "Internal error",
        "data": {
            "details": "File not found"
        }
    }
}
```

### 2. Logging
- **Never log to stdout** (reserved for JSON-RPC)
- Use stderr or file-based logging
- Structured logging recommended

### 3. Tool Design
- Clear, descriptive names
- Comprehensive docstrings
- Type hints for parameters
- Predictable return types

### 4. Security
- Validate all inputs
- Sandbox file operations
- Rate limit API calls
- Authenticate when necessary

## Protocol Extensions

### Custom Capabilities
Servers can declare custom capabilities during initialization:

```json
{
  "capabilities": {
    "tools": true,
    "resources": true,
    "custom": {
      "streaming": true,
      "batch_operations": true
    }
  }
}
```

### Streaming Responses
For long-running operations:

```json
{
  "jsonrpc": "2.0",
  "method": "$/progress",
  "params": {
    "token": "operation-123",
    "value": {
      "kind": "report",
      "percentage": 50,
      "message": "Processing..."
    }
  }
}
```

## Testing

### Unit Testing
```python
import pytest
from my_mcp_server import MyServer

@pytest.mark.asyncio
async def test_read_file():
    server = MyServer()
    result = await server.read_file("test.txt")
    assert result == "expected content"
```

### Integration Testing
Test with actual Claude Desktop/Code connection:

```bash
# Start server in test mode
python server.py --test

# In another terminal
mcp-test-client --server stdio --command "python server.py"
```

## Performance Considerations

### 1. Response Time
- Target <100ms for simple operations
- Use async/await for I/O operations
- Implement caching where appropriate

### 2. Memory Usage
- Stream large files instead of loading
- Clean up resources after use
- Monitor memory in long-running servers

### 3. Concurrency
- Handle multiple requests concurrently
- Use connection pooling for databases
- Implement proper rate limiting

## Debugging

### 1. Enable Debug Logging
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='mcp_debug.log'
)
```

### 2. Protocol Inspection
```bash
# Capture protocol messages
MCP_LOG_LEVEL=debug claude-desktop 2>protocol.log
```

### 3. Common Issues
- **No response**: Check stdout isn't polluted
- **Parse errors**: Validate JSON formatting
- **Tool not found**: Verify tool registration

## References

- [MCP Specification](https://github.com/anthropics/mcp)
- [FastMCP Documentation](https://github.com/anthropics/fastmcp)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
""",

    "production-checklist.md": """# Production Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All tests passing (`pytest`, `npm test`)
- [ ] Code coverage >80%
- [ ] No security vulnerabilities (`pip-audit`, `npm audit`)
- [ ] Linting passed (`flake8`, `black`, `eslint`)
- [ ] Type checking passed (`mypy`)

### Documentation
- [ ] API documentation complete
- [ ] README updated with latest changes
- [ ] CHANGELOG.md updated
- [ ] Configuration examples provided
- [ ] Troubleshooting guide updated

### Security
- [ ] API keys in environment variables
- [ ] File access properly sandboxed
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Authentication enabled where needed

## Deployment

### Environment Setup
- [ ] Python version specified (>=3.11)
- [ ] Virtual environment configured
- [ ] Dependencies pinned (`requirements.txt`)
- [ ] Environment variables documented

### MCP Server Configuration
- [ ] Server registered in claude_desktop_config.json
- [ ] Proper working directory set
- [ ] Error handling configured
- [ ] Logging to appropriate location
- [ ] Resource limits defined

### Testing
- [ ] Integration tests with Claude Desktop
- [ ] Load testing completed
- [ ] Error scenarios tested
- [ ] Rollback plan prepared

## Post-Deployment

### Monitoring
- [ ] Logging aggregation setup
- [ ] Error tracking enabled
- [ ] Performance metrics collected
- [ ] Alerts configured

### Maintenance
- [ ] Backup procedures documented
- [ ] Update process defined
- [ ] Support contacts listed
- [ ] Known issues tracked

## Server-Specific Checklists

### API-Based Servers
- [ ] API key rotation schedule
- [ ] Rate limit handling
- [ ] Retry logic implemented
- [ ] Circuit breaker pattern

### File System Servers
- [ ] Allowed paths configured
- [ ] Permission checks
- [ ] Path traversal prevention
- [ ] Disk space monitoring

### Container-Based Servers
- [ ] Docker images optimized
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Volume persistence

## Performance Benchmarks

### Target Metrics
- Response time: <100ms (simple), <1s (complex)
- Memory usage: <500MB per server
- CPU usage: <10% idle, <50% active
- Error rate: <0.1%

### Load Testing
```bash
# Example load test
mcp-bench --server filesystem --concurrent 10 --requests 1000
```

## Rollback Procedures

### Quick Rollback
1. Stop affected MCP server
2. Restore previous configuration
3. Restart Claude Desktop
4. Verify functionality

### Full Rollback
1. Document issue
2. Restore from backup
3. Revert code changes
4. Update configuration
5. Test thoroughly
6. Communicate to users

## Sign-Off

- [ ] Development Team Lead
- [ ] Security Review
- [ ] Operations Team
- [ ] Product Owner

**Deployment Date**: ________________
**Deployed By**: ____________________
**Version**: ________________________
"""
}

def create_documentation_structure():
    """Create the documentation directory structure."""
    for category, files in DOCS_STRUCTURE.items():
        category_path = DOCS_ROOT / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        for filename in files:
            file_path = category_path / filename
            
            # Skip if file exists (don't overwrite)
            if file_path.exists():
                print(f"Skipping existing file: {file_path.relative_to(PROJECT_ROOT)}")
                continue
            
            # Create file with template content if available
            template_key = filename
            if category != "getting-started":
                template_key = filename  # Could add more templates
            
            content = TEMPLATES.get(template_key, f"# {filename.replace('.md', '').replace('-', ' ').title()}\n\n*Coming soon...*\n")
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"Created: {file_path.relative_to(PROJECT_ROOT)}")

def create_main_docs_readme():
    """Create the main documentation README."""
    readme_content = """# Claude MCP Tools Documentation

## Quick Links

### Getting Started
- [Claude Desktop Setup](getting-started/claude-desktop-setup.md)
- [Claude Code Setup](getting-started/claude-code-setup.md)
- [Quick Start Guide](getting-started/quick-start.md)

### Architecture
- [MCP Protocol Overview](architecture/mcp-protocol.md)
- [Server Implementation Patterns](architecture/server-patterns.md)
- [Security Model](architecture/security-model.md)

### Deployment
- [Production Checklist](deployment/production-checklist.md)
- [Monitoring Guide](deployment/monitoring.md)
- [Troubleshooting](deployment/troubleshooting.md)

### Development
- [Contributing Guidelines](development/contributing.md)
- [Testing Guide](development/testing.md)
- [Coding Standards](development/coding-standards.md)

## Documentation Standards

All documentation follows these principles:

1. **Clarity**: Technical accuracy without jargon
2. **Completeness**: Every feature documented
3. **Examples**: Working code for every concept
4. **Maintenance**: Regular updates with version changes

## Contributing to Documentation

See [Contributing Guidelines](development/contributing.md) for documentation standards and process.
"""
    
    readme_path = DOCS_ROOT / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"Created: {readme_path.relative_to(PROJECT_ROOT)}")

def create_gitignore_additions():
    """Create .gitignore additions for cleanup."""
    gitignore_additions = """
# Redundant files and logs
*.log
*_backup.json
*.bak

# Test artifacts
.coverage
htmlcov/
.pytest_cache/
*.pyc
__pycache__/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Archives
archive/cleanup_*/

# Temporary files
temp/
tmp/
*.tmp
"""
    
    gitignore_path = PROJECT_ROOT / ".gitignore"
    
    # Read existing content
    existing_content = ""
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
    
    # Check if additions already exist
    if "# Redundant files and logs" not in existing_content:
        with open(gitignore_path, 'a') as f:
            f.write("\\n" + gitignore_additions)
        print(f"Updated: {gitignore_path.relative_to(PROJECT_ROOT)}")
    else:
        print(f"Skipping .gitignore update (already contains additions)")

def main():
    """Main function to improve documentation."""
    print("Claude MCP Tools - Documentation Improvement")
    print("==========================================\\n")
    
    print("Creating documentation structure...")
    create_documentation_structure()
    
    print("\\nCreating main documentation README...")
    create_main_docs_readme()
    
    print("\\nUpdating .gitignore...")
    create_gitignore_additions()
    
    print("\\n✅ Documentation structure created successfully!")
    print("\\nNext steps:")
    print("1. Review and customize the template documentation")
    print("2. Run the cleanup script to archive redundant files")
    print("3. Generate API documentation from code")
    print("4. Add architecture diagrams and flowcharts")

if __name__ == "__main__":
    main()