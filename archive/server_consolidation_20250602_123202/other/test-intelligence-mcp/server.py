#!/usr/bin/env python3
"""
Test Intelligence MCP Server

Provides comprehensive test intelligence capabilities including:
- Automated test generation from code
- Test coverage analysis and gap identification
- Flaky test detection
- Test impact analysis for code changes
- Mutation testing support
"""

import asyncio
import ast
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Add the code-intelligence-core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code-intelligence-core"))

from fastmcp import FastMCP
from pythonjsonlogger import jsonlogger
import aiofiles
from jinja2 import Template
from pydantic import BaseModel

# Import our core framework
try:
    from core import get_core, CodeAnalysis, Symbol
except ImportError as e:
    logging.error(f"Failed to import code intelligence core: {e}")
    sys.exit(1)


# Initialize FastMCP server
mcp = FastMCP("test-intelligence-mcp")

# Get shared core instance
core = get_core()


def setup_logging():
    """Setup structured logging for MCP server"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add stderr handler with JSON formatting
    handler = logging.StreamHandler(sys.stderr)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class TestCase:
    """Represents a generated test case"""
    name: str
    function_name: str
    test_type: str  # "unit", "integration", "property"
    inputs: List[Any]
    expected_output: Any
    test_code: str
    framework: str = "pytest"


@dataclass
class CoverageGap:
    """Represents an area lacking test coverage"""
    file_path: str
    line_start: int
    line_end: int
    function_name: str
    gap_type: str  # "uncovered_lines", "missing_edge_case", "no_tests"
    suggested_tests: List[str]


class TestGenerator:
    """Automated test generation engine"""
    
    def __init__(self):
        self.test_templates = self._load_test_templates()
    
    def _load_test_templates(self) -> Dict[str, Template]:
        """Load Jinja2 templates for test generation"""
        templates = {
            "unit_test": Template("""
def test_{{ function_name }}_{{ test_case_name }}():
    \"\"\"{{ test_description }}\"\"\"
    # Arrange
    {% for param, value in test_inputs.items() %}
    {{ param }} = {{ value | repr }}
    {% endfor %}
    
    # Act
    result = {{ function_name }}({{ test_inputs.keys() | join(', ') }})
    
    # Assert
    {% if expected_exception %}
    with pytest.raises({{ expected_exception }}):
        {{ function_name }}({{ test_inputs.keys() | join(', ') }})
    {% else %}
    assert result == {{ expected_output | repr }}
    {% endif %}
"""),
            
            "property_test": Template("""
from hypothesis import given, strategies as st

@given({{ hypothesis_strategies }})
def test_{{ function_name }}_property_{{ property_name }}({{ parameter_names }}):
    \"\"\"Property-based test: {{ property_description }}\"\"\"
    # Act
    result = {{ function_name }}({{ parameter_names }})
    
    # Assert property
    {{ property_assertion }}
"""),
            
            "integration_test": Template("""
def test_{{ function_name }}_integration():
    \"\"\"Integration test for {{ function_name }}\"\"\"
    # Setup
    {{ setup_code }}
    
    # Act
    result = {{ function_name }}({{ test_inputs }})
    
    # Assert
    {{ assertions }}
    
    # Cleanup
    {{ cleanup_code }}
