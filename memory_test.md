# Testing the Memory MCP Server

This document provides examples of how to use the Memory MCP server with Claude Desktop.

## What is the Memory MCP Server?

The Memory MCP server allows Claude to store and retrieve information across sessions. This means Claude can remember important details about your projects, preferences, and previous interactions even after you close and reopen Claude Desktop.

## Example Prompts

Here are some example prompts you can use to test the Memory MCP server:

### Storing Information

```
Using your memory capabilities, please remember the following information about my project preferences:

1. My preferred programming language is Python
2. I like to use the FastAPI framework for backend development
3. For frontend, I prefer React with TypeScript
4. My favorite code editor is Visual Studio Code
5. I prefer to use pytest for testing

Please confirm that you've stored this information and will remember it for future sessions.
```

### Retrieving Information

```
Using your memory capabilities, please recall what you know about my project preferences, particularly my preferred programming language and frameworks.
```

### Updating Information

```
Using your memory capabilities, please update your records to reflect that I now prefer Django over FastAPI for backend development. Please confirm the update and show me all my current preferences.
```

### Organizing Information with Tags

```
Using your memory capabilities, please store the following information about my current project:

Project Name: Claude MCP Tools
Description: A collection of tools and servers for enhancing Claude Desktop with Model Context Protocol capabilities
Main Technologies: Python, JavaScript, Node.js
Key Features: File operations, browser automation, sequential thinking, memory persistence

Please tag this information with "project_info", "mcp_tools", and "claude_desktop" for easy retrieval later.
```

### Retrieving Tagged Information

```
Using your memory capabilities, please retrieve all information tagged with "project_info".
```

## Benefits of Using Memory

1. **Persistence**: Information is stored across sessions
2. **Context Awareness**: Claude can maintain context about your projects and preferences
3. **Efficiency**: Reduces the need to repeat information in every conversation
4. **Organization**: Information can be tagged and categorized for easy retrieval
5. **Personalization**: Claude can adapt to your specific needs and preferences over time

## Best Practices

1. Be explicit when asking Claude to remember information
2. Use tags to organize related information
3. Periodically review and update stored information
4. Be specific when retrieving information
5. Use memory for important, long-term information rather than transient details
