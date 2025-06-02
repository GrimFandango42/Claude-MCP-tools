# Code Quality MCP Server

Comprehensive code quality analysis, linting, and formatting server for Claude Desktop, ensuring code adheres to best practices and style guides.

## Features

### Multi-Tool Linting
- **Python**: flake8, pylint, mypy integration
- **Auto-fix**: Automatic issue resolution with autopep8, black, isort
- **Custom Rules**: Configurable rulesets and style guides
- **Parallel Analysis**: Multiple linters running simultaneously

### Code Formatting
- **Black**: Opinionated Python formatter
- **autopep8**: PEP 8 compliance formatting
- **isort**: Import statement organization
- **Style Guides**: Support for PEP 8, Google, custom configurations

### Quality Metrics
- **Documentation Coverage**: Function and class docstring analysis
- **Test Coverage**: Integration with coverage.py for test analysis
- **Style Compliance**: Comprehensive style guide enforcement
- **Batch Processing**: Directory-wide quality analysis

### Auto-Fix Capabilities
- **Safe Transformations**: Automatic formatting without breaking code
- **Incremental Fixes**: Apply fixes progressively
- **Preview Mode**: See changes before applying
- **Rollback Support**: Undo unwanted changes

## Tools

### `lint_code`
Comprehensive linting with multiple tools and auto-fix support.

```json
{
  "file_path": "src/main.py",
  "ruleset": "pep8",
  "auto_fix": true,
  "tools": ["flake8", "pylint", "mypy"]
}
```

### `format_code`
Format code according to specified style guide.

```json
{
  "file_path": "src/utils.py",
  "style_guide": "black",
  "formatter": "black"
}
```

### `check_documentation_coverage`
Analyze documentation coverage across a project.

```json
{
  "directory": "src/",
  "threshold": 80.0
}
```

### `analyze_test_coverage`
Run tests and analyze code coverage.

```json
{
  "test_command": "pytest tests/",
  "project_path": "/path/to/project"
}
```

### `enforce_style_guide`
Enforce style guide across entire directory.

```json
{
  "style_config": {"max_line_length": 88, "use_tabs": false},
  "directory": "src/",
  "apply_fixes": true
}
```

## Installation

```bash
cd servers/code-quality-mcp
pip install -e .
```

### Required Tools

Install the Python quality tools:
```bash
pip install black isort flake8 pylint mypy autopep8 coverage
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-quality": {
      "command": "python",
      "args": ["servers/code-quality-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Usage Examples

### Lint and Fix File
```
Lint src/main.py with flake8 and pylint, then auto-fix any issues found.
```

### Format Entire Project
```
Format all Python files in my src/ directory using black style guide.
```

### Check Documentation
```
Check documentation coverage for my project and identify functions missing docstrings.
```

### Test Coverage Analysis
```
Run my test suite and analyze code coverage, highlighting areas that need more tests.
```

### Style Guide Enforcement
```
Enforce PEP 8 style guide across my entire codebase and fix violations automatically.
```

## Quality Tools Integration

### Python Linters
- **flake8**: Style guide enforcement (PEP 8)
- **pylint**: Comprehensive code analysis
- **mypy**: Static type checking

### Formatters
- **black**: Uncompromising code formatter
- **autopep8**: Automatic PEP 8 formatting
- **isort**: Import statement sorting

### Coverage Tools
- **coverage.py**: Test coverage measurement
- **pytest-cov**: Pytest coverage integration

## Configuration Options

### Ruleset Configurations
```json
{
  "pep8": {
    "max_line_length": 79,
    "ignore": ["E203", "W503"]
  },
  "google": {
    "max_line_length": 88,
    "docstring_style": "google"
  },
  "black": {
    "line_length": 88,
    "skip_string_normalization": false
  }
}
```

### Auto-Fix Settings
```json
{
  "auto_fix": true,
  "formatters": ["autopep8", "black", "isort"],
  "safe_mode": true,
  "preview_changes": false
}
```

## Integration Patterns

### With Code Analysis MCP
```python
# Workflow: Analyze → Quality Check → Fix
1. code_analysis.analyze_code_structure("src/main.py")
2. code_quality.lint_code("src/main.py", auto_fix=True)
3. code_analysis.calculate_complexity_metrics("src/main.py")
```

### With Development Workflow
```python
# Pre-commit quality checks
1. code_quality.enforce_style_guide(config, "src/", apply_fixes=True)
2. code_quality.analyze_test_coverage("pytest tests/")
3. code_quality.check_documentation_coverage("src/", threshold=80)
```

## Error Handling

- **Tool Availability**: Graceful fallback when tools aren't installed
- **Syntax Errors**: Skip linting files with syntax issues
- **Permission Issues**: Clear error messages for file access problems
- **Command Failures**: Detailed error reporting with suggested fixes

## Performance

- **Parallel Processing**: Multiple linters run concurrently
- **Incremental Analysis**: Only analyze changed files
- **Caching**: Results cached to avoid re-analysis
- **Batch Operations**: Efficient directory-wide processing

## Best Practices

1. **Run linting before committing code**
2. **Use auto-fix for safe formatting operations**
3. **Maintain high documentation coverage (>80%)**
4. **Regular test coverage analysis**
5. **Enforce consistent style guides across team**

Works seamlessly with other Code Intelligence MCPs for comprehensive development workflow automation.