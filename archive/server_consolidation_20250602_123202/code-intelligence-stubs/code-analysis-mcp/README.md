# Code Analysis MCP Server

Advanced semantic code analysis capabilities for Claude Desktop, providing deep understanding of code structure, symbols, complexity, and dependencies.

## Features

### Core Analysis
- **AST Parsing**: Multi-language abstract syntax tree analysis
- **Symbol Resolution**: Functions, classes, variables with scope information
- **Type Inference**: Python type information via Jedi
- **Import/Export Analysis**: Dependency tracking and module relationships

### Code Intelligence
- **Complexity Metrics**: Cyclomatic complexity, function length, class structure
- **Code Smell Detection**: Long functions, excessive dependencies, pattern violations
- **Symbol References**: Cross-file symbol usage and navigation
- **Project Dependencies**: Comprehensive dependency analysis

### Language Support
- **Python**: Full AST analysis with Jedi integration
- **JavaScript/TypeScript**: Basic analysis (extensible)
- **Multi-language**: Framework supports easy language additions

## Tools

### `analyze_code_structure`
Comprehensive file analysis returning symbols, imports, exports, and complexity metrics.

```json
{
  "file_path": "src/main.py",
  "language": "python"
}
```

### `find_symbol_references`
Find all references to a symbol across the project.

```json
{
  "symbol_name": "calculate_total",
  "project_path": "/path/to/project",
  "scope": "module"
}
```

### `get_type_info`
Get type information for expressions at specific locations.

```json
{
  "file_path": "src/utils.py",
  "line": 42,
  "column": 15
}
```

### `detect_code_smells`
Identify potential code quality issues in a directory.

```json
{
  "directory_path": "src/",
  "language": "python"
}
```

### `calculate_complexity_metrics`
Calculate detailed complexity metrics for a file.

```json
{
  "file_path": "src/complex_module.py"
}
```

### `analyze_project_dependencies`
Analyze dependencies across the entire project.

```json
{
  "project_path": "/path/to/project"
}
```

## Installation

```bash
cd servers/code-analysis-mcp
pip install -e .
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-analysis": {
      "command": "python",
      "args": ["servers/code-analysis-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Usage Examples

### Analyze File Structure
```
Analyze the code structure of src/main.py and tell me about the main functions and their complexity.
```

### Find Symbol Usage
```
Find all references to the function 'process_data' in my project and show where it's being called.
```

### Code Quality Check
```
Detect code smells in my src/ directory and suggest improvements.
```

### Type Information
```
What's the type of the variable at line 25, column 10 in utils.py?
```

## Dependencies

- **fastmcp**: MCP framework
- **jedi**: Python type inference
- **tree-sitter**: Multi-language AST parsing
- **python-json-logger**: Structured logging

## Architecture

Built on the **Code Intelligence Core** framework providing:
- Shared AST parsing utilities
- Language detection and routing
- Symbol resolution algorithms  
- Caching for performance optimization
- Extensible language support

## Integration

Works seamlessly with other MCP servers:
- **Refactoring MCP**: Uses analysis for safe transformations
- **Code Quality MCP**: Leverages complexity metrics
- **Test Intelligence MCP**: Analyzes code for test generation
- **Claude Code Integration**: Enhanced development workflow