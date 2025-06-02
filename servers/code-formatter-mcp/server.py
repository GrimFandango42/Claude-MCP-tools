"""
Simplified Code Formatter MCP Server
Focuses on what Claude can't do - actually execute formatters
"""

from fastmcp import FastMCP
import subprocess
import os
from pathlib import Path

mcp = FastMCP("code-formatter")

# Simple formatter mapping
FORMATTERS = {
    ".py": ["black", "-"],
    ".js": ["prettier", "--stdin-filepath", "file.js"],
    ".ts": ["prettier", "--stdin-filepath", "file.ts"],
    ".go": ["gofmt"],
    ".rs": ["rustfmt"],
}

@mcp.tool()
async def format_code(file_path: str) -> str:
    """
    Format code file using appropriate formatter.
    Returns formatted content or error message.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File {file_path} not found"
    
    ext = path.suffix
    if ext not in FORMATTERS:
        return f"No formatter configured for {ext} files"
    
    formatter_cmd = FORMATTERS[ext]
    
    try:
        # Read file content
        content = path.read_text()
        
        # Run formatter
        result = subprocess.run(
            formatter_cmd,
            input=content,
            text=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            # Write formatted content back
            path.write_text(result.stdout)
            return f"Successfully formatted {file_path}"
        else:
            return f"Formatter error: {result.stderr}"
            
    except Exception as e:
        return f"Error formatting file: {str(e)}"

@mcp.tool()
async def format_directory(directory: str, extensions: list[str]) -> dict:
    """
    Format all files in directory with given extensions.
    Returns summary of formatted files.
    """
    formatted = []
    errors = []
    
    for ext in extensions:
        for file_path in Path(directory).rglob(f"*{ext}"):
            result = await format_code(str(file_path))
            if "Successfully" in result:
                formatted.append(str(file_path))
            else:
                errors.append(f"{file_path}: {result}")
    
    return {
        "formatted": formatted,
        "errors": errors,
        "summary": f"Formatted {len(formatted)} files, {len(errors)} errors"
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")