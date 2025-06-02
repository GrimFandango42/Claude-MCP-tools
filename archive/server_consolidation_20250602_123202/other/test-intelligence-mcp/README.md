# Test Intelligence MCP Server

Advanced automated testing capabilities for Claude Desktop, providing intelligent test generation, coverage analysis, and test suite optimization.

## Features

### Automated Test Generation
- **Unit Test Generation**: Create comprehensive unit tests from function analysis
- **Property-Based Testing**: Generate Hypothesis tests for robust validation  
- **Edge Case Detection**: Identify and test boundary conditions
- **Exception Testing**: Generate tests for error handling paths
- **Framework Support**: pytest, unittest, and custom frameworks

### Coverage Intelligence
- **Gap Analysis**: Identify untested code areas with surgical precision
- **Coverage Reporting**: Integration with coverage.py for detailed analysis
- **Threshold Monitoring**: Set and track coverage goals
- **Impact Analysis**: Determine which tests to run based on code changes
- **Regression Prevention**: Ensure new code maintains coverage standards

### Test Quality Analysis
- **Flaky Test Detection**: Identify unreliable tests through repeated execution
- **Test Performance**: Analyze test execution time and optimization opportunities
- **Mutation Testing**: Validate test effectiveness with code mutations
- **Test Dependency Analysis**: Map test relationships and dependencies

### Smart Test Selection
- **Impact-Based Testing**: Run only tests affected by code changes
- **Dependency Tracking**: Understand test-code relationships
- **Parallel Execution**: Optimize test runs for faster feedback
- **Historical Analysis**: Learn from test history to improve selection

## Tools

### `generate_unit_tests`
Generate comprehensive unit tests for a function.

```json
{
  "function_name": "calculate_total",
  "file_path": "src/calculator.py",
  "framework": "pytest"
}
```

### `analyze_test_coverage`
Analyze test coverage and identify gaps.

```json
{
  "project_path": "/path/to/project",
  "test_command": "pytest tests/"
}
```

### `find_coverage_gaps`
Identify specific areas lacking test coverage.

```json
{
  "project_path": "/path/to/project",
  "threshold": 85.0
}
```

### `detect_flaky_tests`
Detect unreliable tests through multiple runs.

```json
{
  "project_path": "/path/to/project",
  "test_runs": 10
}
```

### `analyze_test_impact`
Determine which tests to run based on changed files.

```json
{
  "changed_files": ["src/main.py", "src/utils.py"],
  "project_path": "/path/to/project"
}
```

## Installation

```bash
cd servers/test-intelligence-mcp
pip install -e .
```

### Optional Dependencies

For enhanced functionality:
```bash
# Mutation testing
pip install mutmut cosmic-ray

# Property-based testing
pip install hypothesis

# Advanced coverage
pip install coverage[toml] pytest-cov
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "test-intelligence": {
      "command": "python",
      "args": ["servers/test-intelligence-mcp/server.py"],
      "cwd": "/path/to/Claude-MCP-tools",
      "keepAlive": true,
      "stderrToConsole": true
    }
  }
}
```

## Usage Examples

### Generate Tests for New Function
```
Generate comprehensive unit tests for the calculate_interest function in src/finance.py, including edge cases and property-based tests.
```

### Coverage Analysis and Gap Identification
```
Analyze test coverage for my project and identify specific functions that need more tests to reach 90% coverage.
```

### Smart Test Execution
```
I've modified src/database.py and src/models.py - which tests should I run to verify these changes?
```

### Flaky Test Detection
```
Some of my tests are failing intermittently. Run them 20 times to identify which ones are flaky.
```

### Test Generation Workflow
```
For each function in src/api.py that has less than 80% coverage, generate comprehensive test cases including error scenarios.
```

## Test Generation Templates

### Unit Test Template
```python
def test_{{ function_name }}_{{ scenario }}():
    """{{ test_description }}"""
    # Arrange
    {{ setup_code }}
    
    # Act
    result = {{ function_name }}({{ test_inputs }})
    
    # Assert
    {{ assertions }}
```

