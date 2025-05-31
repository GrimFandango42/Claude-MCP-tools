#!/usr/bin/env python3
"""
Enhanced Claude Code Integration MCP Server

This server provides Claude Code CLI functionality through MCP, with enhanced
capabilities including JSON output parsing, session management, and proper
error handling.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Optional Anthropic client for mock functionality
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Initialize the MCP server
server = Server("claude-code-integration")

# Session management
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.default_session = "default"
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        self.sessions[session_id] = {
            "id": session_id,
            "created": datetime.now().isoformat(),
            "history": [],
            "context": {},
            "mcp_config": None
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        return list(self.sessions.values())

# Global session manager
session_manager = SessionManager()

class ClaudeCodeAPI:
    """Enhanced Claude Code API integration with proper SDK compliance."""
    
    def __init__(self):
        self.claude_code_path = self._find_claude_code()
        
    def _find_claude_code(self) -> Optional[str]:
        """Find Claude Code CLI executable."""
        # Check common locations
        common_paths = [
            "/usr/local/bin/claude-code",
            os.path.expanduser("~/.local/bin/claude-code"),
            "claude-code"  # System PATH
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # Try which command
        try:
            result = subprocess.run(["which", "claude-code"], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def _build_command(self, prompt: str, **options) -> List[str]:
        """Build Claude Code command with SDK-compliant flags."""
        if not self.claude_code_path:
            raise RuntimeError("Claude Code CLI not found. Please install it first.")
        
        cmd = [self.claude_code_path]
        
        # Essential flags for MCP integration
        cmd.extend(["--output-format", "json"])  # Always use JSON for structured output
        
        # Session management
        if session_id := options.get("session_id"):
            if options.get("continue_session"):
                cmd.extend(["--continue", session_id])
            elif options.get("resume_session"):
                cmd.extend(["--resume", session_id])
        
        # Conversation control
        if max_turns := options.get("max_turns"):
            cmd.extend(["--max-turns", str(max_turns)])
        
        # System prompts
        if system_prompt := options.get("system_prompt"):
            cmd.extend(["--system-prompt", system_prompt])
        
        if append_system := options.get("append_system_prompt"):
            cmd.extend(["--append-system-prompt", append_system])
        
        # Tool management
        if allowed_tools := options.get("allowed_tools"):
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])
        
        if disallowed_tools := options.get("disallowed_tools"):
            cmd.extend(["--disallowedTools", ",".join(disallowed_tools)])
        
        # MCP configuration
        if mcp_config := options.get("mcp_config"):
            cmd.extend(["--mcp-config", mcp_config])
        
        # Working directory
        if cwd := options.get("working_directory"):
            cmd.extend(["--cwd", cwd])
        
        # Output control
        if options.get("no_color"):
            cmd.append("--no-color")
        
        if options.get("verbose"):
            cmd.append("--verbose")
        
        # The prompt/instruction
        cmd.append(prompt)
        
        return cmd
    
    async def execute_command(self, prompt: str, **options) -> Dict[str, Any]:
        """Execute Claude Code command with proper error handling."""
        try:
            cmd = self._build_command(prompt, **options)
            
            # Set working directory if specified
            cwd = options.get("working_directory", os.getcwd())
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse JSON output
            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.decode("utf-8") if stdout else "",
                "stderr": stderr.decode("utf-8") if stderr else "",
                "command": " ".join(cmd)
            }
            
            # Try to parse JSON output
            if result["success"] and result["stdout"]:
                try:
                    result["parsed_output"] = json.loads(result["stdout"])
                except json.JSONDecodeError:
                    # Fallback to text output
                    result["parsed_output"] = {"content": result["stdout"]}
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

class MockClaudeCodeAPI:
    """Mock implementation of Claude Code CLI using Anthropic API."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if mock API is available."""
        return self.client is not None
    
    async def execute_command(self, prompt: str, **options) -> Dict[str, Any]:
        """Mock Claude Code execution using Anthropic API."""
        
        if not self.is_available():
            return {
                "success": False,
                "error": "ANTHROPIC_API_KEY not set or anthropic package not installed. Cannot use mock Claude Code API.",
                "error_type": "ConfigurationError"
            }
        
        try:
            # Build system prompt based on options
            system_parts = []
            
            if system_prompt := options.get("system_prompt"):
                system_parts.append(system_prompt)
            
            if append_system := options.get("append_system_prompt"):
                system_parts.append(append_system)
            
            # Add Claude Code simulation instructions
            system_parts.append(
                "You are Claude Code CLI. Respond as if you are executing commands "
                "in a development environment. Provide practical, actionable code "
                "and explanations. If the user asks you to create files or run "
                "commands, simulate the output they would see."
            )
            
            # Tool management
            if allowed_tools := options.get("allowed_tools"):
                system_parts.append(f"You can only use these tools: {', '.join(allowed_tools)}")
            
            if disallowed_tools := options.get("disallowed_tools"):
                system_parts.append(f"You cannot use these tools: {', '.join(disallowed_tools)}")
            
            system_prompt_combined = "\n\n".join(system_parts) if system_parts else "You are Claude Code CLI."
            
            # Make API call
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                system=system_prompt_combined,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Format response as Claude Code would
            content = response.content[0].text if response.content else ""
            
            result = {
                "success": True,
                "return_code": 0,
                "stdout": content,
                "stderr": "",
                "command": f"claude-code (mock) '{prompt[:50]}...'" if len(prompt) > 50 else f"claude-code (mock) '{prompt}'",
                "parsed_output": {
                    "content": content,
                    "model": "claude-3-sonnet-20240229",
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    } if hasattr(response, 'usage') else None,
                    "mock": True
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "mock": True
            }

