# Code Intelligence MCP Setup Guide

Complete setup instructions for the new Code Intelligence MCP servers.

## Quick Start

1. **Install Dependencies for Each Server**:
```bash
# Code Intelligence Core (shared framework)
cd servers/code-intelligence-core
pip install -e .

# Code Analysis MCP
cd ../code-analysis-mcp
pip install -e .

# Code Quality MCP  
cd ../code-quality-mcp
pip install -e .

# Refactoring MCP
cd ../refactoring-mcp
pip install -e .

# Test Intelligence MCP
cd ../test-intelligence-mcp
pip install -e .

# Dependency Analysis MCP
cd ../dependency-analysis-mcp
pip install -e .
```

2. **Update Claude Desktop Configuration**:
   - Copy the contents of `claude_desktop_config_code_intelligence.json`
   - Add to your Claude Desktop config at: 
     - Windows: `C:\Users\<Username>\AppData\Roaming\Claude\claude_desktop_config.json`
     - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

3. **Restart Claude Desktop**

## Detailed Setup

### Prerequisites

#### Python Environment
```bash
# Ensure Python 3.8+ is installed
python --version

# Install core dependencies
pip install fastmcp python-json-logger aiofiles
```

#### Code Quality Tools
```bash
# Python linting and formatting
pip install black isort flake8 pylint mypy autopep8 coverage

# JavaScript tools (if using JS projects)
npm install -g eslint prettier jshint
```

#### Security Tools
```bash
# Python security scanning
pip install pip-audit safety

# JavaScript security (npm audit is built-in)
```

#### Refactoring Tools
```bash
# Python refactoring
pip install rope libcst jedi gitpython
```

#### Testing Tools
```bash
# Python testing
pip install pytest pytest-cov hypothesis

# Coverage analysis
pip install coverage
```

### Server-by-Server Installation

#### 1. Code Intelligence Core
```bash
cd servers/code-intelligence-core
pip install -e .

# Test the core framework
python -c "from core import get_core; print('Core framework loaded successfully')"
```

#### 2. Code Analysis MCP
```bash
cd servers/code-analysis-mcp
pip install -e .

# Test AST parsing
python server.py &
# Should start without errors, then Ctrl+C to stop
```

#### 3. Code Quality MCP
```bash
cd servers/code-quality-mcp
pip install -e .

# Verify linting tools are available
black --version
flake8 --version
pylint --version
```

#### 4. Refactoring MCP
```bash
cd servers/refactoring-mcp
pip install -e .

# Test rope integration
python -c "import rope.base.project; print('Rope integration working')"
```

#### 5. Test Intelligence MCP
```bash
cd servers/test-intelligence-mcp
pip install -e .

# Verify test frameworks
pytest --version
coverage --version
```

#### 6. Dependency Analysis MCP
```bash
cd servers/dependency-analysis-mcp
pip install -e .

# Test security tools
pip-audit --version
safety --version
```

## Configuration

### Claude Desktop Config

Complete configuration with all Code Intelligence servers:

```json
{
  "mcpServers": {
    "code-analysis": {
      "command": "python",
      "args": ["servers/code-analysis-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true,
      "env": {
        "PYTHONPATH": "/path/to/Claude-MCP-tools/servers/code-intelligence-core"
      }
    },
    "code-quality": {
      "command": "python", 
      "args": ["servers/code-quality-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true
    },
    "refactoring": {
      "command": "python",
      "args": ["servers/refactoring-mcp/server.py"], 
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true,
      "env": {
        "PYTHONPATH": "/path/to/Claude-MCP-tools/servers/code-intelligence-core"
      }
    },
    "test-intelligence": {
      "command": "python",
      "args": ["servers/test-intelligence-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools", 
      "keepAlive": true,
      "stderrToConsole": true,
      "env": {
        "PYTHONPATH": "/path/to/Claude-MCP-tools/servers/code-intelligence-core"
      }
    },
    "dependency-analysis": {
      "command": "python",
      "args": ["servers/dependency-analysis-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true, 
      "stderrToConsole": true
    }
  }
}
```

