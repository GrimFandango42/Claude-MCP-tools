#!/usr/bin/env python3
"""
Minimal Claude Code Integration MCP Server
Handles missing dependencies gracefully with fallback implementations
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Try to import MCP, fall back to mock if not available
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("WARNING: FastMCP not available. Running in diagnostic mode.")

# Try to import psutil, fall back to basic functionality if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("INFO: psutil not available. System monitoring disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status enumeration"""
    QUEUED = "queued"
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"

@dataclass
class TaskContext:
    """Simple task context for execution tracking"""
    task_id: str
    description: str
    status: TaskStatus
    created_at: datetime
    error_message: Optional[str] = None

class MockMCP:
    """Mock MCP server for testing when FastMCP is not available"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
    
    def tool(self):
        """Decorator to register tools"""
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator
    
    def run_diagnostic(self):
        """Run diagnostic tests"""
        print(f"\n=== {self.name} Diagnostic Mode ===")
        print(f"Registered tools: {list(self.tools.keys())}")
        
        # Test each tool
        for tool_name, tool_func in self.tools.items():
            try:
                print(f"\nTesting {tool_name}:")
                if tool_name == "check_dependencies":
                    result = tool_func()
                elif tool_name == "test_claude_code_availability":
                    result = tool_func()
                elif tool_name == "get_system_info":
                    result = tool_func()
                else:
                    print(f"  Skipping {tool_name} (requires parameters)")
                    continue
                
                print(f"  Result: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"  Error: {e}")

class ClaudeCodeIntegrationMCP:
    """Minimal Claude Code MCP Server"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskContext] = {}
        self.claude_code_available = self._check_claude_code_availability()
        
    def _check_claude_code_availability(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            result = subprocess.run(
                ["claude-code", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

# Initialize the appropriate server
claude_code_mcp = ClaudeCodeIntegrationMCP()

if MCP_AVAILABLE:
    mcp = FastMCP("Claude Code Integration - Minimal")
else:
    mcp = MockMCP("Claude Code Integration - Mock")

@mcp.tool()
def check_dependencies() -> dict:
    """Check the status of all dependencies"""
    return {
        "mcp_available": MCP_AVAILABLE,
        "psutil_available": PSUTIL_AVAILABLE,
        "claude_code_available": claude_code_mcp.claude_code_available,
        "python_version": sys.version,
        "python_executable": sys.executable,
        "current_directory": os.getcwd(),
        "message": "Dependency check complete"
    }

@mcp.tool()
def test_claude_code_availability() -> dict:
    """Test Claude Code CLI availability with detailed diagnostics"""
    try:
        result = subprocess.run(
            ["claude-code", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            return {
                "available": True,
                "version": result.stdout.strip(),
                "message": "Claude Code CLI is available and ready",
                "command_test": "SUCCESS"
            }
        else:
            return {
                "available": False,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "message": f"Claude Code CLI returned non-zero exit code: {result.returncode}"
            }
    except FileNotFoundError:
        return {
            "available": False,
            "error": "FileNotFoundError",
            "message": "Claude Code CLI not found. Please ensure it's installed and in PATH.",
            "installation_help": {
                "install_command": "npm install -g @anthropic-ai/claude-code",
                "verify_command": "claude-code --version",
                "documentation": "https://docs.anthropic.com/claude-code"
            }
        }
    except subprocess.TimeoutExpired:
        return {
            "available": False,
            "error": "TimeoutExpired", 
            "message": "Claude Code CLI command timed out after 10 seconds"
        }
    except Exception as e:
        return {
            "available": False,
            "error": type(e).__name__,
            "message": f"Unexpected error testing Claude Code CLI: {str(e)}"
        }

@mcp.tool()
def get_system_info() -> dict:
    """Get comprehensive system information"""
    system_info = {
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "platform": sys.platform
        },
        "environment": {
            "current_directory": os.getcwd(),
            "path_dirs": os.environ.get("PATH", "").split(os.pathsep)[:5],  # First 5 PATH entries
            "home_directory": os.path.expanduser("~")
        },
        "dependencies": {
            "mcp_available": MCP_AVAILABLE,
            "psutil_available": PSUTIL_AVAILABLE
        }
    }
    
    if PSUTIL_AVAILABLE:
        try:
            system_info["system_resources"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        except Exception as e:
            system_info["system_resources"] = {"error": str(e)}
    else:
        system_info["system_resources"] = {"note": "psutil not available"}
    
    return system_info

@mcp.tool()
def create_simple_task(description: str) -> dict:
    """Create a simple task for tracking (no execution)"""
    task_id = str(uuid.uuid4())
    task = TaskContext(
        task_id=task_id,
        description=description,
        status=TaskStatus.QUEUED,
        created_at=datetime.now()
    )
    
    claude_code_mcp.tasks[task_id] = task
    
    return {
        "success": True,
        "task_id": task_id,
        "description": description,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "message": "Task created successfully (execution requires Claude Code CLI)"
    }

@mcp.tool()
def list_tasks() -> dict:
    """List all created tasks"""
    tasks = []
    for task_id, task in claude_code_mcp.tasks.items():
        tasks.append({
            "task_id": task_id,
            "description": task.description,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "error_message": task.error_message
        })
    
    return {
        "success": True,
        "total_tasks": len(tasks),
        "tasks": tasks
    }

@mcp.tool()
def install_dependencies() -> dict:
    """Provide instructions for installing missing dependencies"""
    installation_commands = []
    
    if not MCP_AVAILABLE:
        installation_commands.append({
            "package": "fastmcp",
            "command": "pip install fastmcp>=0.2.0",
            "description": "MCP server framework"
        })
    
    if not PSUTIL_AVAILABLE:
        installation_commands.append({
            "package": "psutil", 
            "command": "pip install psutil>=5.9.0",
            "description": "System monitoring utilities"
        })
    
    if not claude_code_mcp.claude_code_available:
        installation_commands.append({
            "package": "claude-code",
            "command": "npm install -g @anthropic-ai/claude-code",
            "description": "Claude Code CLI tool"
        })
    
    return {
        "current_status": {
            "mcp_available": MCP_AVAILABLE,
            "psutil_available": PSUTIL_AVAILABLE,
            "claude_code_available": claude_code_mcp.claude_code_available
        },
        "installation_needed": len(installation_commands) > 0,
        "installation_commands": installation_commands,
        "setup_script": "pip install fastmcp psutil && npm install -g @anthropic-ai/claude-code",
        "virtual_environment_recommended": True,
        "venv_setup": [
            "python3 -m venv venv",
            "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
            "pip install fastmcp psutil"
        ]
    }

def main():
    """Main function"""
    global mcp
    if MCP_AVAILABLE:
        print("Starting Claude Code Integration MCP Server...")
        mcp.run()
    else:
        print("FastMCP not available. Running in diagnostic mode...")
        mcp.run_diagnostic()
        print("\n" + "="*50)
        print("To fix the dependency issues, run:")
        print("pip install fastmcp psutil")
        print("or")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
