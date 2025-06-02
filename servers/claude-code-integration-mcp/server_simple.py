#!/usr/bin/env python3
"""
Simple Claude Code Integration MCP Server - Standalone version
Embeds all logic in one file to avoid import issues
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP

mcp = FastMCP("claude-code-integration")

def check_claude_code_cli() -> Dict[str, Any]:
    """Check if Claude Code CLI is installed and available."""
    try:
        result = subprocess.run(
            ["claude-code", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return {
                "installed": True,
                "version": result.stdout.strip(),
                "path": "claude-code",
                "method": "cli"
            }
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return {
        "installed": False,
        "version": None,
        "path": None,
        "method": "not_found",
        "suggestion": "Install Claude Code CLI from https://github.com/anthropics/claude-code"
    }

@mcp.tool()
async def execute_claude_code(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a command using Claude Code CLI or mock mode.
    
    Args:
        prompt: The instruction for Claude Code
        system_prompt: Optional system prompt
        model: Optional model override
    
    Returns:
        Dictionary with execution results
    """
    
    # Check if we're in mock mode
    if os.getenv("CLAUDE_CODE_MOCK", "false").lower() == "true":
        return {
            "success": True,
            "mock": True,
            "prompt_received": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "response": f"Mock response for: {prompt}",
            "message": "Running in mock mode. Install Claude Code CLI for real functionality."
        }
    
    # Check if CLI is available
    cli_status = check_claude_code_cli()
    if not cli_status["installed"]:
        return {
            "success": False,
            "error": "Claude Code CLI not installed",
            "details": cli_status,
            "suggestion": "Set CLAUDE_CODE_MOCK=true for testing or install Claude Code CLI"
        }
    
    # Build command
    cmd = [cli_status["path"] or "claude-code"]
    
    if model:
        cmd.extend(["--model", model])
    if system_prompt:
        cmd.extend(["--system", system_prompt])
    
    cmd.append(prompt)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "command": " ".join(cmd[:2] + ["..."])
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 5 minutes"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@mcp.tool()
async def check_claude_code_installation() -> Dict[str, Any]:
    """Check the installation status of Claude Code CLI."""
    return check_claude_code_cli()

@mcp.tool()
async def analyze_project(project_path: str) -> Dict[str, Any]:
    """Use Claude Code to analyze a project."""
    if not Path(project_path).exists():
        return {
            "success": False,
            "error": f"Project path does not exist: {project_path}"
        }
    
    prompt = f"""Analyze the project at {project_path} and provide:
1. Project structure overview
2. Main technologies used
3. Key components and their purposes
4. Suggestions for improvements"""
    
    return await execute_claude_code(
        prompt=prompt,
        system_prompt="You are analyzing a software project. Be thorough but concise."
    )

@mcp.tool()
async def delegate_coding_task(
    task_description: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """Delegate a coding task to Claude Code CLI."""
    prompt_parts = [task_description]
    
    if context:
        prompt_parts.append(f"\nContext: {context}")
    
    full_prompt = "\n".join(prompt_parts)
    
    return await execute_claude_code(
        prompt=full_prompt,
        system_prompt="You are a skilled software developer. Provide complete, working code with explanations."
    )

if __name__ == "__main__":
    mcp.run(transport="stdio")