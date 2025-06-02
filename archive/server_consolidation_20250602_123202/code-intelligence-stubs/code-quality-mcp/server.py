#!/usr/bin/env python3
"""
Code Quality MCP Server

Provides comprehensive code quality analysis including:
- Linting with multiple tools (pylint, flake8, mypy)
- Code formatting (black, isort, autopep8)
- Style guide enforcement
- Documentation coverage analysis
- Auto-fix capabilities
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from fastmcp import FastMCP
from pythonjsonlogger import jsonlogger
import aiofiles


# Initialize FastMCP server
mcp = FastMCP("code-quality-mcp")


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


class CodeQualityAnalyzer:
    """Unified interface for code quality tools"""
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript'
        }
    
    async def run_command(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Run a shell command and return structured result"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "command": ' '.join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(command)
            }
    
    def detect_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        return self.supported_languages.get(ext, 'unknown')
    
    async def lint_python_file(self, file_path: str, tools: List[str], auto_fix: bool = False) -> Dict[str, Any]:
        """Lint Python file with specified tools"""
        results = {}
        
        for tool in tools:
            if tool == "flake8":
                result = await self.run_command(["flake8", "--format=json", file_path])
                if result["success"] and result["stdout"]:
                    try:
                        issues = json.loads(result["stdout"])
                        results["flake8"] = {
                            "issues": issues,
                            "total_issues": len(issues)
                        }
                    except json.JSONDecodeError:
                        results["flake8"] = {
                            "issues": [],
                            "raw_output": result["stdout"]
                        }
                else:
                    results["flake8"] = {"issues": [], "error": result.get("stderr", "")}
            
            elif tool == "pylint":
                result = await self.run_command(["pylint", "--output-format=json", file_path])
                if result["stdout"]:
                    try:
                        issues = json.loads(result["stdout"])
                        results["pylint"] = {
                            "issues": issues,
                            "total_issues": len(issues)
                        }
                    except json.JSONDecodeError:
                        results["pylint"] = {
                            "issues": [],
                            "raw_output": result["stdout"]
                        }
                else:
                    results["pylint"] = {"issues": []}
            
            elif tool == "mypy":
                result = await self.run_command(["mypy", "--show-error-codes", "--no-error-summary", file_path])
                issues = []
                if result["stdout"]:
                    for line in result["stdout"].split('\n'):
                        if line.strip() and ':' in line:
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                issues.append({
                                    "file": parts[0],
                                    "line": int(parts[1]) if parts[1].isdigit() else 0,
                                    "level": parts[2].strip(),
                                    "message": parts[3].strip()
                                })
                results["mypy"] = {
                    "issues": issues,
                    "total_issues": len(issues)
                }
        
        # Auto-fix if requested
        if auto_fix:
            await self.auto_fix_python_file(file_path)
        
        return results
    
    async def auto_fix_python_file(self, file_path: str) -> Dict[str, Any]:
        """Auto-fix Python file using formatters"""
        fixes_applied = []
        
        # Apply autopep8 for PEP 8 fixes
        result = await self.run_command(["autopep8", "--in-place", "--aggressive", file_path])
        if result["success"]:
            fixes_applied.append("autopep8")
        
        # Apply black for formatting
        result = await self.run_command(["black", file_path])
        if result["success"]:
            fixes_applied.append("black")
        
        # Apply isort for import sorting
        result = await self.run_command(["isort", file_path])
        if result["success"]:
            fixes_applied.append("isort")
        
        return {
            "fixes_applied": fixes_applied,
            "success": len(fixes_applied) > 0
        }
    
    async def format_python_code(self, content: str, formatter: str = "black") -> Dict[str, Any]:
        """Format Python code content"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            if formatter == "black":
                result = await self.run_command(["black", "--code", content])
                formatted_content = result["stdout"] if result["success"] else content
            elif formatter == "autopep8":
                result = await self.run_command(["autopep8", "-"])
                # For autopep8, we need to pass content via stdin
                formatted_content = content  # Simplified for now
            else:
                formatted_content = content
            
            os.unlink(temp_file)
            
            return {
                "success": True,
                "original_content": content,
                "formatted_content": formatted_content,
                "formatter": formatter
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_content": content
            }
    
    async def check_documentation_coverage(self, directory: str) -> Dict[str, Any]:
        """Check documentation coverage for Python files"""
        coverage_data = {
            "files_analyzed": 0,
            "documented_functions": 0,
            "total_functions": 0,
            "documented_classes": 0,
            "total_classes": 0,
            "files_with_issues": []
        }
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_analysis = await self.analyze_file_documentation(file_path)
                    
                    coverage_data["files_analyzed"] += 1
                    coverage_data["documented_functions"] += file_analysis["documented_functions"]
                    coverage_data["total_functions"] += file_analysis["total_functions"]
                    coverage_data["documented_classes"] += file_analysis["documented_classes"]
                    coverage_data["total_classes"] += file_analysis["total_classes"]
                    
                    if file_analysis["issues"]:
                        coverage_data["files_with_issues"].append({
                            "file": file_path,
                            "issues": file_analysis["issues"]
                        })
        
        # Calculate percentages
        coverage_data["function_coverage"] = (
            coverage_data["documented_functions"] / coverage_data["total_functions"] * 100
            if coverage_data["total_functions"] > 0 else 100
        )
        coverage_data["class_coverage"] = (
            coverage_data["documented_classes"] / coverage_data["total_classes"] * 100
            if coverage_data["total_classes"] > 0 else 100
        )
        
        return coverage_data
    
    async def analyze_file_documentation(self, file_path: str) -> Dict[str, Any]:
        """Analyze documentation coverage for a single file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            import ast
            tree = ast.parse(content)
            
            analysis = {
                "total_functions": 0,
                "documented_functions": 0,
                "total_classes": 0,
                "documented_classes": 0,
                "issues": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["total_functions"] += 1
                    if ast.get_docstring(node):
                        analysis["documented_functions"] += 1
                    else:
                        analysis["issues"].append({
                            "type": "missing_function_docstring",
                            "function": node.name,
                            "line": node.lineno
                        })
                
                elif isinstance(node, ast.ClassDef):
                    analysis["total_classes"] += 1
                    if ast.get_docstring(node):
                        analysis["documented_classes"] += 1
                    else:
                        analysis["issues"].append({
                            "type": "missing_class_docstring",
                            "class": node.name,
                            "line": node.lineno
                        })
            
            return analysis
        except Exception as e:
            return {
                "total_functions": 0,
                "documented_functions": 0,
                "total_classes": 0,
                "documented_classes": 0,
                "issues": [{"error": str(e)}]
            }


# Initialize analyzer
analyzer = CodeQualityAnalyzer()


@mcp.tool()
async def lint_code(file_path: str, ruleset: Optional[str] = None, auto_fix: bool = False, tools: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Lint code file with specified tools and optionally apply auto-fixes.
    
    Args:
        file_path: Path to the file to lint
        ruleset: Optional ruleset configuration (e.g., "pep8", "google", "custom")
        auto_fix: Whether to automatically fix issues
        tools: List of linting tools to use (e.g., ["flake8", "pylint", "mypy"])
    
    Returns:
        Dictionary containing linting results and any applied fixes
    """
    try:
        logging.info(f"Linting file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        language = analyzer.detect_language(file_path)
        
        if language == "python":
            default_tools = tools or ["flake8", "pylint", "mypy"]
            results = await analyzer.lint_python_file(file_path, default_tools, auto_fix)
            
            return {
                "success": True,
                "file_path": file_path,
                "language": language,
                "ruleset": ruleset,
                "auto_fix": auto_fix,
                "tools_used": default_tools,
                "results": results
            }
        else:
            return {
                "success": False,
                "error": f"Linting not yet supported for {language} files"
            }
    
    except Exception as e:
        logging.error(f"Linting failed for {file_path}: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@mcp.tool()
async def format_code(file_path: str, style_guide: Optional[str] = None, formatter: Optional[str] = None) -> Dict[str, Any]:
    """
    Format code file according to style guide.
    
    Args:
        file_path: Path to the file to format
        style_guide: Style guide to follow (e.g., "pep8", "google", "black")
        formatter: Specific formatter to use (e.g., "black", "autopep8")
    
    Returns:
        Dictionary containing formatting results and changes made
    """
    try:
        logging.info(f"Formatting file: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        language = analyzer.detect_language(file_path)
        
        if language == "python":
            # Read original content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                original_content = await f.read()
            
            formatter = formatter or "black"
            result = await analyzer.format_python_code(original_content, formatter)
            
            if result["success"] and auto_fix:
                # Write formatted content back to file
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(result["formatted_content"])
            
            return {
                "success": True,
                "file_path": file_path,
                "language": language,
                "style_guide": style_guide,
                "formatter": formatter,
                "changes_made": result["formatted_content"] != original_content,
                "result": result
            }
        else:
            return {
                "success": False,
                "error": f"Formatting not yet supported for {language} files"
            }
    
    except Exception as e:
        logging.error(f"Formatting failed for {file_path}: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@mcp.tool()
async def check_documentation_coverage(directory: str, threshold: Optional[float] = None) -> Dict[str, Any]:
    """
    Check documentation coverage for code in a directory.
    
    Args:
        directory: Directory to analyze
        threshold: Minimum coverage threshold (0-100)
    
    Returns:
        Dictionary containing documentation coverage analysis
    """
    try:
        logging.info(f"Checking documentation coverage: {directory}")
        
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        coverage = await analyzer.check_documentation_coverage(directory)
        
        # Check against threshold
        threshold = threshold or 80.0
        overall_coverage = (coverage["function_coverage"] + coverage["class_coverage"]) / 2
        meets_threshold = overall_coverage >= threshold
        
        return {
            "success": True,
            "directory": directory,
            "threshold": threshold,
            "meets_threshold": meets_threshold,
            "overall_coverage": overall_coverage,
            "coverage": coverage
        }
    
    except Exception as e:
        logging.error(f"Documentation coverage check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "directory": directory
        }


@mcp.tool()
async def analyze_test_coverage(test_command: str, project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze test coverage by running tests with coverage measurement.
    
    Args:
        test_command: Command to run tests (e.g., "pytest", "python -m pytest")
        project_path: Optional project root path
    
    Returns:
        Dictionary containing test coverage analysis
    """
    try:
        logging.info(f"Analyzing test coverage with command: {test_command}")
        
        cwd = project_path or os.getcwd()
        
        # Run tests with coverage
        coverage_command = ["coverage", "run", "--source=.", "-m"] + test_command.split()[1:]
        if test_command.startswith("python"):
            coverage_command = ["coverage", "run", "--source=."] + test_command.split()
        
        result = await analyzer.run_command(coverage_command, cwd=cwd)
        
        if not result["success"]:
            return {
                "success": False,
                "error": "Test execution failed",
                "details": result
            }
        
        # Generate coverage report
        report_result = await analyzer.run_command(["coverage", "report", "--format=json"], cwd=cwd)
        
        if report_result["success"] and report_result["stdout"]:
            try:
                coverage_data = json.loads(report_result["stdout"])
                return {
                    "success": True,
                    "test_command": test_command,
                    "project_path": cwd,
                    "coverage": coverage_data
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback to text report
        text_report = await analyzer.run_command(["coverage", "report"], cwd=cwd)
        
        return {
            "success": True,
            "test_command": test_command,
            "project_path": cwd,
            "coverage_report": text_report["stdout"] if text_report["success"] else "Coverage report generation failed"
        }
    
    except Exception as e:
        logging.error(f"Test coverage analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "test_command": test_command
        }


@mcp.tool()
async def enforce_style_guide(style_config: Dict[str, Any], directory: str, apply_fixes: bool = False) -> Dict[str, Any]:
    """
    Enforce style guide across a directory of files.
    
    Args:
        style_config: Configuration for style enforcement
        directory: Directory to process
        apply_fixes: Whether to automatically apply fixes
    
    Returns:
        Dictionary containing style enforcement results
    """
    try:
        logging.info(f"Enforcing style guide in: {directory}")
        
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        results = {
            "files_processed": 0,
            "files_with_violations": 0,
            "total_violations": 0,
            "files_fixed": 0,
            "violations_by_file": {}
        }
        
        # Process all Python files in directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    results["files_processed"] += 1
                    
                    # Lint the file
                    lint_result = await lint_code(file_path, auto_fix=apply_fixes)
                    
                    if lint_result["success"]:
                        file_violations = 0
                        for tool, tool_result in lint_result["results"].items():
                            if "total_issues" in tool_result:
                                file_violations += tool_result["total_issues"]
                        
                        if file_violations > 0:
                            results["files_with_violations"] += 1
                            results["total_violations"] += file_violations
                            results["violations_by_file"][file_path] = file_violations
                        
                        if apply_fixes and file_violations > 0:
                            results["files_fixed"] += 1
        
        return {
            "success": True,
            "directory": directory,
            "style_config": style_config,
            "apply_fixes": apply_fixes,
            "results": results
        }
    
    except Exception as e:
        logging.error(f"Style guide enforcement failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "directory": directory
        }


def main():
    """Main entry point for the MCP server"""
    setup_logging()
    logging.info("Starting Code Quality MCP Server")
    
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