### Property-Based Test Template
```python
from hypothesis import given, strategies as st

@given({{ strategies }})
def test_{{ function_name }}_property({{ parameters }}):
    """Property: {{ property_description }}"""
    result = {{ function_name }}({{ parameters }})
    {{ property_assertions }}
```

### Integration Test Template
```python
def test_{{ function_name }}_integration():
    """Integration test for {{ function_name }}"""
    # Setup dependencies
    {{ dependency_setup }}
    
    # Execute workflow
    result = {{ function_name }}({{ realistic_inputs }})
    
    # Verify outcomes
    {{ comprehensive_assertions }}
```

## Advanced Features

### Intelligent Test Case Generation
- **Type Inference**: Generate appropriate test data based on type hints
- **Complexity Analysis**: More tests for complex functions
- **Dependency Injection**: Mock external dependencies automatically
- **Realistic Data**: Generate meaningful test data, not just placeholders

### Coverage Gap Analysis
```python
# Identify specific uncovered areas
{
  "function": "process_payment",
  "file": "src/payment.py",
  "uncovered_lines": [45, 46, 50-55],
  "gap_type": "exception_handling",
  "suggested_tests": [
    "test_process_payment_invalid_amount",
    "test_process_payment_network_failure"
  ]
}
```

### Test Impact Analysis
- **Change Detection**: Identify modified functions and their dependencies
- **Test Mapping**: Map tests to the code they exercise
- **Selective Execution**: Run only relevant tests for faster feedback
- **Regression Risk**: Assess risk of changes breaking existing functionality

## Quality Metrics

### Coverage Metrics
- **Statement Coverage**: Line-by-line execution tracking
- **Branch Coverage**: Decision point coverage analysis
- **Function Coverage**: Ensure all functions are tested
- **Module Coverage**: File-level coverage tracking

### Test Quality Metrics
- **Test Effectiveness**: Mutation testing scores
- **Test Stability**: Flaky test detection and scoring
- **Test Performance**: Execution time analysis
- **Test Maintainability**: Complexity and duplication analysis

## Integration Patterns

### With Code Analysis MCP
```python
# Workflow: Analyze → Generate Tests → Verify Coverage
1. code_analysis.analyze_code_structure("src/complex.py")
2. test_intelligence.generate_unit_tests("complex_function", "src/complex.py")
3. test_intelligence.analyze_test_coverage("/project")
```

### With Refactoring MCP
```python
# Safe refactoring with test validation
1. test_intelligence.analyze_test_impact(["src/refactor_target.py"])
2. refactoring.extract_method("src/refactor_target.py", 50, 80, "new_method")
3. test_intelligence.generate_unit_tests("new_method", "src/refactor_target.py")
```

### With Code Quality MCP
```python
# Quality-driven development
1. code_quality.detect_code_smells("src/")
2. test_intelligence.find_coverage_gaps("/project", threshold=90)
3. test_intelligence.generate_unit_tests(uncovered_functions)
```

## Configuration Options

### Test Generation Settings
```json
{
  "generation": {
    "include_property_tests": true,
    "include_edge_cases": true,
    "include_exception_tests": true,
    "framework": "pytest",
    "test_data_strategy": "realistic"
  }
}
```

### Coverage Analysis Settings
```json
{
  "coverage": {
    "threshold": 85.0,
    "exclude_patterns": ["**/migrations/**", "**/tests/**"],
    "include_branches": true,
    "show_missing": true
  }
}
```

## Best Practices

1. **Generate tests early** in development process
2. **Use property-based testing** for complex logic
3. **Monitor coverage trends** over time
4. **Run impact analysis** before code changes
5. **Address flaky tests** immediately when detected
6. **Combine multiple test types** for comprehensive coverage

## Performance Optimization

- **Parallel Test Generation**: Generate multiple test files simultaneously
- **Incremental Analysis**: Only analyze changed code
- **Caching**: Cache analysis results for faster repeated operations
- **Smart Scheduling**: Optimize test execution order

Works seamlessly with Code Analysis, Code Quality, and Refactoring MCPs for comprehensive test-driven development workflows.