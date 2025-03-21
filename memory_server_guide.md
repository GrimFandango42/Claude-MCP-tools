# Claude Desktop Memory MCP Server Guide

## Overview

The Memory MCP server allows Claude to store and retrieve information across sessions, creating a persistent memory system. This guide explains how to use our custom Memory MCP server implementation, which uses a SQLite database for reliable storage.

## Features

Our custom Memory MCP server provides the following capabilities:

1. **Create Memories**: Store important information with titles, content, and tags
2. **Retrieve Memories**: Access previously stored memories by ID
3. **Update Memories**: Modify existing memories
4. **Delete Memories**: Remove memories that are no longer needed
5. **Search Memories**: Find memories by text content or tags

## Setup

### Prerequisites

- Python 3.8 or higher
- Required Python packages (install using `pip install -r memory_server_requirements.txt`)
- Claude Desktop with MCP configuration

### Installation

1. Ensure the `memory_mcp_server.py` file is in your project directory
2. Update your Claude Desktop configuration (`claude_desktop_config.json`) to include the Memory MCP server:

```json
"memory": {
  "command": "python",
  "args": [
    "C:\\AI_Projects\\Claude MCP tools\\memory_mcp_server.py"
  ],
  "tools": [
    "memory_create",
    "memory_get",
    "memory_update",
    "memory_delete",
    "memory_search"
  ]
}
```

3. Start the Memory MCP server by running:

```
python memory_mcp_server.py
```

4. Restart Claude Desktop to apply the configuration changes

## Using the Memory MCP Server with Claude

### Creating Memories

To create a new memory, use a prompt like this:

```
Using your memory capabilities, please remember the following information about my project preferences:

1. My preferred programming language is Python
2. I like to use the FastAPI framework for backend development
3. For frontend, I prefer React with TypeScript

Please store this with the tags "preferences" and "development".
```

Claude will use the `memory_create` tool to store this information in the database.

### Retrieving Memories

To retrieve a specific memory by ID:

```
Using your memory capabilities, please retrieve the memory with ID 1.
```

Claude will use the `memory_get` tool to fetch the memory from the database.

### Searching Memories

To search for memories by content or tags:

```
Using your memory capabilities, please find all memories related to "Python" or tagged with "preferences".
```

Claude will use the `memory_search` tool to find matching memories in the database.

### Updating Memories

To update an existing memory:

```
Using your memory capabilities, please update memory ID 1 to reflect that I now prefer Django over FastAPI for backend development.
```

Claude will use the `memory_update` tool to modify the memory in the database.

### Deleting Memories

To delete a memory:

```
Using your memory capabilities, please delete memory ID 2 as it's no longer relevant.
```

Claude will use the `memory_delete` tool to remove the memory from the database.

## Best Practices

1. **Be Specific**: When asking Claude to remember information, be clear and specific
2. **Use Tags**: Tags make it easier to organize and retrieve related memories
3. **Regular Maintenance**: Periodically update or remove outdated memories
4. **Context Matters**: Provide enough context when asking Claude to recall information
5. **Verify Retrieval**: Ask Claude to confirm what it remembers to ensure accuracy

## Troubleshooting

### Common Issues

1. **Server Not Starting**: Ensure all dependencies are installed and the port (8093) is not in use
2. **Memory Not Found**: Verify you're using the correct memory ID
3. **Search Not Working**: Check that your search terms match the content or tags of your memories
4. **Claude Not Using Memory Tools**: Restart Claude Desktop and ensure the configuration is correct

### Logs

Check the `memory_mcp_server.log` file in your project directory for detailed logs that can help diagnose issues.

## Technical Details

### Database Schema

The Memory MCP server uses a SQLite database with the following tables:

1. **memories**: Stores the core memory data (ID, title, content, timestamps)
2. **tags**: Stores unique tags
3. **memory_tags**: Junction table linking memories to tags

### API Endpoints

The server exposes a WebSocket endpoint that implements the Model Context Protocol (MCP) for communication with Claude Desktop.

## Example Workflow

1. Start the Memory MCP server
2. Ask Claude to remember important project information
3. In a later session, ask Claude to recall that information
4. Update the information as your project evolves
5. Search for specific memories when needed

This persistent memory system makes Claude much more effective for long-term projects and ongoing conversations.
