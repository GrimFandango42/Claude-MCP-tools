# MCP Server Development - Critical Success Patterns & Memory

## Windows Computer Use MCP Server Fix - Key Learning

### Problem Solved
**Zod validation errors preventing proper MCP server registration in Claude Desktop**

### Root Cause
- **Manual JSON-RPC Implementation**: Original server used custom stdin/stdout parsing
- **Schema Non-Compliance**: Tool definitions didn't match MCP framework standards
- **Missing Async Stream Handling**: No proper stdio_server() context management

### Solution That Worked
**Complete MCP Framework Integration**

#### Critical Success Pattern:
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

class CustomMCPServer:
    def __init__(self):
        self.server = Server("server-name")
        self._register_tools()
    
    def _register_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [Tool(name="...", description="...", inputSchema={...})]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            result = await self._handle_tool_logic(name, arguments)
            return [TextContent(type="text", text=json.dumps(result))]

async def main():
    server_instance = CustomMCPServer()
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(read_stream, write_stream,
                                        server_instance.server.create_initialization_options())
```

### Why This Pattern Works
1. **Automatic Protocol Compliance**: MCP framework handles JSON-RPC validation
2. **Proper Stream Management**: stdio_server() provides async stream handling
3. **Type Safety**: TextContent responses with proper serialization
4. **Error Handling**: Framework manages protocol-level errors
5. **Consistency**: Matches all successful servers in project

### Reusable Guidelines for All MCP Servers
1. ✅ **ALWAYS use MCP framework** - never manual JSON-RPC
2. ✅ **Use proper decorators** - @server.list_tools() and @server.call_tool()
3. ✅ **Implement async patterns** - await all operations
4. ✅ **Return TextContent** - with JSON serialization
5. ✅ **Use stdio_server() context** - for stream management
6. ✅ **Structured error handling** - with stderr logging

### Servers Successfully Using This Pattern
- ✅ Financial Datasets MCP
- ✅ Knowledge Memory MCP  
- ✅ Docker Orchestration MCP
- ✅ Windows Computer Use MCP (after fix)

### Anti-Patterns That Fail
- ❌ Manual stdin reading with `for line in sys.stdin:`
- ❌ Custom JSON-RPC message routing
- ❌ Direct stdout JSON responses without framework
- ❌ Missing async/await patterns
- ❌ Non-TextContent responses

**CRITICAL RULE**: Any deviation from the MCP framework pattern results in Zod validation errors and server failure.

## Next MCP Server Implementation Strategy
When building new MCP servers:
1. Start with MCP framework template
2. Define tools using proper schema validation
3. Implement async tool handlers
4. Test with validation framework
5. Follow established project patterns

This pattern ensures immediate success and prevents debugging sessions.
