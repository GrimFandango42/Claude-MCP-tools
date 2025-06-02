# Detailed Server Consolidation Plan - REQUIRES APPROVAL

## Summary
- **Current**: 25 servers
- **Proposed**: 12-14 servers
- **To Remove**: 11-13 servers (pending your approval)

## 🟢 KEEP AS-IS (8 servers)

### Core Infrastructure
1. **filesystem** - Essential file operations
2. **github** - Repository management API
3. **sqlite** - Database operations
4. **docker-orchestration-mcp** - Container management

### High-Value Integrations  
5. **agenticseek-mcp** - Multi-provider AI routing (recently fixed)
6. **playwright** - Browser automation
7. **firecrawl-mcp-custom** - Advanced web scraping
8. **financial-mcp-server** - Market data API

## 🟡 CONSOLIDATE (7 servers → 3 servers)

### Memory/Knowledge (3 → 1)
**Current:**
- `memory` (official MCP)
- `knowledge-memory-mcp` (vector search)
- Legacy memory implementations in archive

**Recommendation:** KEEP `memory` (official) OR `knowledge-memory-mcp` (if vector search needed)
**Your choice?** _______________

### Desktop Automation (4 → 2)
**Current:**
- `windows-computer-use` - Native Windows automation
- `containerized-computer-use` - Docker-isolated GUI
- `screenpilot` - Screen analysis
- `claude-desktop-agent` - Screenshot tool

**Recommendation:** 
- KEEP `windows-computer-use` (most comprehensive)
- KEEP `containerized-computer-use` (security isolation)
- REMOVE others unless you have specific use cases

**Your approval?** _______________

## 🔴 PROPOSED FOR REMOVAL (11 servers)

### Code Intelligence Servers (6 servers)
**Never implemented/stubs only:**
1. **code-analysis-mcp** - Claude already understands code
2. **code-quality-mcp** - Redundant with formatter
3. **refactoring-mcp** - Edit tools sufficient
4. **test-intelligence-mcp** - Claude writes tests well
5. **dependency-analysis-mcp** - Unless security scanning critical
6. **code-intelligence-core** - Over-abstraction

**Your approval to remove?** _______________

### Specialized/Rarely Used (5 servers)
7. **n8n-mcp-server** - Workflow automation (specialized)
8. **test-automation-mcp** - Overlaps with playwright
9. **api-gateway-mcp** - Unless actively using multi-provider APIs
10. **vibetest-use** - Very specialized QA tool
11. **fantasy-pl** - Sports-specific

**Your approval to remove?** _______________

## 🟢 PROPOSED NEW SERVERS (2 simple implementations)

### Replace 6 code intelligence servers with 2 focused ones:
1. **code-formatter-mcp** - Simple black/prettier wrapper (50 lines)
2. **security-scanner-mcp** - pip-audit/npm audit wrapper (100 lines)

**Your approval to add?** _______________

## 📋 IMPLEMENTATION PLAN

### Phase 1: Cleanup (After Your Approval)
1. Archive servers marked for removal
2. Keep backups for 30 days
3. Update configurations

### Phase 2: Consolidation
1. Choose ONE memory solution
2. Remove redundant desktop tools
3. Add two simple code tools

### Phase 3: Documentation
1. Update README with final server list
2. Document clear use case for each
3. Remove references to deleted servers

## 🤔 SPECIFIC QUESTIONS FOR YOU

1. **Memory Choice**: Do you need vector search (`knowledge-memory-mcp`) or is simple key-value enough (`memory`)?

2. **Desktop Tools**: Do you use `screenpilot` or `claude-desktop-agent` for anything specific?

3. **Specialized Servers**: 
   - Are you actively using `n8n-mcp-server`?
   - Do you need `api-gateway-mcp` for anything?
   - Is `vibetest-use` being used?
   - Do you use `fantasy-pl`?

4. **Security Scanning**: Is dependency security scanning important enough to keep?

5. **Code Formatting**: Do you want the simple formatter/security scanner replacements?

## 📊 FINAL COUNT IF APPROVED

**Before**: 25 servers
**After**: 12-14 servers (depending on your choices)

**Breakdown**:
- 8 Keep as-is
- 2-3 From consolidation 
- 2 New simple replacements
- = 12-13 total

## ⚠️ NOTHING WILL BE DELETED WITHOUT YOUR EXPLICIT APPROVAL

Please review and let me know:
1. Which servers you definitely want to keep
2. Which removals you approve
3. Any servers you're unsure about
4. Whether to add the two simple code tool replacements

I'll wait for your approval before making any changes.