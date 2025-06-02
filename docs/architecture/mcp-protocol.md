# MCP Protocol Architecture

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
    """Read contents of a file."""
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
            
            sys.stdout.write(json.dumps(response) + "\n")
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
