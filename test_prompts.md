# MCP Skills Test Prompts

These prompts are designed to test various MCP capabilities in Claude desktop, both individually and in combination.

## Individual Skill Tests

### Filesystem MCP

1. **Basic File Reading**
   ```
   Using your filesystem MCP capabilities, please read the README.md file from C:\AI_Projects\Claude-MCP-tools\ and summarize what this project is about.
   ```

2. **Directory Structure Analysis**
   ```
   Using your filesystem MCP access, scan the C:\AI_Projects\Claude-MCP-tools directory and list all Python files (.py extension) you find. Group them by their apparent functionality (MCP servers, utilities, etc.) based on their filenames and locations.
   ```

3. **File Comparison**
   ```
   I have two MCP server implementations in my project. Using your filesystem access, please read both C:\AI_Projects\Claude-MCP-tools\memory_mcp_server.py and C:\AI_Projects\Claude-MCP-tools\git_mcp_server.py, then compare their approaches to handling WebSocket connections and JSON-RPC messages.
   ```

### Memory MCP

1. **Memory Creation and Retrieval**
   ```
   Create a memory with the title "Claude-MCP-tools Project Structure" containing this information: "The project contains several custom MCP server implementations including memory_mcp_server.py (SQLite-based memory storage), git_mcp_server.py (Git operations), and basic_mcp_server.py (screenshot capabilities)." Then, retrieve and summarize this memory.
   ```

2. **Memory with Tags**
   ```
   Create a memory titled "MCP Architecture Patterns" with the tags "architecture" and "mcp" containing this text: "MCP servers follow a standard pattern with initialize method handling, tools/list for capability discovery, and tools/call for execution. All use JSON-RPC message format over WebSockets or stdio." Later, I'll ask you to find memories with the "architecture" tag.
   ```

3. **Memory Update Test**
   ```
   Create a memory titled "MCP Testing Plan" containing: "Step 1: Test filesystem access to project files. Step 2: Test memory creation and retrieval." Then update it to add: "Step 3: Test sequential thinking for multi-step reasoning. Step 4: Test Puppeteer for web automation."
   ```

### Sequential Thinking MCP

1. **Multi-step Problem Solving**
   ```
   I want to implement a new MCP server for Windows system commands in my C:\AI_Projects\Claude-MCP-tools project. Using your sequential thinking capabilities, break down this task into logical steps, including: 1) JSON-RPC message handling setup, 2) Windows command execution function creation, 3) Tool schema definition, 4) Error handling implementation, and 5) Security considerations.
   ```

2. **Algorithm Implementation**
   ```
   I need to implement a data processing algorithm in my MCP server. I have event logs from user interactions that need to be sorted and filtered. Using sequential thinking, walk through implementing a solution that: 1) Parses log entries, 2) Filters by relevance, 3) Sorts by timestamp, and 4) Generates analytical insights.
   ```

3. **Troubleshooting Sequence**
   ```
   One of my custom MCP servers (C:\AI_Projects\Claude-MCP-tools\memory_mcp_server.py) keeps disconnecting after running for a few minutes. Using sequential thinking, create a systematic troubleshooting plan that investigates: 1) WebSocket connection stability, 2) SQLite database locking issues, 3) Memory consumption patterns, 4) Error handling robustness, and 5) Client timeout settings.
   ```

### Puppeteer MCP

1. **Web Interaction**
   ```
   Use your Puppeteer MCP capability to navigate to https://github.com/punkpeye/awesome-mcp-servers and summarize the types of MCP server implementations listed there. This will help me understand what kinds of servers I could integrate into my project.
   ```

2. **Form Automation Example**
   ```
   I want to automate testing of web forms in my MCP project. Using your Puppeteer capabilities, show me example code for automating a login form that: 1) Navigates to a page, 2) Fills in username and password fields, 3) Submits the form, and 4) Validates successful login.
   ```

3. **Documentation Extraction**
   ```
   Use your Puppeteer capabilities to visit https://github.com/modelcontextprotocol/mcp and extract the core architectural concepts from the README. Specifically, find information about the JSON-RPC protocol format and standard message types used in MCP.
   ```

## Combined Skill Prompts

1. **Filesystem + Memory**
   ```
   Using your filesystem MCP access, read the file at C:\AI_Projects\Claude-MCP-tools\memory_mcp_server.py. Then create a detailed memory titled "Memory MCP Server API" containing a list of the specific API endpoints and their functionality. Include tags "api" and "memory_server".
   ```

2. **Sequential Thinking + Memory**
   ```
   I want to implement a websocket-based MCP server similar to the ones in my C:\AI_Projects\Claude-MCP-tools project. Using sequential thinking, create a detailed implementation plan with at least 8 distinct steps. Then store this plan as a memory titled "WebSocket MCP Server Implementation" with the tag "implementation_plan".
   ```

3. **Filesystem + Puppeteer**
   ```
   I'd like to combine filesystem and puppeteer capabilities for my MCP project:

   1. First, use filesystem access to list all Python files in C:\AI_Projects\Claude-MCP-tools that contain "server" in their name
   2. Choose one of these server files and read its imports to determine what dependencies it uses
   3. Then use Puppeteer to search for documentation for these dependencies on PyPI (Python Package Index) or GitHub
   4. Summarize what you found about each major dependency, focusing on how they contribute to MCP server functionality

   This will help me understand the external libraries my MCP servers depend on and how they're being used.
   ```

4. **Full Integration Test**
   ```
   Let's test a full workflow combining multiple MCP skills:
   1. Use filesystem access to analyze the structure of C:\AI_Projects\Claude-MCP-tools, focusing on the MCP server implementations
   2. Use sequential thinking to outline how these servers could be integrated into a unified framework
   3. Store this integration plan as a memory titled "Unified MCP Framework" with tags "architecture" and "integration"
   4. Use Puppeteer to search GitHub for similar integration approaches we could learn from

   Work through each step in order, showing your process.
   ```

   Using Firecrawl, research best practices for implementing FastAPI with Model Context Protocol (MCP) servers from multiple sources. Specifically:

1. Search for and analyze at least 3 different implementations of FastAPI-based MCP servers on GitHub, paying special attention to:
   - Connection management and timeout handling
   - Error recovery mechanisms
   - Process lifecycle management
   - Keep-alive implementations

2. Visit the official MCP documentation at modelcontextprotocol.io and identify recommended patterns for handling timeouts and maintaining persistent connections.

3. Find examples of production-grade MCP servers that implement custom timeout configurations.

After gathering this information, evaluate my current MCP implementation at C:\AI_Projects\Claude-MCP-tools, focusing specifically on:
- How our Firecrawl implementation compares to best practices
- Potential improvements for connection stability
- Better timeout and retry mechanisms we could implement
- Any architectural patterns we should adopt from successful projects

Create a detailed analysis that compares our implementation against the best practices you've found, with specific recommendations for improvements. Pay special attention to the timeout handling in our configuration files.

Save your findings to memory with a comprehensive summary of best practices and specific improvement recommendations for future reference.

#firecrawl
Can you use firecraw ll(please specically use firecrawl) to scrape everything you can to around details of any specific MCP servers called out on these sites:
https://modelcontextprotocol.io/examples
https://github.com/modelcontextprotocol/servers?tab=readme-ov-file
https://github.com/punkpeye/awesome-mcp-servers

Please use firecrawl to do that.

Once you do that please - make a plan for which MCP skills to implement over the next few days  for my C:\\AI\Projects\\Claude-MCP-Tools to help build up the general purpose bot skills over time and save that to your memory.