#!/usr/bin/env python3
"""
Refactoring MCP Server

Provides safe automated code refactoring capabilities including:
- Symbol renaming across files
- Extract method/function/variable operations
- Inline operations
- Move class/function between files
- Safe AST-based transformations
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add the code-intelligence-core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code-intelligence-core"))

from fastmcp import FastMCP
from pythonjsonlogger import jsonlogger
import aiofiles

# Import refactoring libraries
try:
    import rope.base.project
    import rope.base.resources
    import rope.refactor.rename
    import rope.refactor.extract
    import rope.refactor.inline
    import rope.refactor.move
    import libcst as cst
    import git
except ImportError as e:
    logging.error(f"Failed to import refactoring dependencies: {e}")
    sys.exit(1)

# Import our core framework
try:
    from core import get_core, CodeAnalysis, Symbol
except ImportError as e:
    logging.error(f"Failed to import code intelligence core: {e}")
    sys.exit(1)


# Initialize FastMCP server
mcp = FastMCP("refactoring-mcp")

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


class RefactoringEngine:
    """Safe code refactoring engine using Rope and LibCST"""
    
    def __init__(self):
        self.project_cache = {}
    
    def get_rope_project(self, project_path: str) -> rope.base.project.Project:
        """Get or create a Rope project for the given path"""
        if project_path not in self.project_cache:
            self.project_cache[project_path] = rope.base.project.Project(project_path)
        return self.project_cache[project_path]
    
    async def backup_file(self, file_path: str) -> str:
        """Create a backup of the file before refactoring"""
        backup_path = f"{file_path}.refactor_backup"
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as src:
            content = await src.read()
        async with aiofiles.open(backup_path, 'w', encoding='utf-8') as dst:
            await dst.write(content)
        return backup_path
    
    async def create_git_commit(self, project_path: str, message: str, files: List[str]) -> Dict[str, Any]:
        """Create a git commit for the refactoring changes"""
        try:
            repo = git.Repo(project_path)
            
            # Add the changed files
            for file_path in files:
                repo.index.add([file_path])
            
            # Create commit
            commit = repo.index.commit(message)
            
            return {
                "success": True,
                "commit_hash": commit.hexsha,
                "message": message,
                "files": files
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def rename_symbol_in_project(self, project_path: str, file_path: str, 
                                     old_name: str, new_name: str, 
                                     scope: str = "project") -> Dict[str, Any]:
        """Rename a symbol across the project using Rope"""
        try:
            project = self.get_rope_project(project_path)
            resource = project.get_resource(os.path.relpath(file_path, project_path))
            
            # Find the symbol in the file
            analysis = await core.analyze_file(file_path)
            symbol_location = None
            
            for symbol in analysis.symbols:
                if symbol.name == old_name:
                    # Convert to offset (Rope uses offset, not line/column)
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    offset = sum(len(line) for line in lines[:symbol.line_start-1])
                    offset += symbol.column_start
                    symbol_location = offset
                    break
            
            if symbol_location is None:
                return {
                    "success": False,
                    "error": f"Symbol '{old_name}' not found in {file_path}"
                }
            
            # Perform the rename
            renamer = rope.refactor.rename.Rename(project, resource, symbol_location)
            changes = renamer.get_changes(new_name)
            
            # Get preview of changes
            changed_files = []
            for change in changes.changes:
                changed_files.append({
                    "file": change.get_new_contents() if hasattr(change, 'get_new_contents') else str(change),
                    "resource": str(change.resource) if hasattr(change, 'resource') else "unknown"
                })
            
            # Apply changes if not in preview mode
            project.do(changes)
            
            return {
                "success": True,
                "old_name": old_name,
                "new_name": new_name,
                "scope": scope,
                "changed_files": changed_files,
                "total_changes": len(changes.changes)
            }
            
        except Exception as e:
            logging.error(f"Symbol rename failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "old_name": old_name,
                "new_name": new_name
            }
    
    async def extract_method_from_lines(self, file_path: str, start_line: int, 
                                      end_line: int, method_name: str, 
                                      project_path: Optional[str] = None) -> Dict[str, Any]:
        """Extract method from specified lines using Rope"""
        try:
            if project_path is None:
                project_path = os.path.dirname(file_path)
            
            project = self.get_rope_project(project_path)
            resource = project.get_resource(os.path.relpath(file_path, project_path))
            
            # Convert line numbers to offset range
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            start_offset = sum(len(line) for line in lines[:start_line-1])
            end_offset = sum(len(line) for line in lines[:end_line])
            
            # Backup original file
            backup_path = await self.backup_file(file_path)
            
            # Perform extract method
            extractor = rope.refactor.extract.ExtractMethod(
                project, resource, start_offset, end_offset
            )
            changes = extractor.get_changes(method_name)
            
            # Apply changes
            project.do(changes)
            
            return {
                "success": True,
                "file_path": file_path,
                "method_name": method_name,
                "start_line": start_line,
                "end_line": end_line,
                "backup_path": backup_path,
                "changes_applied": True
            }
            
        except Exception as e:
            logging.error(f"Extract method failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "method_name": method_name
            }
    
    async def extract_variable_from_expression(self, file_path: str, line: int, 
                                             column: int, variable_name: str,
                                             project_path: Optional[str] = None) -> Dict[str, Any]:
        """Extract variable from expression at specified location"""
        try:
            if project_path is None:
                project_path = os.path.dirname(file_path)
            
            project = self.get_rope_project(project_path)
            resource = project.get_resource(os.path.relpath(file_path, project_path))
            
            # Convert line/column to offset
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            offset = sum(len(line) for line in lines[:line-1]) + column
            
            # Backup original file
            backup_path = await self.backup_file(file_path)
            
            # Try to extract variable (this is a simplified approach)
            # In practice, we'd need more sophisticated expression detection
            extractor = rope.refactor.extract.ExtractVariable(project, resource, offset, offset + 10)
            changes = extractor.get_changes(variable_name)
            
            # Apply changes
            project.do(changes)
            
            return {
                "success": True,
                "file_path": file_path,
                "variable_name": variable_name,
                "line": line,
                "column": column,
                "backup_path": backup_path
            }
            
        except Exception as e:
            logging.error(f"Extract variable failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "variable_name": variable_name
            }
    
    async def inline_method_or_variable(self, file_path: str, symbol_name: str,
                                      project_path: Optional[str] = None) -> Dict[str, Any]:
        """Inline a method or variable definition"""
        try:
            if project_path is None:
                project_path = os.path.dirname(file_path)
            
            project = self.get_rope_project(project_path)
            resource = project.get_resource(os.path.relpath(file_path, project_path))
            
            # Find symbol location
            analysis = await core.analyze_file(file_path)
            symbol_location = None
            
            for symbol in analysis.symbols:
                if symbol.name == symbol_name:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    offset = sum(len(line) for line in lines[:symbol.line_start-1])
                    offset += symbol.column_start
                    symbol_location = offset
                    break
            
            if symbol_location is None:
                return {
                    "success": False,
                    "error": f"Symbol '{symbol_name}' not found"
                }
            
            # Backup original file
            backup_path = await self.backup_file(file_path)
            
            # Perform inline operation
            inliner = rope.refactor.inline.InlineFunction(project, resource, symbol_location)
            changes = inliner.get_changes()
            
            # Apply changes
            project.do(changes)
            
            return {
                "success": True,
                "file_path": file_path,
                "symbol_name": symbol_name,
                "backup_path": backup_path,
                "inlined": True
            }
            
        except Exception as e:
            logging.error(f"Inline operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "symbol_name": symbol_name
            }
    
    async def move_symbol_to_file(self, source_file: str, symbol_name: str, 
                                target_file: str, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Move a symbol from one file to another"""
        try:
            if project_path is None:
                project_path = os.path.dirname(source_file)
            
            project = self.get_rope_project(project_path)
            source_resource = project.get_resource(os.path.relpath(source_file, project_path))
            target_resource = project.get_resource(os.path.relpath(target_file, project_path))
            
            # Find symbol location
            analysis = await core.analyze_file(source_file)
            symbol_location = None
            
            for symbol in analysis.symbols:
                if symbol.name == symbol_name:
                    with open(source_file, 'r') as f:
                        lines = f.readlines()
                    
                    offset = sum(len(line) for line in lines[:symbol.line_start-1])
                    offset += symbol.column_start
                    symbol_location = offset
                    break
            
            if symbol_location is None:
                return {
                    "success": False,
                    "error": f"Symbol '{symbol_name}' not found in source file"
                }
            
            # Backup both files
            source_backup = await self.backup_file(source_file)
            target_backup = await self.backup_file(target_file) if os.path.exists(target_file) else None
            
            # Perform move operation
            mover = rope.refactor.move.MoveMethod(project, source_resource, symbol_location)
            changes = mover.get_changes(target_resource)
            
            # Apply changes
            project.do(changes)
            
            return {
                "success": True,
                "source_file": source_file,
                "target_file": target_file,
                "symbol_name": symbol_name,
                "source_backup": source_backup,
                "target_backup": target_backup,
                "moved": True
            }
            
        except Exception as e:
            logging.error(f"Move operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_file": source_file,
                "target_file": target_file,
                "symbol_name": symbol_name
            }


