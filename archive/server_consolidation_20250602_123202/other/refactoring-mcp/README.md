# Refactoring MCP Server

Advanced automated refactoring capabilities for Claude Desktop, providing safe code transformations with AST-based analysis and git integration.

## Features

### Safe Refactoring Operations
- **Symbol Renaming**: Cross-file symbol renaming with reference tracking
- **Extract Method**: Convert code blocks into reusable methods
- **Extract Variable**: Extract expressions into named variables
- **Inline Operations**: Replace method/variable usage with definitions
- **Move Symbols**: Relocate classes/functions between files

### Safety & Reliability
- **AST-Based**: Uses abstract syntax trees for safe transformations
- **Backup Creation**: Automatic file backups before changes
- **Git Integration**: Automatic commits with descriptive messages
- **Preview Mode**: See changes before applying
- **Rollback Support**: Easy reversion of changes

### Language Support
- **Python**: Full support via Rope library
- **Cross-Reference**: Tracks symbol usage across multiple files
- **Project-Wide**: Operations work across entire project
- **Scope Control**: File, module, or project-level transformations

## Tools

### `rename_symbol`
Safely rename symbols across project with reference tracking.

```json
{
  "old_name": "calculateTotal",
  "new_name": "compute_total",
  "file_path": "src/calculator.py",
  "scope": "project",
  "project_path": "/path/to/project"
}
```

### `extract_method`
Extract code lines into a new method.

```json
{
  "file_path": "src/utils.py",
  "start_line": 15,
  "end_line": 25,
  "method_name": "validate_input",
  "project_path": "/path/to/project"
}
```

### `extract_variable`
Extract expression into a named variable.

```json
{
  "file_path": "src/math_utils.py",
  "line": 42,
  "column": 15,
  "variable_name": "calculation_result"
}
```

### `inline_method`
Inline method calls with method body.

```json
{
  "file_path": "src/helpers.py",
  "method_name": "simple_getter",
  "project_path": "/path/to/project"
}
```

### `move_to_file`
Move symbol from one file to another.

```json
{
  "source_file": "src/old_module.py",
  "symbol_name": "UtilityClass",
  "target_file": "src/new_module.py"
}
```

### `preview_refactoring`
Preview refactoring changes before applying.

```json
{
  "operation": "rename",
  "parameters": {
    "old_name": "oldFunction",
    "new_name": "newFunction",
    "file_path": "src/main.py"
  }
}
```

## Installation

```bash
cd servers/refactoring-mcp
pip install -e .
```

### Required Dependencies

- **rope**: Python refactoring library
- **libcst**: Concrete syntax tree manipulation
- **gitpython**: Git integration for automatic commits
- **jedi**: Symbol analysis support

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "refactoring": {
      "command": "python",
      "args": ["servers/refactoring-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Usage Examples

### Rename Function Across Project
```
Rename the function 'process_data' to 'transform_data' across my entire project and update all references.
```

### Extract Complex Logic
```
Extract lines 25-40 from src/calculator.py into a new method called 'validate_calculation'.
```

### Clean Up Code Structure
```
Move the UtilityClass from src/main.py to src/utils.py and update all imports.
```

### Inline Simple Methods
```
Inline the method 'get_name' in src/user.py since it's just a simple getter.
```

### Safe Refactoring Workflow
```
Preview the rename of 'old_method' to 'new_method' first, then apply if the changes look correct.
```

## Safety Features

### Automatic Backups
- Creates `.refactor_backup` files before changes
- Preserves original code for easy rollback
- Maintains backup history for multiple operations

### Git Integration
- Automatic commits after successful refactoring
- Descriptive commit messages with operation details
- Easy reversion using git history
- Tracks all files modified in single commit

### AST-Based Safety
- Analyzes code structure before modifications
- Prevents breaking syntax or semantics
- Validates symbol references and scopes
- Ensures type safety where possible

### Error Handling
- Graceful failure without corrupting files
- Detailed error messages with context
- Rollback on partial failures
- Validation before applying changes

## Advanced Features

### Cross-File Operations
```python
# Rename symbol across multiple files
rename_symbol("DatabaseConnection", "DbConnection", scope="project")

# Move class between modules with import updates
move_to_file("src/models.py", "User", "src/user_model.py")
```

### Method Extraction Patterns
```python
# Extract complex calculation
extract_method("src/finance.py", 45, 65, "calculate_compound_interest")

# Extract validation logic
extract_method("src/api.py", 120, 135, "validate_request_data")
```

### Code Organization
```python
# Move related functions together
move_to_file("src/main.py", "helper_function", "src/helpers.py")

# Inline unnecessary abstractions
inline_method("src/utils.py", "trivial_wrapper")
```

## Integration Patterns

### With Code Analysis MCP
```python
# Workflow: Analyze → Refactor → Verify
1. code_analysis.analyze_code_structure("src/complex.py")
2. refactoring.extract_method("src/complex.py", 50, 80, "split_logic")
3. code_analysis.calculate_complexity_metrics("src/complex.py")
```

### With Code Quality MCP
```python
# Quality-driven refactoring
1. code_quality.detect_code_smells("src/")
2. refactoring.extract_method(long_method_file, start, end, new_name)
3. code_quality.lint_code(modified_file, auto_fix=True)
```

### With Git Workflow
```python
# Automated refactoring with version control
1. refactoring.rename_symbol("old_name", "new_name", scope="project")
   # Automatically creates git commit
2. Continue development with clean history
3. Easy rollback if needed: git revert <commit>
```

## Performance Optimization

- **Project Caching**: Reuses Rope project instances
- **Incremental Analysis**: Only analyzes affected files
- **Lazy Loading**: Loads libraries only when needed
- **Efficient AST**: Minimal tree traversal for operations

## Best Practices

1. **Always use preview mode** for complex refactoring
2. **Commit frequently** to enable easy rollback
3. **Test after refactoring** to ensure correctness
4. **Use descriptive names** for extracted methods/variables
5. **Refactor incrementally** rather than large changes

## Error Recovery

- **Backup Restoration**: Automatic file restoration on errors
- **Git Revert**: Use git history to undo changes
- **Partial Rollback**: Selective restoration of specific files
- **Validation Checks**: Pre-flight checks prevent invalid operations

Works seamlessly with Code Analysis and Code Quality MCPs for comprehensive development workflow automation.