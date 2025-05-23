# Gmail MCP Server Usage Guide

## Overview

The Gmail MCP server allows Claude to interact with your Gmail account, providing capabilities to read, search, and manage emails through natural language commands.

## Prerequisites

1. Node.js and npm installed
2. Google account with Gmail
3. OAuth credentials stored at `~/.gmail-mcp/gcp-oauth.keys.json`

## Installation

```bash
npm install -g @gongrzhe/server-gmail-autoauth-mcp
```

## Authentication Setup

1. Download OAuth credentials from Google Cloud Console and save to `~/.gmail-mcp/gcp-oauth.keys.json`
2. Run the authentication command:

```bash
npx -y @gongrzhe/server-gmail-autoauth-mcp auth
```

3. Follow the browser prompts to allow access to your Gmail account

## Claude Desktop Configuration

Add the following to your `claude_desktop_config.json` file:

```json
"gmail": {
  "command": "cmd",
  "args": [
    "/c",
    "npx -y @gongrzhe/server-gmail-autoauth-mcp"
  ],
  "keepAlive": true,
  "stderrToConsole": true
}
```

## Example Commands

Once configured, you can ask Claude to perform the following actions:

### List Mail Labels
```
Can you list all my Gmail labels?
```

### Show Unread Messages
```
Show me my unread emails in the inbox.
```

### Search for Specific Emails
```
Find all emails from example@gmail.com in the last week.
```

### Read Email Content
```
Read me the most recent email from my boss.
```

### Mark Emails
```
Mark the three most recent unread emails as read.
```

## Troubleshooting

### Authentication Issues

If you encounter authentication problems:

1. Delete the token file in `~/.gmail-mcp/` directory
2. Re-run the authentication command
3. Ensure your OAuth credentials file is correctly formatted and valid

### Connection Issues

If Claude cannot connect to Gmail:

1. Check that the server is running properly in Claude Desktop
2. Verify your internet connection
3. Ensure your Google account has not revoked permissions

## Security Notes

- The MCP server stores OAuth tokens locally in `~/.gmail-mcp/`
- Never share or commit these tokens to version control
- The integration uses standard OAuth flow for secure authentication
- Email content is processed locally through the MCP server