""")
        }
        return templates
    
    async def analyze_function_for_testing(self, file_path: str, function_name: str) -> Dict[str, Any]:
        """Analyze a function to determine test generation strategy"""
        analysis = await core.analyze_file(file_path)
        
        function_info = None
        for symbol in analysis.symbols:
            if symbol.name == function_name and symbol.kind == "function":
                function_info = symbol
                break
        
        if not function_info:
            return {"error": f"Function {function_name} not found in {file_path}"}
        
        # Read function source code
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        lines = content.split('\n')
        function_source = '\n'.join(lines[function_info.line_start-1:function_info.line_end])
        
        # Parse function to extract information
        try:
            tree = ast.parse(function_source)
            func_node = tree.body[0] if tree.body and isinstance(tree.body[0], ast.FunctionDef) else None
            
            if not func_node:
                return {"error": "Could not parse function"}
            
            # Extract function metadata
            parameters = []
            for arg in func_node.args.args:
                param_info = {
                    "name": arg.arg,
                    "type_hint": None,
                    "default": None
                }
                if arg.annotation:
                    try:
                        param_info["type_hint"] = ast.unparse(arg.annotation)
                    except:
                        param_info["type_hint"] = str(arg.annotation)
                parameters.append(param_info)
            
            # Analyze function complexity and behavior
            complexity_score = self._calculate_function_complexity(func_node)
            has_conditionals = self._has_conditionals(func_node)
            has_loops = self._has_loops(func_node)
            has_exceptions = self._has_exception_handling(func_node)
            
            return {
                "function_name": function_name,
                "parameters": parameters,
                "complexity_score": complexity_score,
                "has_conditionals": has_conditionals,
                "has_loops": has_loops,
                "has_exceptions": has_exceptions,
                "docstring": function_info.docstring,
                "source_code": function_source,
                "line_start": function_info.line_start,
                "line_end": function_info.line_end
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze function: {e}"}
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of function"""
        complexity = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def _has_conditionals(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has conditional statements"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                return True
        return False
    
    def _has_loops(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has loops"""
        for node in ast.walk(func_node):
            if isinstance(node, (ast.For, ast.While)):
                return True
        return False
    
    def _has_exception_handling(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has exception handling"""
        for node in ast.walk(func_node):
            if isinstance(node, (ast.Try, ast.Raise)):
                return True
        return False
    
    async def generate_unit_tests(self, function_info: Dict[str, Any], 
                                framework: str = "pytest") -> List[TestCase]:
        """Generate unit tests for a function"""
        tests = []
        
        function_name = function_info["function_name"]
        parameters = function_info["parameters"]
        
        # Generate basic positive test case
        test_inputs = {}
        for param in parameters:
            test_inputs[param["name"]] = self._generate_test_value(param)
        
        basic_test = TestCase(
            name=f"test_{function_name}_basic",
            function_name=function_name,
            test_type="unit",
            inputs=list(test_inputs.values()),
            expected_output="expected_result",  # Would be inferred or specified
            test_code=self.test_templates["unit_test"].render(
                function_name=function_name,
                test_case_name="basic",
                test_description=f"Test basic functionality of {function_name}",
                test_inputs=test_inputs,
                expected_output="expected_result"
            ),
            framework=framework
        )
        tests.append(basic_test)
        
        # Generate edge case tests
        if function_info.get("has_conditionals"):
            edge_test = TestCase(
                name=f"test_{function_name}_edge_cases",
                function_name=function_name,
                test_type="unit",
                inputs=[],
                expected_output=None,
                test_code=self._generate_edge_case_test(function_info),
                framework=framework
            )
            tests.append(edge_test)
        
        # Generate exception tests
        if function_info.get("has_exceptions"):
            exception_test = TestCase(
                name=f"test_{function_name}_exceptions",
                function_name=function_name,
                test_type="unit",
                inputs=[],
                expected_output=None,
                test_code=self._generate_exception_test(function_info),
                framework=framework
            )
            tests.append(exception_test)
        
        return tests
    
    def _generate_test_value(self, param: Dict[str, Any]) -> Any:
        """Generate appropriate test value for parameter"""
        type_hint = param.get("type_hint", "")
        
        if "int" in type_hint.lower():
            return 42
        elif "str" in type_hint.lower():
            return "test_string"
        elif "float" in type_hint.lower():
            return 3.14
        elif "bool" in type_hint.lower():
            return True
        elif "list" in type_hint.lower():
            return [1, 2, 3]
        elif "dict" in type_hint.lower():
            return {"key": "value"}
        else:
            return "test_value"
    
    def _generate_edge_case_test(self, function_info: Dict[str, Any]) -> str:
        """Generate edge case test code"""
        function_name = function_info["function_name"]
        return f"""
def test_{function_name}_edge_cases():
    \"\"\"Test edge cases for {function_name}\"\"\"
    # Test empty inputs
    # Test boundary values
    # Test null/None inputs
    # Add specific edge case tests based on function logic
    pass
"""
    
    def _generate_exception_test(self, function_info: Dict[str, Any]) -> str:
        """Generate exception handling test code"""
        function_name = function_info["function_name"]
        return f"""
def test_{function_name}_exceptions():
    \"\"\"Test exception handling for {function_name}\"\"\"
    with pytest.raises(ValueError):
        {function_name}(invalid_input)
    
    with pytest.raises(TypeError):
        {function_name}(wrong_type_input)
"""
    
    async def generate_property_tests(self, function_info: Dict[str, Any]) -> List[TestCase]:
        """Generate property-based tests using Hypothesis"""
        tests = []
        
        function_name = function_info["function_name"]
        parameters = function_info["parameters"]
        
        # Generate strategies based on parameter types
        strategies = []
        param_names = []
        
        for param in parameters:
            param_names.append(param["name"])
            type_hint = param.get("type_hint", "")
            
            if "int" in type_hint.lower():
                strategies.append(f"st.integers()")
            elif "str" in type_hint.lower():
                strategies.append(f"st.text()")
            elif "float" in type_hint.lower():
                strategies.append(f"st.floats()")
            else:
                strategies.append(f"st.text()")
        
        if strategies:
            property_test = TestCase(
                name=f"test_{function_name}_property",
                function_name=function_name,
                test_type="property",
                inputs=[],
                expected_output=None,
                test_code=self.test_templates["property_test"].render(
                    function_name=function_name,
                    property_name="invariant",
                    property_description="Function maintains invariant properties",
                    hypothesis_strategies=", ".join(strategies),
                    parameter_names=", ".join(param_names),
                    property_assertion="assert result is not None  # Add specific property assertions"
                ),
                framework="pytest"
            )
            tests.append(property_test)
        
        return tests


class CoverageAnalyzer:
    """Test coverage analysis and gap identification"""
    
    async def analyze_coverage(self, project_path: str, test_command: str = "pytest") -> Dict[str, Any]:
        """Run coverage analysis and return detailed results"""
        try:
            # Run tests with coverage
            process = await asyncio.create_subprocess_exec(
                "coverage", "run", "--source=.", "-m", "pytest",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": "Test execution failed",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
            
            # Generate coverage report
            report_process = await asyncio.create_subprocess_exec(
                "coverage", "report", "--format=json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )
            
            report_stdout, report_stderr = await report_process.communicate()
            
            if report_process.returncode == 0 and report_stdout:
                coverage_data = json.loads(report_stdout.decode())
                
                # Analyze gaps
                gaps = await self._identify_coverage_gaps(coverage_data, project_path)
                
                return {
                    "success": True,
                    "coverage_data": coverage_data,
                    "coverage_gaps": gaps,
                    "summary": self._create_coverage_summary(coverage_data)
                }
            else:
                return {
                    "success": False,
                    "error": "Coverage report generation failed",
                    "stderr": report_stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _identify_coverage_gaps(self, coverage_data: Dict[str, Any], 
                                    project_path: str) -> List[CoverageGap]:
        """Identify specific areas lacking coverage"""
        gaps = []
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            if file_data.get("summary", {}).get("percent_covered", 100) < 100:
                missing_lines = file_data.get("missing_lines", [])
                
                if missing_lines:
                    # Analyze functions containing missing lines
                    full_path = os.path.join(project_path, file_path)
                    if os.path.exists(full_path):
                        analysis = await core.analyze_file(full_path)
                        
                        for symbol in analysis.symbols:
                            if symbol.kind == "function":
                                function_missing_lines = [
                                    line for line in missing_lines
                                    if symbol.line_start <= line <= symbol.line_end
                                ]
                                
                                if function_missing_lines:
                                    gap = CoverageGap(
                                        file_path=file_path,
                                        line_start=min(function_missing_lines),
                                        line_end=max(function_missing_lines),
                                        function_name=symbol.name,
                                        gap_type="uncovered_lines",
                                        suggested_tests=[
                                            f"test_{symbol.name}_missing_path",
                                            f"test_{symbol.name}_edge_case"
                                        ]
                                    )
                                    gaps.append(gap)
        
        return gaps
    
    def _create_coverage_summary(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of coverage data"""
        totals = coverage_data.get("totals", {})
        
        return {
            "total_statements": totals.get("num_statements", 0),
            "covered_statements": totals.get("covered_lines", 0),
            "missing_statements": totals.get("missing_lines", 0),
            "percent_covered": totals.get("percent_covered", 0),
            "files_analyzed": len(coverage_data.get("files", {}))
        }


class TestAnalyzer:
    """Test suite analysis and optimization"""
    
    async def detect_flaky_tests(self, project_path: str, runs: int = 10) -> Dict[str, Any]:
        """Detect flaky tests by running them multiple times"""
        try:
            results = []
            
            for run in range(runs):
                process = await asyncio.create_subprocess_exec(
                    "pytest", "--tb=short", "-v",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=project_path
                )
                
                stdout, stderr = await process.communicate()
                
                results.append({
                    "run": run + 1,
                    "returncode": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                })
            
            # Analyze results for flakiness
            flaky_tests = self._analyze_test_consistency(results)
            
            return {
                "success": True,
                "total_runs": runs,
                "flaky_tests": flaky_tests,
                "consistency_score": self._calculate_consistency_score(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_test_consistency(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze test results for consistency"""
        # This is a simplified implementation
        # In practice, would parse test output and track individual test results
        
        flaky_tests = []
        failed_runs = sum(1 for r in results if r["returncode"] != 0)
        
        if 0 < failed_runs < len(results):
            flaky_tests.append({
                "test_pattern": "intermittent_failures",
                "failure_rate": failed_runs / len(results),
                "description": f"Tests failed in {failed_runs} out of {len(results)} runs"
            })
        
        return flaky_tests
    
    def _calculate_consistency_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate overall test consistency score"""
        consistent_runs = sum(1 for r in results if r["returncode"] == 0)
        return consistent_runs / len(results) * 100


# Initialize components
test_generator = TestGenerator()
coverage_analyzer = CoverageAnalyzer()
test_analyzer = TestAnalyzer()


@mcp.tool()
async def generate_unit_tests(function_name: str, file_path: str, 
                             framework: str = "pytest") -> Dict[str, Any]:
    """
    Generate unit tests for a specific function.
    
    Args:
        function_name: Name of the function to test
        file_path: Path to file containing the function
        framework: Testing framework to use (pytest, unittest)
    
    Returns:
        Dictionary containing generated test cases
    """
    try:
        logging.info(f"Generating unit tests for {function_name} in {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Analyze function for test generation
        function_info = await test_generator.analyze_function_for_testing(file_path, function_name)
        
        if "error" in function_info:
            return {
                "success": False,
                "error": function_info["error"]
            }
        
        # Generate unit tests
        unit_tests = await test_generator.generate_unit_tests(function_info, framework)
        
        # Generate property-based tests if applicable
        property_tests = await test_generator.generate_property_tests(function_info)
        
        all_tests = unit_tests + property_tests
        
        return {
            "success": True,
            "function_name": function_name,
            "file_path": file_path,
            "framework": framework,
            "function_analysis": function_info,
            "generated_tests": [
                {
                    "name": test.name,
                    "type": test.test_type,
                    "code": test.test_code
                }
                for test in all_tests
            ],
            "total_tests": len(all_tests)
        }
        
    except Exception as e:
        logging.error(f"Test generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "function_name": function_name
        }


@mcp.tool()
async def analyze_test_coverage(project_path: str, test_command: str = "pytest") -> Dict[str, Any]:
    """
    Analyze test coverage and identify gaps.
    
    Args:
        project_path: Root path of the project
        test_command: Command to run tests
    
    Returns:
        Dictionary containing coverage analysis and gaps
    """
    try:
        logging.info(f"Analyzing test coverage for project: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        result = await coverage_analyzer.analyze_coverage(project_path, test_command)
        
        return result
        
    except Exception as e:
        logging.error(f"Coverage analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def find_coverage_gaps(project_path: str, threshold: float = 80.0) -> Dict[str, Any]:
    """
    Identify specific areas lacking test coverage.
    
    Args:
        project_path: Root path of the project
        threshold: Coverage threshold percentage
    
    Returns:
        Dictionary containing identified coverage gaps and suggestions
    """
    try:
        logging.info(f"Finding coverage gaps in: {project_path}")
        
        coverage_result = await coverage_analyzer.analyze_coverage(project_path)
        
        if not coverage_result["success"]:
            return coverage_result
        
        gaps = coverage_result["coverage_gaps"]
        summary = coverage_result["summary"]
        
        # Filter gaps based on threshold
        significant_gaps = [
            gap for gap in gaps
            if gap.gap_type in ["uncovered_lines", "no_tests"]
        ]
        
        recommendations = []
        for gap in significant_gaps:
            recommendations.extend([
                f"Add tests for {gap.function_name} in {gap.file_path}:{gap.line_start}-{gap.line_end}",
                f"Consider edge case testing for {gap.function_name}"
            ])
        
        return {
            "success": True,
            "project_path": project_path,
            "threshold": threshold,
            "meets_threshold": summary["percent_covered"] >= threshold,
            "current_coverage": summary["percent_covered"],
            "coverage_gaps": [
                {
                    "file": gap.file_path,
                    "function": gap.function_name,
                    "lines": f"{gap.line_start}-{gap.line_end}",
                    "type": gap.gap_type,
                    "suggested_tests": gap.suggested_tests
                }
                for gap in significant_gaps
            ],
            "recommendations": recommendations,
            "summary": summary
        }
        
    except Exception as e:
        logging.error(f"Coverage gap analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def detect_flaky_tests(project_path: str, test_runs: int = 5) -> Dict[str, Any]:
    """
    Detect flaky tests by running test suite multiple times.
    
    Args:
        project_path: Root path of the project
        test_runs: Number of test runs to perform
    
    Returns:
        Dictionary containing flaky test analysis
    """
    try:
        logging.info(f"Detecting flaky tests in: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        result = await test_analyzer.detect_flaky_tests(project_path, test_runs)
        
        return result
        
    except Exception as e:
        logging.error(f"Flaky test detection failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


@mcp.tool()
async def analyze_test_impact(changed_files: List[str], project_path: str) -> Dict[str, Any]:
    """
    Analyze which tests should be run based on changed files.
    
    Args:
        changed_files: List of files that have been modified
        project_path: Root path of the project
    
    Returns:
        Dictionary containing test impact analysis
    """
    try:
        logging.info(f"Analyzing test impact for {len(changed_files)} changed files")
        
        impacted_tests = []
        analysis_details = {}
        
        for file_path in changed_files:
            if not os.path.exists(file_path):
                continue
            
            # Analyze the changed file
            analysis = await core.analyze_file(file_path)
            
            # Find related test files
            test_files = await self._find_related_test_files(file_path, project_path)
            
            # Analyze dependencies
            dependent_files = await self._find_dependent_files(file_path, project_path)
            
            analysis_details[file_path] = {
                "symbols_changed": len(analysis.symbols),
                "related_test_files": test_files,
                "dependent_files": dependent_files
            }
            
            impacted_tests.extend(test_files)
        
        # Remove duplicates
        impacted_tests = list(set(impacted_tests))
        
        return {
            "success": True,
            "changed_files": changed_files,
            "impacted_test_files": impacted_tests,
            "total_impacted_tests": len(impacted_tests),
            "analysis_details": analysis_details,
            "recommended_test_command": f"pytest {' '.join(impacted_tests)}" if impacted_tests else "pytest"
        }
        
    except Exception as e:
        logging.error(f"Test impact analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "changed_files": changed_files
        }

    async def _find_related_test_files(self, file_path: str, project_path: str) -> List[str]:
        """Find test files related to a source file"""
        test_files = []
        
        # Common test file patterns
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        test_patterns = [
            f"test_{base_name}.py",
            f"{base_name}_test.py",
            f"test_{base_name}s.py"
        ]
        
        # Search for test files
        for root, dirs, files in os.walk(project_path):
            if "test" in root.lower() or any(d.startswith("test") for d in root.split(os.sep)):
                for file in files:
                    if any(pattern in file for pattern in test_patterns):
                        test_files.append(os.path.join(root, file))
        
        return test_files
    
    async def _find_dependent_files(self, file_path: str, project_path: str) -> List[str]:
        """Find files that depend on the changed file"""
        dependent_files = []
        
        # This is a simplified implementation
        # In practice, would analyze import statements across the project
        
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    try:
                        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                            content = await f.read()
                        
                        if f"import {module_name}" in content or f"from {module_name}" in content:
                            dependent_files.append(full_path)
                    except:
                        continue
        
        return dependent_files


def main():
    """Main entry point for the MCP server"""
    setup_logging()
    logging.info("Starting Test Intelligence MCP Server")
    
    try:
        # Run the MCP server
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()