### Environment Variables

Optional environment variables for enhanced functionality:

```bash
# API keys for enhanced security scanning
export SNYK_TOKEN="your_snyk_token"
export GITHUB_TOKEN="your_github_token"

# Custom tool paths
export BLACK_PATH="/custom/path/to/black"
export PYLINT_PATH="/custom/path/to/pylint"
```

## Testing Installation

### Basic Functionality Test

Create a test Python file:

```python
# test_file.py
def calculate_total(items):
    """Calculate total price of items."""
    total = 0
    for item in items:
        total += item.price
    return total

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
```

### Test Each Server

#### Code Analysis
```
Ask Claude: "Analyze the code structure of test_file.py and show me the functions and classes"
```

#### Code Quality  
```
Ask Claude: "Lint test_file.py and format it using black"
```

#### Refactoring
```
Ask Claude: "Rename the function 'calculate_total' to 'compute_total_price' in test_file.py"
```

#### Test Intelligence
```
Ask Claude: "Generate unit tests for the calculate_total function in test_file.py"
```

#### Dependency Analysis
```
Ask Claude: "Scan this project for security vulnerabilities and unused dependencies"
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Fix Python path issues
export PYTHONPATH="/path/to/Claude-MCP-tools/servers/code-intelligence-core:$PYTHONPATH"
```

#### 2. Tool Not Found Errors
```bash
# Install missing tools
pip install black flake8 pylint mypy
pip install pip-audit safety
```

#### 3. Permission Errors
```bash
# Fix file permissions
chmod +x servers/*/server.py
```

#### 4. Server Won't Start
```bash
# Check logs in Claude Desktop logs directory
# Windows: C:\Users\<Username>\AppData\Roaming\Claude\logs\
# Mac: ~/Library/Application Support/Claude/logs/

# Test server manually
cd servers/code-analysis-mcp
python server.py
```

### Debugging Tips

1. **Check Claude Desktop logs** for error messages
2. **Test servers individually** before adding to config
3. **Verify all dependencies** are installed
4. **Use absolute paths** in configuration
5. **Restart Claude Desktop** after config changes

## Integration Workflows

### Complete Development Workflow

1. **Analyze Code Structure**:
   ```
   Analyze the code structure of src/main.py
   ```

2. **Quality Check**:
   ```
   Lint and format all Python files in src/ directory
   ```

3. **Security Scan**:
   ```
   Scan for security vulnerabilities and check license compliance
   ```

4. **Generate Tests**:
   ```
   Generate comprehensive unit tests for the main functions
   ```

5. **Safe Refactoring**:
   ```
   Extract the complex logic in process_data function into smaller methods
   ```

### Maintenance Workflow

1. **Weekly Security Scan**:
   ```
   Perform comprehensive dependency analysis and security scanning
   ```

2. **Monthly Cleanup**:
   ```
   Find unused dependencies and suggest safe updates
   ```

3. **Quality Monitoring**:
   ```
   Check code quality metrics and documentation coverage
   ```

## Performance Optimization

### Server Performance
- **Parallel Processing**: Servers run concurrently for better performance
- **Caching**: Code analysis results cached for repeated operations  
- **Incremental Analysis**: Only analyze changed files when possible

### Memory Usage
- **Lazy Loading**: Modules loaded only when needed
- **Resource Cleanup**: Temporary files cleaned automatically
- **Connection Pooling**: Efficient resource management

## Next Steps

1. **Explore Advanced Features**: Try complex refactoring and test generation
2. **Custom Configurations**: Adjust linting rules and quality thresholds  
3. **Integration**: Combine with existing MCP servers for workflows
4. **Automation**: Set up automated quality checks in development process

The Code Intelligence MCP servers transform Claude Desktop into a powerful development environment with advanced code understanding, quality assurance, and automated refactoring capabilities.