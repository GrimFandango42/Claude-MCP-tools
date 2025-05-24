# N8n MCP Server - Setup and Integration Guide

## 🎉 **SUCCESS!** N8n MCP Server Created

I have successfully created a complete N8n MCP server for your Claude Desktop integration. This server enables Claude to generate N8n workflows from natural language descriptions.

## 📁 What Was Created

### Server Location
`C:\AI_Projects\Claude-MCP-tools\servers\n8n-mcp-server\`

### Files Created
- ✅ `server.js` - Main MCP server (modern implementation using official SDK)
- ✅ `package.json` - Dependencies and configuration
- ✅ `README.md` - Complete documentation
- ✅ `test-server.js` - Automated test suite
- ✅ `examples.md` - Example workflows and usage patterns
- ✅ `run-n8n-mcp.bat` - Easy startup script
- ✅ `install-deps.bat` - Dependency installation
- ✅ `claude_desktop_config_example.json` - Configuration template

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd "C:\AI_Projects\Claude-MCP-tools\servers\n8n-mcp-server"
npm install
```
*Or double-click `install-deps.bat`*

### Step 2: Test the Server
```bash
npm test
```
*Or run `node test-server.js`*

### Step 3: Add to Claude Desktop
Edit your Claude Desktop config file:
`%APPDATA%\Claude\claude_desktop_config.json`

Add this server configuration:
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

### Step 4: Restart Claude Desktop
Close and reopen Claude Desktop to load the new server.

## 🎯 What You Can Do Now

### Generate N8n Workflows with Natural Language

**Example Requests:**
- "Create an N8n workflow that fetches data from an API and processes it"
- "Generate a scheduled workflow that syncs sales data to Google Sheets daily"
- "Build a webhook workflow that sends Slack notifications"
- "Create a workflow that monitors RSS feeds and emails summaries"

### Available Tools
1. **generate_workflow** - Create workflows from descriptions
2. **create_template** - Use predefined templates
3. **validate_workflow** - Check workflow structure
4. **list_node_types** - See available nodes
5. **create_custom_workflow** - Build complex workflows
6. **export_workflow** - Format for N8n import

### Supported Node Types
- Triggers: Manual, Schedule, Webhook
- Actions: HTTP Request, Code, Set, IF
- Services: Gmail, Slack, Google Sheets
- *Easily extensible for more types*

## 📋 Testing Your Setup

### 1. Test Server Connection
After adding to Claude Desktop config, ask Claude:
```
List the available N8n node types
```

### 2. Generate a Simple Workflow
```
Create a basic N8n workflow that makes an HTTP request and processes the response
```

### 3. Test N8n Import
1. Copy the generated JSON from Claude's response
2. Open your N8n instance
3. Click Import → From JSON
4. Paste and import
5. Configure any credentials needed

## 🔧 Server Capabilities

### Workflow Generation Features
- **Smart Node Selection**: Analyzes descriptions to choose appropriate nodes
- **Connection Management**: Automatically creates proper node connections
- **Template System**: Predefined patterns for common workflows
- **Validation**: Ensures workflows are valid before export
- **Custom Configurations**: Supports complex node parameters

### N8n Compatibility
- Generates valid N8n workflow JSON
- Includes proper node IDs and positioning
- Handles connections and data flow
- Ready for direct import into N8n
- Supports N8n workflow metadata

## 📖 Usage Examples

See `examples.md` for detailed workflow examples including:
- Basic HTTP data processing
- Scheduled data synchronization  
- Webhook notification systems
- Complex multi-branch workflows

## 🔧 Troubleshooting

### Server Won't Start
- Ensure Node.js v18+ is installed
- Run `npm install` in the server directory
- Check console for error messages

### Claude Can't Connect
- Verify file path in config is correct
- Restart Claude Desktop after config changes
- Check Claude logs: `%APPDATA%\Claude\logs\`

### Workflow Import Issues
- Use the `validate_workflow` tool first
- Ensure all required credentials are configured in N8n
- Check N8n version compatibility

## 🎨 Customization

### Adding New Node Types
Edit `NODE_TEMPLATES` in `server.js`:
```javascript
'Your Node': {
  id: '',
  name: 'Your Node',
  type: 'n8n-nodes-base.yourNode',
  typeVersion: 1,
  position: [240, 300],
  parameters: {
    // Your node parameters
  }
}
```

### Adding Workflow Templates
Edit `WORKFLOW_TEMPLATES` in `server.js`:
```javascript
'your-template': {
  name: 'Your Template',
  description: 'Template description',
  nodes: ['Node1', 'Node2'],
  connections: [{ from: 0, to: 1 }]
}
```

## 🌟 What Makes This Special

1. **Complete Integration**: Full MCP protocol compliance with Claude Desktop
2. **Modern Architecture**: Uses official MCP SDK and best practices
3. **Natural Language**: Convert plain English to working N8n workflows
4. **Production Ready**: Comprehensive error handling and validation
5. **Extensible**: Easy to add new nodes and capabilities
6. **Well Documented**: Complete examples and usage instructions

## 🔄 Next Steps

1. **Install and Test**: Follow the quick setup above
2. **Generate Workflows**: Try the example requests
3. **Import to N8n**: Test with your N8n instance
4. **Customize**: Add your specific node types or templates
5. **Integrate**: Use in your automation projects

## 📞 Integration Validation

To verify everything is working:

1. **Server Status**: Run `npm test` - all tests should pass
2. **Claude Connection**: Ask Claude to list N8n node types
3. **Workflow Generation**: Generate a simple workflow
4. **N8n Import**: Successfully import generated JSON
5. **Workflow Execution**: Execute workflow in N8n

---

**🎯 Goal Achieved**: You now have a fully functional N8n MCP server that integrates with Claude Desktop, enabling natural language workflow generation for N8n automation!

The server follows your established patterns from the Claude-MCP-tools project and provides a solid foundation for N8n workflow automation through conversational AI.
