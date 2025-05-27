#!/usr/bin/env python3
"""
Enhanced Claude Code Integration MCP Server
Provides advanced orchestration and delegation capabilities for Claude Code CLI
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

try:
    import psutil
except ImportError:
    psutil = None

# MCP imports
from mcp.server.fastmcp import FastMCP

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
    TERMINATED = "terminated"
    KILLED = "killed"
    ERROR = "error"

class TaskPriority(Enum):
    """Task priority levels for execution order"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ProjectContext:
    """Project-specific context and configuration"""
    path: str
    name: str
    type: Optional[str] = None
    git_remote: Optional[str] = None
    branch: Optional[str] = None
    dependencies: List[str] = None
    build_command: Optional[str] = None
    test_command: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class TaskContext:
    """Enhanced task context with execution metadata"""
    task_id: str
    description: str
    project_context: Optional[ProjectContext]
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.QUEUED
    pid: Optional[int] = None
    exit_code: Optional[int] = None
    command_executed: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None
    dependencies: List[str] = None
    tags: List[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []

class EnhancedClaudeCodeMCP:
    """Enhanced Claude Code MCP Server with advanced orchestration capabilities"""
    
    def __init__(self):
        self.active_project_path: Optional[str] = None
        self.tasks: Dict[str, TaskContext] = {}
        self.projects: Dict[str, ProjectContext] = {}
        self.claude_code_available = self._check_claude_code_availability()
        self.task_queue: List[str] = []
        
    def _check_claude_code_availability(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            # Set up proper environment with node binary path
            env = os.environ.copy()
            env['PATH'] = '/home/nithin/.nvm/versions/node/v24.1.0/bin:' + env.get('PATH', '')
            
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                env=env
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def _detect_project_type(self, project_path: str) -> Optional[str]:
        """Detect project type based on files present"""
        path = Path(project_path)
        
        if (path / "package.json").exists():
            return "nodejs"
        elif (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
            return "python"
        elif (path / "Cargo.toml").exists():
            return "rust"
        elif (path / "pom.xml").exists():
            return "java"
        elif (path / "go.mod").exists():
            return "go"
        elif (path / "composer.json").exists():
            return "php"
        elif any((path / f).exists() for f in ["*.csproj", "*.sln"]):
            return "dotnet"
        
        return None

    def _get_git_info(self, project_path: str) -> tuple[Optional[str], Optional[str]]:
        """Get git remote and current branch information"""
        try:
            remote_result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            remote = remote_result.stdout.strip() if remote_result.returncode == 0 else None
            
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
            
            return remote, branch
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None, None

    async def _analyze_project(self, project_path: str) -> ProjectContext:
        """Analyze project and create context"""
        path = Path(project_path)
        project_name = path.name
        project_type = self._detect_project_type(project_path)
        git_remote, branch = self._get_git_info(project_path)
        
        build_command = None
        test_command = None
        dependencies = []
        
        if project_type == "nodejs":
            build_command = "npm run build"
            test_command = "npm test"
            if (path / "package.json").exists():
                try:
                    with open(path / "package.json") as f:
                        package_data = json.load(f)
                        dependencies = list(package_data.get("dependencies", {}).keys())
                except:
                    pass
        elif project_type == "python":
            build_command = "python -m build" if (path / "pyproject.toml").exists() else None
            test_command = "python -m pytest"
            if (path / "requirements.txt").exists():
                try:
                    with open(path / "requirements.txt") as f:
                        dependencies = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
                except:
                    pass
        
        return ProjectContext(
            path=project_path,
            name=project_name,
            type=project_type,
            git_remote=git_remote,
            branch=branch,
            dependencies=dependencies,
            build_command=build_command,
            test_command=test_command
        )

    async def _execute_task_async(self, task_id: str) -> None:
        """Execute a task asynchronously"""
        task = self.tasks.get(task_id)
        if not task:
            return
            
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            cmd = self._build_claude_code_command(task)
            task.command_executed = " ".join(cmd)
            
            # Set up proper environment with node binary path
            env = os.environ.copy()
            env['PATH'] = '/home/nithin/.nvm/versions/node/v24.1.0/bin:' + env.get('PATH', '')
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=task.project_context.path if task.project_context else None,
                env=env
            )
            
            task.pid = process.pid
            stdout, stderr = await process.communicate()
            
            task.stdout = stdout.decode('utf-8', errors='replace')
            task.stderr = stderr.decode('utf-8', errors='replace')
            task.exit_code = process.returncode
            task.completed_at = datetime.now()
            
            if process.returncode == 0:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
                task.error_message = f"Process exited with code {process.returncode}"
                
        except Exception as e:
            task.status = TaskStatus.ERROR
            task.error_message = str(e)
            task.completed_at = datetime.now()
        
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)

    def _build_claude_code_command(self, task: TaskContext) -> List[str]:
        """Build the Claude Code CLI command for a task"""
        cmd = ["claude"]
        
        if task.project_context:
            cmd.extend(["--project", task.project_context.path])
        
        cmd.extend(["--task", task.description])
        
        if task.project_context and task.project_context.type:
            cmd.extend(["--project-type", task.project_context.type])
            
        return cmd

# Initialize the MCP server
mcp = FastMCP("Enhanced Claude Code Integration")
claude_code_mcp = EnhancedClaudeCodeMCP()

@mcp.tool()
def check_claude_code_availability() -> dict:
    """Check if Claude Code CLI is available and get version info"""
    try:
        # Set up proper environment with node binary path
        env = os.environ.copy()
        env['PATH'] = '/home/nithin/.nvm/versions/node/v24.1.0/bin:' + env.get('PATH', '')
        
        result = subprocess.run(
            ["claude", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            env=env
        )
        
        if result.returncode == 0:
            return {
                "available": True,
                "version": result.stdout.strip(),
                "message": "Claude Code CLI is available and ready"
            }
        else:
            return {
                "available": False,
                "message": f"Claude Code CLI returned non-zero exit code: {result.returncode}",
                "stderr": result.stderr
            }
    except FileNotFoundError:
        return {
            "available": False,
            "message": "Claude Code CLI not found. Please ensure it's installed and in PATH."
        }
    except Exception as e:
        return {
            "available": False,
            "message": f"Unexpected error checking Claude Code CLI: {str(e)}"
        }

@mcp.tool()
def analyze_project(project_path: str) -> dict:
    """Analyze a project and return detailed context information"""
    try:
        if not os.path.exists(project_path):
            return {
                "success": False,
                "message": f"Project path does not exist: {project_path}"
            }
        
        # Create event loop for async operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            project_context = loop.run_until_complete(
                claude_code_mcp._analyze_project(project_path)
            )
        finally:
            loop.close()
        
        claude_code_mcp.projects[project_path] = project_context
        
        return {
            "success": True,
            "project_context": asdict(project_context),
            "message": f"Project analyzed successfully: {project_context.name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error analyzing project: {str(e)}"
        }

@mcp.tool()
def set_active_project(project_path: str) -> dict:
    """Set the active project path with automatic analysis"""
    try:
        if project_path not in claude_code_mcp.projects:
            analysis_result = analyze_project(project_path)
            if not analysis_result["success"]:
                return analysis_result
        
        claude_code_mcp.active_project_path = project_path
        project_context = claude_code_mcp.projects[project_path]
        
        return {
            "success": True,
            "message": f"Active project set to: {project_context.name}",
            "project_context": asdict(project_context)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting active project: {str(e)}"
        }

@mcp.tool()
def delegate_coding_task(
    task_description: str,
    project_path: Optional[str] = None,
    priority: str = "normal",
    tags: Optional[List[str]] = None,
    dependencies: Optional[List[str]] = None
) -> dict:
    """Delegate a coding task to Claude Code with enhanced context and prioritization"""
    try:
        if project_path is None:
            project_path = claude_code_mcp.active_project_path
            
        if project_path is None:
            return {
                "success": False,
                "message": "No project path specified and no active project set"
            }
        
        if project_path not in claude_code_mcp.projects:
            analysis_result = analyze_project(project_path)
            if not analysis_result["success"]:
                return analysis_result
        
        project_context = claude_code_mcp.projects[project_path]
        
        try:
            task_priority = TaskPriority[priority.upper()]
        except KeyError:
            task_priority = TaskPriority.NORMAL
        
        task_id = str(uuid.uuid4())
        task = TaskContext(
            task_id=task_id,
            description=task_description,
            project_context=project_context,
            priority=task_priority,
            created_at=datetime.now(),
            dependencies=dependencies or [],
            tags=tags or []
        )
        
        claude_code_mcp.tasks[task_id] = task
        claude_code_mcp.task_queue.append(task_id)
        
        if not claude_code_mcp.claude_code_available:
            task.status = TaskStatus.ERROR
            task.error_message = "Claude Code CLI not available"
            return {
                "success": False,
                "task_id": task_id,
                "message": "Claude Code CLI not available. Please install and configure it."
            }
        
        # Start execution asynchronously
        task.status = TaskStatus.STARTED
        
        # Create and run the async task
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.create_task(claude_code_mcp._execute_task_async(task_id))
            # Let the task start but don't block
        except Exception as async_error:
            task.status = TaskStatus.ERROR
            task.error_message = f"Failed to start async execution: {str(async_error)}"
        
        return {
            "success": True,
            "task_id": task_id,
            "status": task.status.value,
            "priority": task.priority.name,
            "project": project_context.name,
            "message": f"Task delegated successfully: {task_description[:50]}..."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error delegating task: {str(e)}"
        }

@mcp.tool()
def monitor_task_progress(task_id: str) -> dict:
    """Monitor the progress and status of a delegated task"""
    task = claude_code_mcp.tasks.get(task_id)
    if not task:
        return {
            "success": False,
            "message": f"Task ID not found: {task_id}"
        }
    
    # Check if process is still running (if psutil is available)
    if psutil and task.pid and task.status == TaskStatus.RUNNING:
        try:
            process = psutil.Process(task.pid)
            if not process.is_running():
                task.status = TaskStatus.COMPLETED if task.exit_code == 0 else TaskStatus.FAILED
                task.completed_at = datetime.now()
        except psutil.NoSuchProcess:
            task.status = TaskStatus.COMPLETED if task.exit_code == 0 else TaskStatus.FAILED
            task.completed_at = datetime.now()
    
    execution_time = None
    if task.started_at:
        end_time = task.completed_at or datetime.now()
        execution_time = (end_time - task.started_at).total_seconds()
    
    return {
        "success": True,
        "task_id": task_id,
        "status": task.status.value,
        "description": task.description,
        "project": task.project_context.name if task.project_context else None,
        "priority": task.priority.name,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "execution_time_seconds": execution_time,
        "pid": task.pid,
        "exit_code": task.exit_code,
        "command_executed": task.command_executed,
        "error_message": task.error_message,
        "tags": task.tags,
        "retry_count": task.retry_count
    }

@mcp.tool()
def get_task_results(task_id: str, include_output: bool = True) -> dict:
    """Retrieve results and output from a completed task"""
    task = claude_code_mcp.tasks.get(task_id)
    if not task:
        return {
            "success": False,
            "message": f"Task ID not found: {task_id}"
        }
    
    if task.status in [TaskStatus.QUEUED, TaskStatus.STARTED, TaskStatus.RUNNING]:
        return {
            "success": False,
            "task_id": task_id,
            "status": task.status.value,
            "message": "Task is still running. Results not yet available."
        }
    
    result = {
        "success": True,
        "task_id": task_id,
        "status": task.status.value,
        "exit_code": task.exit_code,
        "execution_time": (
            (task.completed_at - task.started_at).total_seconds() 
            if task.completed_at and task.started_at else None
        ),
        "error_message": task.error_message
    }
    
    if include_output:
        result.update({
            "stdout": task.stdout,
            "stderr": task.stderr
        })
    
    return result

@mcp.tool()
def list_active_tasks() -> dict:
    """List all active and queued tasks"""
    active_tasks = []
    completed_tasks = []
    
    for task_id, task in claude_code_mcp.tasks.items():
        task_info = {
            "task_id": task_id,
            "description": task.description[:100] + "..." if len(task.description) > 100 else task.description,
            "status": task.status.value,
            "priority": task.priority.name,
            "project": task.project_context.name if task.project_context else None,
            "created_at": task.created_at.isoformat(),
            "tags": task.tags
        }
        
        if task.status in [TaskStatus.QUEUED, TaskStatus.STARTED, TaskStatus.RUNNING]:
            active_tasks.append(task_info)
        else:
            completed_tasks.append(task_info)
    
    return {
        "success": True,
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks[-10:],
        "total_active": len(active_tasks),
        "total_completed": len(completed_tasks)
    }

@mcp.tool()
def get_system_status() -> dict:
    """Get comprehensive system status including tasks, projects, and resources"""
    task_stats = {
        "total": len(claude_code_mcp.tasks),
        "queued": len([t for t in claude_code_mcp.tasks.values() if t.status == TaskStatus.QUEUED]),
        "running": len([t for t in claude_code_mcp.tasks.values() if t.status == TaskStatus.RUNNING]),
        "completed": len([t for t in claude_code_mcp.tasks.values() if t.status == TaskStatus.COMPLETED]),
        "failed": len([t for t in claude_code_mcp.tasks.values() if t.status == TaskStatus.FAILED])
    }
    
    project_stats = {
        "total": len(claude_code_mcp.projects),
        "active_project": claude_code_mcp.active_project_path,
        "project_types": list(set(p.type for p in claude_code_mcp.projects.values() if p.type))
    }
    
    system_resources = {}
    if psutil:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_resources = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        except:
            system_resources = {"error": "Could not retrieve system resources"}
    else:
        system_resources = {"note": "psutil not available for system monitoring"}
    
    return {
        "success": True,
        "claude_code_available": claude_code_mcp.claude_code_available,
        "task_statistics": task_stats,
        "project_statistics": project_stats,
        "system_resources": system_resources,
        "queue_length": len(claude_code_mcp.task_queue)
    }

if __name__ == "__main__":
    mcp.run()