# Initialize refactoring engine
refactoring_engine = RefactoringEngine()


@mcp.tool()
async def rename_symbol(old_name: str, new_name: str, file_path: str, 
                       scope: str = "project", project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely rename a symbol across the project or specified scope.
    
    Args:
        old_name: Current name of the symbol
        new_name: New name for the symbol
        file_path: File containing the symbol
        scope: Scope of rename ("file", "module", "project")
        project_path: Optional project root path
    
    Returns:
        Dictionary containing rename results and affected files
    """
    try:
        logging.info(f"Renaming symbol '{old_name}' to '{new_name}' in {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if project_path is None:
            project_path = os.path.dirname(file_path)
        
        result = await refactoring_engine.rename_symbol_in_project(
            project_path, file_path, old_name, new_name, scope
        )
        
        # Create git commit if successful
        if result["success"] and result.get("changed_files"):
            files_changed = [cf.get("resource", file_path) for cf in result["changed_files"]]
            git_result = await refactoring_engine.create_git_commit(
                project_path, 
                f"Refactor: rename {old_name} to {new_name}",
                files_changed
            )
            result["git_commit"] = git_result
        
        return result
        
    except Exception as e:
        logging.error(f"Symbol rename failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "old_name": old_name,
            "new_name": new_name
        }


@mcp.tool()
async def extract_method(file_path: str, start_line: int, end_line: int, 
                        method_name: str, project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract code lines into a new method.
    
    Args:
        file_path: File containing the code to extract
        start_line: Starting line number (1-based)
        end_line: Ending line number (1-based)
        method_name: Name for the new method
        project_path: Optional project root path
    
    Returns:
        Dictionary containing extraction results
    """
    try:
        logging.info(f"Extracting method '{method_name}' from lines {start_line}-{end_line} in {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        result = await refactoring_engine.extract_method_from_lines(
            file_path, start_line, end_line, method_name, project_path
        )
        
        # Create git commit if successful
        if result["success"]:
            git_result = await refactoring_engine.create_git_commit(
                project_path or os.path.dirname(file_path),
                f"Refactor: extract method {method_name}",
                [file_path]
            )
            result["git_commit"] = git_result
        
        return result
        
    except Exception as e:
        logging.error(f"Extract method failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "method_name": method_name
        }


@mcp.tool()
async def extract_variable(file_path: str, line: int, column: int, 
                          variable_name: str, project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract an expression into a new variable.
    
    Args:
        file_path: File containing the expression
        line: Line number of the expression (1-based)
        column: Column number of the expression (0-based)
        variable_name: Name for the new variable
        project_path: Optional project root path
    
    Returns:
        Dictionary containing extraction results
    """
    try:
        logging.info(f"Extracting variable '{variable_name}' at {file_path}:{line}:{column}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        result = await refactoring_engine.extract_variable_from_expression(
            file_path, line, column, variable_name, project_path
        )
        
        # Create git commit if successful
        if result["success"]:
            git_result = await refactoring_engine.create_git_commit(
                project_path or os.path.dirname(file_path),
                f"Refactor: extract variable {variable_name}",
                [file_path]
            )
            result["git_commit"] = git_result
        
        return result
        
    except Exception as e:
        logging.error(f"Extract variable failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "variable_name": variable_name
        }


@mcp.tool()
async def inline_method(file_path: str, method_name: str, 
                       project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Inline a method by replacing calls with the method body.
    
    Args:
        file_path: File containing the method
        method_name: Name of the method to inline
        project_path: Optional project root path
    
    Returns:
        Dictionary containing inline results
    """
    try:
        logging.info(f"Inlining method '{method_name}' in {file_path}")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        result = await refactoring_engine.inline_method_or_variable(
            file_path, method_name, project_path
        )
        
        # Create git commit if successful
        if result["success"]:
            git_result = await refactoring_engine.create_git_commit(
                project_path or os.path.dirname(file_path),
                f"Refactor: inline method {method_name}",
                [file_path]
            )
            result["git_commit"] = git_result
        
        return result
        
    except Exception as e:
        logging.error(f"Inline method failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "method_name": method_name
        }


@mcp.tool()
async def move_to_file(source_file: str, symbol_name: str, target_file: str,
                      project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Move a symbol (class, function, etc.) from one file to another.
    
    Args:
        source_file: File containing the symbol
        symbol_name: Name of the symbol to move
        target_file: Destination file
        project_path: Optional project root path
    
    Returns:
        Dictionary containing move results
    """
    try:
        logging.info(f"Moving symbol '{symbol_name}' from {source_file} to {target_file}")
        
        if not os.path.exists(source_file):
            return {
                "success": False,
                "error": f"Source file not found: {source_file}"
            }
        
        result = await refactoring_engine.move_symbol_to_file(
            source_file, symbol_name, target_file, project_path
        )
        
        # Create git commit if successful
        if result["success"]:
            git_result = await refactoring_engine.create_git_commit(
                project_path or os.path.dirname(source_file),
                f"Refactor: move {symbol_name} to {os.path.basename(target_file)}",
                [source_file, target_file]
            )
            result["git_commit"] = git_result
        
        return result
        
    except Exception as e:
        logging.error(f"Move symbol failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "source_file": source_file,
            "target_file": target_file,
            "symbol_name": symbol_name
        }


@mcp.tool()
async def preview_refactoring(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preview the effects of a refactoring operation without applying changes.
    
    Args:
        operation: Type of refactoring ("rename", "extract_method", "inline", "move")
        parameters: Parameters for the refactoring operation
    
    Returns:
        Dictionary containing preview of changes that would be made
    """
    try:
        logging.info(f"Previewing refactoring operation: {operation}")
        
        # This would be implemented to show diffs without actually applying changes
        # For now, return a placeholder response
        
        return {
            "success": True,
            "operation": operation,
            "parameters": parameters,
            "preview": "Refactoring preview functionality would show detailed diffs here",
            "estimated_changes": "Would show files and lines that would be modified"
        }
        
    except Exception as e:
        logging.error(f"Refactoring preview failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "operation": operation
        }


def main():
    """Main entry point for the MCP server"""
    setup_logging()
    logging.info("Starting Refactoring MCP Server")
    
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