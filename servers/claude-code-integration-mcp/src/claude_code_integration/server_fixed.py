#!/usr/bin/env python3
"""
Fixed Claude Code Integration MCP Server using FastMCP
Provides a bridge between Claude Desktop and Claude Code CLI
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from fastmcp import FastMCP

# Configure logging to stderr only
import logging
logger = logging.getLogger(__name__)
logger.propagate = False

mcp = FastMCP("claude-code-integration")

# Check if Claude Code CLI is available
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
    
    # Check common installation paths
    common_paths = [
        Path.home() / ".local" / "bin" / "claude-code",
        Path("/usr/local/bin/claude-code"),
        Path("C:/Program Files/Claude/claude-code.exe"),
        Path("C:/Users") / os.environ.get("USERNAME", "User") / "AppData/Local/Programs/claude-code/claude-code.exe"
    ]
    
    for path in common_paths:
        if path.exists():
            return {
                "installed": True,
                "version": "unknown",
                "path": str(path),
                "method": "found_at_path"
            }
    
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
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute a command using Claude Code CLI.
    
    Args:
        prompt: The instruction or question for Claude Code
        system_prompt: Optional system prompt to guide behavior
        model: Optional model override (e.g., 'claude-3-opus-20240229')
        temperature: Optional temperature setting (0.0-1.0)
        max_tokens: Optional max tokens for response
    
    Returns:
        Dictionary with execution results
    """
    
    # Check if CLI is available
    cli_status = check_claude_code_cli()
    if not cli_status["installed"]:
        return {
            "success": False,
            "error": "Claude Code CLI not installed",
            "details": cli_status,
            "suggestion": "Please install Claude Code CLI to use this integration"
        }
    
    # Build command
    cmd = [cli_status["path"] or "claude-code"]
    
    # Add optional parameters
    if model:
        cmd.extend(["--model", model])
    if temperature is not None:
        cmd.extend(["--temperature", str(temperature)])
    if max_tokens:
        cmd.extend(["--max-tokens", str(max_tokens)])
    if system_prompt:
        cmd.extend(["--system", system_prompt])
    
    # Add the prompt
    cmd.append(prompt)
    
    try:
        # Execute command
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
            "command": " ".join(cmd[:2] + ["..."])  # Show command without full prompt
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 5 minutes",
            "command": " ".join(cmd[:2] + ["..."])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "command": " ".join(cmd[:2] + ["..."])
        }

@mcp.tool()
async def check_claude_code_installation() -> Dict[str, Any]:
    """
    Check the installation status of Claude Code CLI.
    
    Returns:
        Dictionary with installation details
    """
    return check_claude_code_cli()

@mcp.tool()
async def analyze_project(project_path: str) -> Dict[str, Any]:
    """
    Use Claude Code to analyze a project and provide insights.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        Analysis results from Claude Code
    """
    if not Path(project_path).exists():
        return {
            "success": False,
            "error": f"Project path does not exist: {project_path}"
        }
    
    prompt = f"""Analyze the project at {project_path} and provide:
1. Project structure overview
2. Main technologies used
3. Key components and their purposes
4. Suggestions for improvements
5. Any potential issues found"""
    
    return await execute_claude_code(
        prompt=prompt,
        system_prompt="You are analyzing a software project. Be thorough but concise."
    )

@mcp.tool()
async def delegate_coding_task(
    task_description: str,
    context: Optional[str] = None,
    constraints: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delegate a coding task to Claude Code CLI.
    
    Args:
        task_description: Description of the coding task
        context: Optional context about the project or requirements
        constraints: Optional constraints or guidelines
    
    Returns:
        Claude Code's response with implementation
    """
    prompt_parts = [task_description]
    
    if context:
        prompt_parts.append(f"\nContext: {context}")
    
    if constraints:
        prompt_parts.append(f"\nConstraints: {constraints}")
    
    full_prompt = "\n".join(prompt_parts)
    
    return await execute_claude_code(
        prompt=full_prompt,
        system_prompt="You are a skilled software developer. Provide complete, working code with explanations."
    )

@mcp.tool()
async def run_claude_code_interactive(
    initial_prompt: str,
    working_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run Claude Code in interactive mode for complex tasks.
    
    Args:
        initial_prompt: Initial prompt to start the session
        working_directory: Optional working directory for the session
    
    Returns:
        Session results
    """
    # Note: This is a simplified version. Full interactive mode would require
    # maintaining state between calls
    
    cmd = ["claude-code", "--interactive"]
    
    if working_directory:
        if not Path(working_directory).exists():
            return {
                "success": False,
                "error": f"Working directory does not exist: {working_directory}"
            }
        cmd.extend(["--cwd", working_directory])
    
    # For now, just execute the initial prompt
    # In a full implementation, this would maintain a session
    return await execute_claude_code(
        prompt=initial_prompt,
        system_prompt="You are in an interactive coding session. Be helpful and thorough."
    )

# Simple mock mode for testing without CLI
MOCK_MODE = os.getenv("CLAUDE_CODE_MOCK", "false").lower() == "true"

if MOCK_MODE:
    logger.info("Running in mock mode - no actual Claude Code CLI calls")
    
    @mcp.tool()
    async def mock_execute(prompt: str) -> Dict[str, Any]:
        """Mock execution for testing."""
        return {
            "success": True,
            "mock": True,
            "prompt_received": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "response": "This is a mock response. Install Claude Code CLI for real functionality."
        }

if __name__ == "__main__":
    # Run with stdio transport
    mcp.run(transport="stdio")