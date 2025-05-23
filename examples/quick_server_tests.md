# Quick MCP Server Tests
*Simple prompts to validate individual server functionality*

## Purpose
Use these simple prompts to quickly verify that each MCP server is working correctly before attempting complex multi-server workflows.

---

## Financial Datasets Server Test
**Prompt:** `"Get company facts for Apple (AAPL) including basic company information."`

**Expected Result:** Company name, industry, sector, market cap, and other basic facts
**Validates:** API connectivity, authentication, and data retrieval

---

## Firecrawl Server Test
**Prompt:** `"Scrape the main content from https://example.com and summarize what you find."`

**Expected Result:** Clean text content from the webpage
**Validates:** Web scraping functionality and content extraction

---

## KnowledgeMemory Server Test
**Prompt:** `"Store this information in memory: 'My favorite programming language is Python because of its simplicity and extensive libraries.' Then retrieve and confirm what you stored."`

**Expected Result:** Confirmation of storage and accurate retrieval
**Validates:** Memory storage and retrieval functionality

---

## Sequential Thinking Server Test
**Prompt:** `"Use sequential thinking to plan a simple weekend project: organizing my digital photos. Break it down into logical steps."`

**Expected Result:** Structured thinking process with clear steps
**Validates:** Complex reasoning and planning capabilities

---

## Playwright Server Test
**Prompt:** `"Use browser automation to visit google.com and capture a screenshot of the homepage."`

**Expected Result:** Screenshot of Google homepage
**Validates:** Browser automation and screenshot capabilities

---

## ScreenPilot Server Test
**Prompt:** `"Take a screenshot of my current desktop and describe what applications appear to be running."`

**Expected Result:** Desktop screenshot with analysis of visible applications
**Validates:** Desktop monitoring and analysis

---

## Fantasy PL Server Test
**Prompt:** `"Get current Premier League player data for the top 5 forwards by points."`

**Expected Result:** List of top forwards with their points and stats
**Validates:** Sports data API connectivity and data parsing

---

## SQLite Server Test
**Prompt:** `"Create a simple database table called 'test_table' with columns for id, name, and date, then insert one sample record."`

**Expected Result:** Confirmation of table creation and data insertion
**Validates:** Database operations and SQL execution

---

## Pandoc Server Test
**Prompt:** `"Convert this markdown text to HTML: '# Test Header\nThis is a **bold** test with a [link](https://example.com).'"`

**Expected Result:** Proper HTML conversion with formatting preserved
**Validates:** Document conversion capabilities

---

## Filesystem Server Test
**Prompt:** `"Create a new text file called 'mcp_test.txt' in my Downloads folder with the content 'MCP servers are working correctly!' and then read it back to confirm."`

**Expected Result:** File creation confirmation and content verification
**Validates:** File system operations and access permissions

---

## Testing Checklist

### Before Testing
- [ ] Restart Claude Desktop to ensure all servers are loaded
- [ ] Verify internet connectivity for API-dependent servers
- [ ] Check that all required API keys are configured

### During Testing
- [ ] Test servers individually before combining
- [ ] Note any error messages or failures
- [ ] Verify expected outputs are generated
- [ ] Check Claude Desktop logs for any warnings

### After Testing
- [ ] Document any servers that failed
- [ ] Note performance issues or slow responses
- [ ] Confirm successful servers are ready for complex workflows

---

## Troubleshooting Quick Reference

**If a server fails:**
1. Check Claude Desktop logs: `C:\Users\Nithin\AppData\Roaming\Claude\logs\`
2. Verify server configuration in `claude_desktop_config.json`
3. For API servers: confirm API keys are valid and have remaining credits
4. For custom servers: check server process is running and dependencies are installed
5. Restart Claude Desktop and try again

**Common Issues:**
- **"Server transport closed unexpectedly"**: Server process crashed, check server logs
- **API authentication errors**: Verify API keys in configuration
- **File permission errors**: Ensure paths are within allowed directories
- **Network timeouts**: Check internet connectivity and API service status