class EnhancedClaudeCodeAPI(ClaudeCodeAPI):
    """Enhanced API with mock fallback."""
    
    def __init__(self):
        super().__init__()
        self.mock_api = MockClaudeCodeAPI()
        self.prefer_mock = os.getenv("CLAUDE_CODE_USE_MOCK", "").lower() in ("true", "1", "yes")
    
    async def execute_command(self, prompt: str, **options) -> Dict[str, Any]:
        """Execute with fallback to mock API."""
        
        # If CLI not available or mock preferred, use mock
        if not self.claude_code_path or self.prefer_mock:
            if self.mock_api.is_available():
                result = await self.mock_api.execute_command(prompt, **options)
                result["execution_method"] = "mock_api"
                return result
            else:
                return {
                    "success": False,
                    "error": "Neither Claude Code CLI nor Anthropic API key available",
                    "error_type": "ConfigurationError",
                    "suggestions": [
                        "Install Claude Code CLI",
                        "Set ANTHROPIC_API_KEY environment variable",
                        "Check system requirements"
                    ]
                }
        
        # Try CLI first
        result = await super().execute_command(prompt, **options)
        result["execution_method"] = "claude_code_cli"
        
        # If CLI fails and mock is available, fallback
        if not result["success"] and self.mock_api.is_available():
            mock_result = await self.mock_api.execute_command(prompt, **options)
            mock_result["execution_method"] = "mock_api_fallback"
            mock_result["cli_error"] = result.get("error", "CLI execution failed")
            return mock_result
        
        return result

# Global API instance
claude_code_api = EnhancedClaudeCodeAPI()

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available Claude Code integration tools."""
    return [
        types.Tool(
            name="claude_code_execute",
            description="Execute Claude Code CLI with enhanced capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt/instruction to send to Claude Code"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session ID for conversation continuity"
                    },
                    "continue_session": {
                        "type": "boolean",
                        "description": "Continue existing session",
                        "default": False
                    },
                    "resume_session": {
                        "type": "boolean",
                        "description": "Resume existing session",
                        "default": False
                    },
                    "max_turns": {
                        "type": "integer",
                        "description": "Maximum conversation turns",
                        "minimum": 1,
                        "maximum": 50
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt to guide Claude Code behavior"
                    },
                    "append_system_prompt": {
                        "type": "string",
                        "description": "Additional system prompt to append"
                    },
                    "allowed_tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of allowed tools for Claude Code"
                    },
                    "disallowed_tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of disallowed tools for Claude Code"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for Claude Code execution"
                    },
                    "mcp_config": {
                        "type": "string",
                        "description": "Path to MCP configuration file"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Enable verbose output",
                        "default": False
                    },
                    "no_color": {
                        "type": "boolean",
                        "description": "Disable colored output",
                        "default": False
                    }
                },
                "required": ["prompt"]
            }
        ),
        types.Tool(
            name="claude_code_session_create",
            description="Create a new Claude Code session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Optional custom session ID"
                    }
                }
            }
        ),
        types.Tool(
            name="claude_code_session_list",
            description="List all Claude Code sessions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="claude_code_session_info",
            description="Get information about a specific session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to query"
                    }
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="claude_code_check_installation",
            description="Check Claude Code CLI installation status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="claude_code_create_mcp_config",
            description="Create MCP configuration file for Claude Code",
            inputSchema={
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path where to save the MCP config file"
                    },
                    "servers": {
                        "type": "object",
                        "description": "MCP servers configuration"
                    }
                },
                "required": ["config_path", "servers"]
            }
        }
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls for Claude Code integration."""
    
    if name == "claude_code_execute":
        prompt = arguments.get("prompt", "")
        if not prompt:
            return [types.TextContent(
                type="text",
                text="Error: Prompt is required for Claude Code execution"
            )]
        
        # Session management
        session_id = arguments.get("session_id")
        if session_id and session_id not in session_manager.sessions:
            session_manager.create_session(session_id)
        
        # Execute Claude Code
        result = await claude_code_api.execute_command(prompt, **arguments)
        
        # Update session if provided
        if session_id:
            session_manager.update_session(session_id, {
                "last_command": prompt,
                "last_result": result,
                "last_execution": datetime.now().isoformat()
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "claude_code_session_create":
        session_id = session_manager.create_session(arguments.get("session_id"))
        return [types.TextContent(
            type="text",
            text=f"Created session: {session_id}"
        )]
    
    elif name == "claude_code_session_list":
        sessions = session_manager.list_sessions()
        return [types.TextContent(
            type="text",
            text=json.dumps(sessions, indent=2)
        )]
    
    elif name == "claude_code_session_info":
        session_id = arguments.get("session_id")
        session = session_manager.get_session(session_id)
        if not session:
            return [types.TextContent(
                type="text",
                text=f"Session not found: {session_id}"
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(session, indent=2)
        )]
    
    elif name == "claude_code_check_installation":
        claude_code_path = claude_code_api._find_claude_code()
        status = {
            "installed": claude_code_path is not None,
            "path": claude_code_path,
            "version": None
        }
        
        # Try to get version if installed
        if claude_code_path:
            try:
                result = subprocess.run([claude_code_path, "--version"],
                                       capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    status["version"] = result.stdout.strip()
            except:
                pass
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    
    elif name == "claude_code_create_mcp_config":
        config_path = arguments.get("config_path")
        servers = arguments.get("servers", {})
        
        config = {
            "mcpServers": servers
        }
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return [types.TextContent(
                type="text",
                text=f"MCP configuration saved to: {config_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error creating MCP config: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Run the Claude Code Integration MCP server."""
    # Create default session
    session_manager.create_session(session_manager.default_session)
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="claude-code-integration",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
