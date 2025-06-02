# Server Archive Report - 2025-06-02 12:32:04

## Summary
- Servers archived: 8
- Errors encountered: 0
- Archive location: `archive/server_consolidation_20250602_123202`

## Archived Servers
- **code-analysis-mcp**: `servers/code-analysis-mcp` → `archive/server_consolidation_20250602_123202/code-intelligence-stubs/code-analysis-mcp`
- **code-quality-mcp**: `servers/code-quality-mcp` → `archive/server_consolidation_20250602_123202/code-intelligence-stubs/code-quality-mcp`
- **refactoring-mcp**: `servers/refactoring-mcp` → `archive/server_consolidation_20250602_123202/other/refactoring-mcp`
- **test-intelligence-mcp**: `servers/test-intelligence-mcp` → `archive/server_consolidation_20250602_123202/other/test-intelligence-mcp`
- **dependency-analysis-mcp**: `servers/dependency-analysis-mcp` → `archive/server_consolidation_20250602_123202/other/dependency-analysis-mcp`
- **code-intelligence-core**: `servers/code-intelligence-core` → `archive/server_consolidation_20250602_123202/code-intelligence-stubs/code-intelligence-core`
- **knowledge-memory-mcp**: `servers/knowledge-memory-mcp` → `archive/server_consolidation_20250602_123202/memory-consolidation/knowledge-memory-mcp`
- **ClaudeDesktopAgent**: `ClaudeDesktopAgent/` → `archive/server_consolidation_20250602_123202/desktop-consolidation/ClaudeDesktopAgent`
  - Note: Copied instead of moved - may need manual cleanup

## Next Steps
1. Update claude_desktop_config.json to remove references to archived servers
2. Update documentation to reflect the consolidation
3. Test remaining servers to ensure everything works
4. Delete ClaudeDesktopAgent directory if no longer needed
