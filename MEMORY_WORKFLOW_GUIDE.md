# Memory Workflow Guide

## 🧠 Memory MCP Integration for Enhanced Context Retention

This guide explains how to use the Memory MCP server effectively to maintain context across Claude Desktop sessions, similar to conversation memory.

## 🚀 Quick Start

### Session Beginning
1. **Search for context**: `mcp__memory__search_nodes` with relevant keywords
2. **Review related entities**: Check existing project knowledge
3. **Plan current work**: Based on memory context and current goals

### During Work
1. **Document discoveries**: Create entities for new components/solutions
2. **Update progress**: Add observations to existing entities
3. **Link related items**: Create relations between connected components

### Session End
1. **Summarize work**: Create session summary entity
2. **Update project status**: Add observations about changes made
3. **Set context for next session**: Document next steps and important context

## 📋 Memory Entity Types

### Core Entity Types Used
- **repository**: Main project containers
- **server**: Individual MCP servers
- **process**: Development workflows and procedures
- **document**: Important documentation files
- **configuration**: Config files and settings
- **knowledge**: Solutions, patterns, and learnings
- **timeline**: Chronological project events
- **reference**: Key locations and resources

## 🔍 Effective Search Strategies

### Single Keywords (Recommended)
- `consolidation` - Server consolidation work
- `FastMCP` - Framework-related information
- `server` - All server-related entities
- `configuration` - Config files and settings
- `documentation` - Document entities
- `workflow` - Process and procedure entities

### Search by Entity Type
- Search "server" to find all MCP servers
- Search "document" to find documentation
- Search "process" to find workflows

### Search by Status
- Search "operational" for working components
- Search "fixed" for resolved issues
- Search "production" for ready systems

## 🔧 Common Memory Operations

### Create New Server Entity
```
Entity: "{Server Name} MCP"
Type: server
Observations:
- Primary functionality description
- Location: servers/{name}-mcp/
- Key features and capabilities
- Status: [Operational/Under Development/Fixed]
- Dependencies and requirements
```

### Document Issue Resolution
```
Entity: "{Issue Description}"
Type: knowledge
Observations:
- Problem: [What went wrong]
- Root Cause: [Why it happened]
- Solution: [How it was fixed]
- Prevention: [How to avoid future occurrences]
- Related Components: [What was affected]
```

### Track Development Process
```
Entity: "{Process Name}"
Type: process
Observations:
- Step-by-step procedure
- Key tools and commands used
- Best practices discovered
- Common pitfalls to avoid
- Success criteria
```

## 📈 Memory Enhancement Patterns

### Rich Observations
Include detailed, searchable information:
- **Specific tools**: "Uses FastMCP framework with stdio transport"
- **Exact locations**: "Location: servers/agenticseek-mcp/"
- **Status details**: "Status: Fixed asyncio conflicts, 100% success rate"
- **Key capabilities**: "Smart routing between DeepSeek, OpenAI, Google"

### Meaningful Relations
Connect related components:
- `hosts` - Repository hosts servers
- `documents` - Documentation describes components
- `fixes` - Solutions address problems
- `collaborates_with` - Servers work together
- `alternative_to` - Different approaches to same goal

### Consistent Naming
Use standard naming conventions:
- Servers: "{Name} MCP Server"
- Documents: Use actual filename (e.g., "PROJECT_STATUS.md")
- Processes: Descriptive action names (e.g., "Server Consolidation Process")

## 🎯 Project-Specific Memory Usage

### Start of Session Search Terms
```
# Search these keywords at session start:
mcp__memory__search_nodes("consolidation")  # Recent major work
mcp__memory__search_nodes("server")        # Server ecosystem
mcp__memory__search_nodes("documentation") # Available docs
mcp__memory__search_nodes("workflow")      # Process guidance
mcp__memory__search_nodes("configuration") # Config files
```

### Essential Memory Entities Already Created
- **Claude-MCP-Tools Repository**: Main project container
- **Server Consolidation Process**: Recent optimization work
- **21 Individual Servers**: All operational components
- **Development Workflow**: Standard procedures
- **Common Issues and Solutions**: Troubleshooting knowledge
- **Key File Locations**: Important paths and references

### Recommended Memory Updates
1. **Session Summaries**: Create entity for each significant session
2. **Decision Records**: Document important architectural choices
3. **Learning Notes**: Capture insights and best practices
4. **Issue Tracking**: Document problems and solutions
5. **Progress Updates**: Regular status observations

## 📚 Memory vs Project Features

### Memory MCP Advantages
- **Persistent**: Survives restarts and tool switches
- **Searchable**: Find specific information quickly
- **Relational**: Discover connected information
- **Shared**: Available to both Claude Desktop and Claude Code

### Complementary with Projects
- **Project Instructions**: Define consistent behavior
- **Document Upload**: Provide reference materials
- **Memory MCP**: Store dynamic, evolving knowledge
- **Session Templates**: Structure consistent workflows

## 🎉 Expected Benefits

### Improved Context Retention
- Faster session startup with relevant context
- Better decision making based on historical knowledge
- Reduced need to re-explain project structure
- Consistent coding patterns and best practices

### Enhanced Problem Solving
- Quick access to previous solutions
- Pattern recognition across similar issues
- Comprehensive troubleshooting knowledge base
- Systematic tracking of what works

### Better Project Continuity
- Clear understanding of project evolution
- Documented decision rationale
- Preserved institutional knowledge
- Seamless handoffs between sessions

---

**Remember**: The Memory MCP server provides persistent, searchable knowledge that both Claude Desktop and Claude Code can access. Use it actively to build a comprehensive project knowledge base that improves over time!