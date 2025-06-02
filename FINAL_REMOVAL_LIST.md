# Final Server Removal/Consolidation List

## 🔴 SERVERS TO REMOVE (7 total)

### Code Intelligence Stubs (6 servers)
1. **code-analysis-mcp** - Stub only, duplicates Claude's abilities
2. **code-quality-mcp** - Stub only, redundant with formatter
3. **refactoring-mcp** - Stub only, edit tools sufficient
4. **test-intelligence-mcp** - Stub only, Claude writes tests well
5. **dependency-analysis-mcp** - Stub only, unless you want security scanning
6. **code-intelligence-core** - Framework for servers we're removing

### Memory Consolidation (1 server)
7. **knowledge-memory-mcp** - Remove since you prefer simple key-value
   - Keep official `memory` server instead

## 🟢 SERVERS TO KEEP (All others - 18 servers)

### Desktop Automation (ALL 4)
- ✅ windows-computer-use
- ✅ containerized-computer-use  
- ✅ screenpilot (per your request)
- ✅ claude-desktop-agent (per your request)

### Specialized Servers (ALL kept)
- ✅ n8n-mcp-server
- ✅ financial-mcp-server
- ✅ api-gateway-mcp
- ✅ vibetest-use
- ✅ fantasy-pl (if exists)

### Core Infrastructure
- ✅ filesystem
- ✅ github
- ✅ sqlite
- ✅ docker-orchestration-mcp
- ✅ memory (official)

### High-Value Integrations
- ✅ agenticseek-mcp
- ✅ playwright
- ✅ firecrawl-mcp-custom
- ✅ claude-code-integration-mcp (needs fixing)
- ✅ sequential-thinking
- ✅ pandoc

## 📊 FINAL COUNT
- **Current**: 25 servers
- **After removal**: 18 servers
- **Removed**: 7 servers (6 code intelligence stubs + 1 redundant memory)

## 🔧 ADDITIONAL ACTIONS

1. **Add 2 simple replacements** for code intelligence:
   - `code-formatter-mcp` - Simple formatter wrapper (black/prettier)
   - `security-scanner-mcp` - Simple security scanner (pip-audit/npm audit)
   
2. **Fix claude-code-integration-mcp** - Currently throwing errors

## ⚠️ CONFIRMATION NEEDED

**Do you approve:**
1. ✅ Removing the 7 servers listed above?
2. ✅ Adding the 2 simple code tool replacements?
3. ✅ Fixing the claude-code-integration-mcp errors?

This is much more conservative than my original plan - keeping all specialized servers and all desktop automation tools as requested.