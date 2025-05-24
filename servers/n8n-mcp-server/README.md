# N8n MCP Server

A Model Context Protocol (MCP) server that provides N8n workflow generation and management capabilities for Claude Desktop. This server enables Claude to create, validate, and export N8n workflows from natural language descriptions.

## Features

- **Workflow Generation**: Create N8n workflows from natural language descriptions
- **Template System**: Use predefined workflow templates for common automation patterns
- **Node Management**: Support for common N8n node types (HTTP Request, Code, Set, IF, etc.)
- **Workflow Validation**: Validate N8n workflow JSON structure
- **Export Ready**: Generate workflows ready for N8n import
- **Custom Workflows**: Create complex workflows with custom node configurations and connections

## Supported Node Types

- **Manual Trigger**: Manual workflow execution
- **Schedule Trigger**: Time-based workflow execution
- **Webhook**: HTTP webhook triggers
- **HTTP Request**: External API calls
- **Code**: Custom JavaScript execution
- **Set**: Data transformation and variable assignment
- **IF**: Conditional logic
- **Gmail**: Email operations
- **Slack**: Slack messaging
- **Google Sheets**: Spreadsheet operations

## Workflow Templates

### Basic HTTP Processing
Simple workflow that fetches data via HTTP and processes it:
- Manual Trigger → HTTP Request → Code → Set

### Scheduled Data Sync
Workflow that runs on a schedule to sync data between systems:
- Schedule Trigger → HTTP Request → IF → Google Sheets

### Webhook Notification
Receive webhook data and send notifications via Slack/Gmail:
- Webhook → Code → IF → Slack/Gmail

## Installation

1. **Install Dependencies**
   ```bash
   cd servers/n8n-mcp-server
   npm install
   ```

2. **Test the Server**
   ```bash
   npm start
   ```

3. **Add to Claude Desktop Configuration**

   Edit your `claude_desktop_config.json` file and add:

   ```json
   {
     "mcpServers": {
       "n8n-workflow-generator": {
         "command": "node",
         "args": [
           "C:\\AI_Projects\\Claude-MCP-tools\\servers\\n8n-mcp-server\\server.js"
         ],
         "keepAlive": true,
         "stderrToConsole": true
       }
     }
   }
   ```

   Alternative batch file approach:
   ```json
   {
     "mcpServers": {
       "n8n-workflow-generator": {
         "command": "cmd",
         "args": [
           "/c",
           "cd /d C:\\AI_Projects\\Claude-MCP-tools\\servers\\n8n-mcp-server && node server.js"
         ],
         "keepAlive": true,
         "stderrToConsole": true
       }
     }
   }
   ```

4. **Restart Claude Desktop**

## Usage Examples

### Generate a Simple Workflow

```
Create an N8n workflow that fetches data from an API, processes it with JavaScript, and stores results in a Google Sheet.
```

### Create from Template

```
Create a workflow using the "scheduled-data-sync" template named "Daily Sales Report"
```

### Custom Workflow

```
Create a custom N8n workflow with:
- Webhook trigger
- HTTP request to validate data
- IF condition to check response
- Slack notification on success
- Gmail notification on failure
```

### Validate Existing Workflow

```
Validate this N8n workflow JSON: [paste workflow JSON]
```

## Available Tools

### `generate_workflow`
Generate an N8n workflow from a natural language description.

**Parameters:**
- `description` (required): Natural language description of the desired workflow
- `name` (optional): Name for the workflow
- `template` (optional): Base template to use

### `create_template`
Create a workflow from a predefined template.

**Parameters:**
- `template` (required): Template name
- `name` (optional): Custom name for the workflow
- `customizations` (optional): Custom parameters for nodes

### `validate_workflow`
Validate an N8n workflow JSON structure.

**Parameters:**
- `workflow` (required): N8n workflow JSON to validate

### `list_node_types`
List available N8n node types and templates.

### `create_custom_workflow`
Create a custom workflow with specific nodes and connections.

**Parameters:**
- `name` (required): Workflow name
- `description` (optional): Workflow description
- `nodes` (required): Array of node configurations
- `connections` (optional): Array of connection configurations

### `export_workflow`
Export workflow in N8n import format.

**Parameters:**
- `workflow` (required): Workflow to export
- `format` (optional): Export format (json or clipboard)

## Example Workflow Output

```json
{
  "name": "API Data Processing",
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [240, 300],
      "parameters": {}
    },
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [460, 300],
      "parameters": {
        "url": "https://api.example.com/data",
        "options": {}
      }
    }
  ],
  "connections": {
    "0": {
      "main": [
        [
          {
            "node": 1,
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1"
  }
}
```

## Integration with N8n

1. **Copy Generated JSON**: Copy the workflow JSON from Claude's response
2. **Open N8n**: Navigate to your N8n instance
3. **Import Workflow**: Click the menu and select "Import from JSON"
4. **Paste JSON**: Paste the generated workflow JSON
5. **Configure Credentials**: Set up any required API credentials
6. **Test Workflow**: Execute the workflow to ensure it works correctly

## Troubleshooting

### Server Won't Start
- Ensure Node.js v18+ is installed
- Run `npm install` in the server directory
- Check that no other process is using STDIO

### Claude Desktop Can't Connect
- Verify the path in `claude_desktop_config.json` is correct
- Restart Claude Desktop after configuration changes
- Check logs in `%APPDATA%\\Claude\\logs\\` for connection errors

### Workflow Import Fails
- Validate the workflow JSON using the `validate_workflow` tool
- Ensure all node types are supported by your N8n version
- Check for missing required parameters

## Development

### Adding New Node Types

To add support for new N8n node types, edit the `NODE_TEMPLATES` object in `server.js`:

```javascript
const NODE_TEMPLATES = {
  'New Node Type': {
    id: '',
    name: 'New Node Type',
    type: 'n8n-nodes-base.newNodeType',
    typeVersion: 1,
    position: [240, 300],
    parameters: {
      // Node-specific parameters
    }
  }
};
```

### Adding New Templates

Add new workflow templates to the `WORKFLOW_TEMPLATES` object:

```javascript
const WORKFLOW_TEMPLATES = {
  'new-template': {
    name: 'New Template',
    description: 'Description of the new template',
    nodes: ['Node Type 1', 'Node Type 2'],
    connections: [
      { from: 0, to: 1 }
    ]
  }
};
```

## Technical Details

- **MCP Version**: Uses the official `@modelcontextprotocol/sdk` v0.6.0
- **Transport**: STDIO-based communication with Claude Desktop
- **Node.js**: Requires Node.js v18.0.0 or higher
- **Validation**: Uses Zod for parameter validation
- **Logging**: Structured JSON logging to stderr

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see the main project LICENSE file for details.
