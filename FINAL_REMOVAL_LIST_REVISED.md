# Final Server Removal/Consolidation List (Revised)

## 🔴 SERVERS TO REMOVE (9 total)

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

### Desktop Automation Consolidation (2 servers)
8. **screenpilot** - Overlaps with windows-computer-use capabilities
9. **claude-desktop-agent** - Basic screenshot functionality covered by windows-computer-use

**Keeping:**
- ✅ **windows-computer-use** - Most comprehensive, native Windows automation
- ✅ **containerized-computer-use** - Unique value: security isolation for untrusted automation

## 🟢 SERVERS TO KEEP (16 servers)

### Desktop Automation (2 - consolidated from 4)
- ✅ windows-computer-use (comprehensive native automation)
- ✅ containerized-computer-use (isolated/secure automation)

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
- ✅ playwright (web automation - different from desktop)
- ✅ firecrawl-mcp-custom
- ✅ claude-code-integration-mcp (needs fixing)
- ✅ sequential-thinking
- ✅ pandoc

## 📊 FINAL COUNT
- **Current**: 25 servers
- **After removal**: 18 servers (removing 9, adding 2)
- **Removed**: 9 servers

## 🔧 ADDITIONAL ACTIONS

1. **Add 2 simple replacements** for code intelligence:
   - `code-formatter-mcp` - Simple formatter wrapper (already created)
   - `security-scanner-mcp` - Simple security scanner (already created)
   
2. **Fix claude-code-integration-mcp** - Currently throwing errors

## 💡 RATIONALE FOR DESKTOP CONSOLIDATION

**Why remove screenpilot & claude-desktop-agent:**
- `windows-computer-use` already provides screenshot, mouse, keyboard, window management
- `screenpilot` doesn't add unique capabilities
- `claude-desktop-agent` was an early prototype with basic screenshot only

**Why keep two:**
- `windows-computer-use` - For normal desktop automation
- `containerized-computer-use` - For when you need isolation (untrusted sites, testing)

## ⚠️ CONFIRMATION NEEDED

**Do you approve:**
1. ✅ Removing the 9 servers listed above?
2. ✅ Adding the 2 simple code tool replacements?
3. ✅ Fixing the claude-code-integration-mcp errors?