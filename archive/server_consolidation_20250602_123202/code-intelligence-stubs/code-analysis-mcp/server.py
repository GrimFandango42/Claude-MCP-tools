#!/usr/bin/env python3
"""
Code Analysis MCP Server

Provides semantic code analysis capabilities including:
- AST parsing and symbol extraction
- Type inference and resolution
- Code complexity analysis
- Symbol reference finding
- Import/export analysis
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the code-intelligence-core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code-intelligence-core"))

from fastmcp import FastMCP
from pythonjsonlogger import jsonlogger

# Import our core framework
try:
    from core import get_core, CodeAnalysis, Symbol, LanguageType
except ImportError as e:
    logging.error(f"Failed to import code intelligence core: {e}")
    sys.exit(1)


# Initialize FastMCP server
mcp = FastMCP("code-analysis-mcp")

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


@mcp.tool()
async def analyze_code_structure(file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze code structure and return comprehensive information about symbols, imports, and complexity.
    
    Args:
        file_path: Path to the file to analyze
        language: Optional language hint (python, javascript, typescript)
    
    Returns:
        Dictionary containing symbols, imports, exports, complexity metrics, and dependencies
    """
    try:
        logging.info(f"Analyzing code structure for: {file_path}")
        
        # Validate file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "file_path": file_path
            }
        
        # Perform analysis
        analysis: CodeAnalysis = await core.analyze_file(file_path)
        
        # Convert to serializable format
        result = analysis.to_dict()
        result["success"] = True
        
        logging.info(f"Analysis completed for {file_path}: {len(analysis.symbols)} symbols found")
        return result
        
    except Exception as e:
        logging.error(f"Code analysis failed for {file_path}: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@mcp.tool()
async def find_symbol_references(symbol_name: str, project_path: str, scope: Optional[str] = None) -> Dict[str, Any]:
    """
    Find all references to a symbol across the project.
    
    Args:
        symbol_name: Name of the symbol to search for
        project_path: Root path of the project to search
        scope: Optional scope filter (module, class, function)
    
    Returns:
        Dictionary containing all references with file paths, line numbers, and context
    """
    try:
        logging.info(f"Finding references for symbol '{symbol_name}' in {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        references = await core.find_symbol_references(symbol_name, project_path)
        
        return {
            "success": True,
            "symbol_name": symbol_name,
            "project_path": project_path,
            "scope": scope,
            "references": references,
            "total_references": len(references)
        }
        
    except Exception as e:
        logging.error(f"Symbol reference search failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "symbol_name": symbol_name
        }


@mcp.tool()
async def get_type_info(file_path: str, line: int, column: int) -> Dict[str, Any]:
    """
    Get type information for an expression at a specific location.
    
    Args:
        file_path: Path to the file
        line: Line number (1-based)
        column: Column number (0-based)
    
    Returns:
        Dictionary containing type information and documentation
    """
    try:
        logging.info(f"Getting type info for {file_path}:{line}:{column}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # For Python files, use Jedi for type inference
        if file_path.endswith('.py'):
            import jedi
            
            with open(file_path, 'r') as f:
                source = f.read()
            
            script = jedi.Script(code=source, path=file_path)
            definitions = script.infer(line=line, column=column)
            
            type_info = []
            for definition in definitions:
                type_info.append({
                    "name": definition.name,
                    "type": getattr(definition, 'type', None),
                    "description": definition.description if hasattr(definition, 'description') else None,
                    "docstring": definition.docstring() if hasattr(definition, 'docstring') else None
                })
            
            return {
                "success": True,
                "file_path": file_path,
                "line": line,
                "column": column,
                "type_info": type_info
            }
        else:
            return {
                "success": False,
                "error": f"Type inference not yet supported for {file_path}"
            }
            
    except Exception as e:
        logging.error(f"Type info lookup failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "line": line,
            "column": column
        }


@mcp.tool()
async def detect_code_smells(directory_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Detect code smells and potential issues in a directory.
    
    Args:
        directory_path: Path to directory to analyze
        language: Optional language filter (python, javascript, typescript)
    
    Returns:
        Dictionary containing detected code smells grouped by file and type
    """
    try:
        logging.info(f"Detecting code smells in: {directory_path}")
        
        if not os.path.exists(directory_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }
        
        code_smells = {
            "files_analyzed": 0,
            "total_smells": 0,
            "smells_by_type": {},
            "files_with_smells": {}
        }
        
        # Walk through directory and analyze files
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    file_path = os.path.join(root, file)
                    analysis = await core.analyze_file(file_path)
                    code_smells["files_analyzed"] += 1
                    
                    # Detect smells based on complexity and patterns
                    file_smells = []
                    
                    # High complexity functions
                    for symbol in analysis.symbols:
                        if symbol.kind == "function":
                            # Simulate complexity check (would be more sophisticated)
                            if (symbol.line_end - symbol.line_start) > 50:
                                file_smells.append({
                                    "type": "long_function",
                                    "symbol": symbol.name,
                                    "line": symbol.line_start,
                                    "message": f"Function '{symbol.name}' is too long ({symbol.line_end - symbol.line_start} lines)"
                                })
                    
                    # Too many dependencies
                    if len(analysis.dependencies) > 10:
                        file_smells.append({
                            "type": "too_many_dependencies",
                            "line": 1,
                            "message": f"File has too many dependencies ({len(analysis.dependencies)})"
                        })
                    
                    if file_smells:
                        code_smells["files_with_smells"][file_path] = file_smells
                        code_smells["total_smells"] += len(file_smells)
                        
                        for smell in file_smells:
                            smell_type = smell["type"]
                            if smell_type not in code_smells["smells_by_type"]:
                                code_smells["smells_by_type"][smell_type] = 0
                            code_smells["smells_by_type"][smell_type] += 1
        
        return {
            "success": True,
            "directory_path": directory_path,
            "language": language,
            "analysis": code_smells
        }
        
    except Exception as e:
        logging.error(f"Code smell detection failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "directory_path": directory_path
        }


@mcp.tool()
async def calculate_complexity_metrics(file_path: str) -> Dict[str, Any]:
    """
    Calculate detailed complexity metrics for a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        Dictionary containing various complexity metrics
    """
    try:
        logging.info(f"Calculating complexity metrics for: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        analysis = await core.analyze_file(file_path)
        
        # Enhanced complexity metrics
        metrics = analysis.complexity_metrics.copy()
        
        # Add per-function complexity
        function_complexities = []
        for symbol in analysis.symbols:
            if symbol.kind == "function":
                function_complexities.append({
                    "function": symbol.name,
                    "lines": symbol.line_end - symbol.line_start + 1,
                    "estimated_complexity": max(1, (symbol.line_end - symbol.line_start) // 10)
                })
        
        metrics["function_complexities"] = function_complexities
        metrics["average_function_length"] = (
            sum(f["lines"] for f in function_complexities) / len(function_complexities)
            if function_complexities else 0
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "metrics": metrics
        }
        
    except Exception as e:
        logging.error(f"Complexity calculation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@mcp.tool()
async def analyze_project_dependencies(project_path: str) -> Dict[str, Any]:
    """
    Analyze all dependencies across a project.
    
    Args:
        project_path: Root path of the project
    
    Returns:
        Dictionary containing dependency analysis across all files
    """
    try:
        logging.info(f"Analyzing project dependencies: {project_path}")
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"Project path not found: {project_path}"
            }
        
        dependencies = await core.get_project_dependencies(project_path)
        
        return {
            "success": True,
            "project_path": project_path,
            "dependencies": dependencies
        }
        
    except Exception as e:
        logging.error(f"Project dependency analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_path": project_path
        }


def main():
    """Main entry point for the MCP server"""
    setup_logging()
    logging.info("Starting Code Analysis MCP Server")
    
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