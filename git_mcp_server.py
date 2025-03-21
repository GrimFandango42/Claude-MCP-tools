import asyncio
import json
import logging
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("git_mcp_server.log")
    ]
)
logger = logging.getLogger("git_mcp_server")

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Git operations
async def run_git_command(args: List[str], cwd: str = None) -> Dict[str, Any]:
    """Run a git command and return the result"""
    try:
        cmd = ["git"] + args
        logger.info(f"Running git command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()
        
        if process.returncode != 0:
            logger.error(f"Git command failed: {stderr_str}")
            return {
                "success": False,
                "error": stderr_str,
                "output": stdout_str,
                "returncode": process.returncode
            }
        
        logger.info(f"Git command succeeded: {stdout_str}")
        return {
            "success": True,
            "output": stdout_str,
            "returncode": process.returncode
        }
    except Exception as e:
        logger.error(f"Error running git command: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        }

async def git_status(repo_path: str) -> Dict[str, Any]:
    """Get the status of a git repository"""
    return await run_git_command(["status"], cwd=repo_path)

async def git_init(repo_path: str) -> Dict[str, Any]:
    """Initialize a git repository"""
    return await run_git_command(["init"], cwd=repo_path)

async def git_add(repo_path: str, files: List[str] = None) -> Dict[str, Any]:
    """Add files to git staging"""
    if files is None:
        files = ["."]  # Add all files if none specified
    return await run_git_command(["add"] + files, cwd=repo_path)

async def git_commit(repo_path: str, message: str) -> Dict[str, Any]:
    """Commit changes to git"""
    return await run_git_command(["commit", "-m", message], cwd=repo_path)

async def git_remote_add(repo_path: str, name: str, url: str) -> Dict[str, Any]:
    """Add a remote repository"""
    return await run_git_command(["remote", "add", name, url], cwd=repo_path)

async def git_push(repo_path: str, remote: str, branch: str) -> Dict[str, Any]:
    """Push changes to a remote repository"""
    return await run_git_command(["push", "-u", remote, branch], cwd=repo_path)

async def git_pull(repo_path: str, remote: str, branch: str) -> Dict[str, Any]:
    """Pull changes from a remote repository"""
    return await run_git_command(["pull", remote, branch], cwd=repo_path)

async def git_clone(repo_url: str, target_path: str) -> Dict[str, Any]:
    """Clone a repository"""
    return await run_git_command(["clone", repo_url, target_path])

async def git_branch(repo_path: str, branch_name: str = None) -> Dict[str, Any]:
    """Create a new branch or list branches"""
    if branch_name:
        return await run_git_command(["branch", branch_name], cwd=repo_path)
    else:
        return await run_git_command(["branch"], cwd=repo_path)

async def git_checkout(repo_path: str, branch_name: str) -> Dict[str, Any]:
    """Checkout a branch"""
    return await run_git_command(["checkout", branch_name], cwd=repo_path)

# WebSocket endpoint for MCP
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received message: {message}")
            
            # Extract message details
            method = message.get("method")
            message_id = message.get("id")
            
            # Handle initialize method
            if method == "initialize":
                logger.debug("Handling initialize request")
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "experimental": {}
                        },
                        "serverInfo": {
                            "name": "Git MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }))
                logger.info("Sent initialize response")
            
            # Handle tools/list method
            elif method == "tools/list":
                logger.debug("Handling tools/list request")
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "tools": [
                            {
                                "name": "git_status",
                                "description": "Get the status of a git repository",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        }
                                    },
                                    "required": ["repo_path"]
                                }
                            },
                            {
                                "name": "git_init",
                                "description": "Initialize a git repository",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to initialize the git repository"
                                        }
                                    },
                                    "required": ["repo_path"]
                                }
                            },
                            {
                                "name": "git_add",
                                "description": "Add files to git staging",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "files": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Files to add (default: all files)"
                                        }
                                    },
                                    "required": ["repo_path"]
                                }
                            },
                            {
                                "name": "git_commit",
                                "description": "Commit changes to git",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "Commit message"
                                        }
                                    },
                                    "required": ["repo_path", "message"]
                                }
                            },
                            {
                                "name": "git_remote_add",
                                "description": "Add a remote repository",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "name": {
                                            "type": "string",
                                            "description": "Name of the remote (e.g., 'origin')"
                                        },
                                        "url": {
                                            "type": "string",
                                            "description": "URL of the remote repository"
                                        }
                                    },
                                    "required": ["repo_path", "name", "url"]
                                }
                            },
                            {
                                "name": "git_push",
                                "description": "Push changes to a remote repository",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "remote": {
                                            "type": "string",
                                            "description": "Name of the remote (e.g., 'origin')"
                                        },
                                        "branch": {
                                            "type": "string",
                                            "description": "Branch to push (e.g., 'main' or 'master')"
                                        }
                                    },
                                    "required": ["repo_path", "remote", "branch"]
                                }
                            },
                            {
                                "name": "git_pull",
                                "description": "Pull changes from a remote repository",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "remote": {
                                            "type": "string",
                                            "description": "Name of the remote (e.g., 'origin')"
                                        },
                                        "branch": {
                                            "type": "string",
                                            "description": "Branch to pull (e.g., 'main' or 'master')"
                                        }
                                    },
                                    "required": ["repo_path", "remote", "branch"]
                                }
                            },
                            {
                                "name": "git_clone",
                                "description": "Clone a repository",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_url": {
                                            "type": "string",
                                            "description": "URL of the repository to clone"
                                        },
                                        "target_path": {
                                            "type": "string",
                                            "description": "Path where to clone the repository"
                                        }
                                    },
                                    "required": ["repo_url", "target_path"]
                                }
                            },
                            {
                                "name": "git_branch",
                                "description": "Create a new branch or list branches",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "branch_name": {
                                            "type": "string",
                                            "description": "Name of the branch to create (optional)"
                                        }
                                    },
                                    "required": ["repo_path"]
                                }
                            },
                            {
                                "name": "git_checkout",
                                "description": "Checkout a branch",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repo_path": {
                                            "type": "string",
                                            "description": "Path to the git repository"
                                        },
                                        "branch_name": {
                                            "type": "string",
                                            "description": "Name of the branch to checkout"
                                        }
                                    },
                                    "required": ["repo_path", "branch_name"]
                                }
                            }
                        ]
                    }
                }))
                logger.info("Sent tools/list response")
            
            # Handle tools/call method
            elif method == "tools/call":
                logger.debug("Handling tools/call request")
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
                
                result = None
                error = None
                
                try:
                    if tool_name == "git_status":
                        repo_path = arguments.get("repo_path")
                        result = await git_status(repo_path)
                    
                    elif tool_name == "git_init":
                        repo_path = arguments.get("repo_path")
                        result = await git_init(repo_path)
                    
                    elif tool_name == "git_add":
                        repo_path = arguments.get("repo_path")
                        files = arguments.get("files")
                        result = await git_add(repo_path, files)
                    
                    elif tool_name == "git_commit":
                        repo_path = arguments.get("repo_path")
                        message = arguments.get("message")
                        result = await git_commit(repo_path, message)
                    
                    elif tool_name == "git_remote_add":
                        repo_path = arguments.get("repo_path")
                        name = arguments.get("name")
                        url = arguments.get("url")
                        result = await git_remote_add(repo_path, name, url)
                    
                    elif tool_name == "git_push":
                        repo_path = arguments.get("repo_path")
                        remote = arguments.get("remote")
                        branch = arguments.get("branch")
                        result = await git_push(repo_path, remote, branch)
                    
                    elif tool_name == "git_pull":
                        repo_path = arguments.get("repo_path")
                        remote = arguments.get("remote")
                        branch = arguments.get("branch")
                        result = await git_pull(repo_path, remote, branch)
                    
                    elif tool_name == "git_clone":
                        repo_url = arguments.get("repo_url")
                        target_path = arguments.get("target_path")
                        result = await git_clone(repo_url, target_path)
                    
                    elif tool_name == "git_branch":
                        repo_path = arguments.get("repo_path")
                        branch_name = arguments.get("branch_name")
                        result = await git_branch(repo_path, branch_name)
                    
                    elif tool_name == "git_checkout":
                        repo_path = arguments.get("repo_path")
                        branch_name = arguments.get("branch_name")
                        result = await git_checkout(repo_path, branch_name)
                    
                    else:
                        error = f"Unknown tool: {tool_name}"
                        logger.warning(error)
                except Exception as e:
                    error = str(e)
                    logger.error(f"Error executing {tool_name}: {error}", exc_info=True)
                
                if error:
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32000,
                            "message": error
                        }
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        }
                    }))
                    logger.info(f"Sent {tool_name} response")
            
            # Handle unknown methods
            else:
                logger.warning(f"Unknown method: {method}")
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)

# HTTP endpoint for health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the server
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8092  # Different port to avoid conflicts
    logger.info(f"Starting Git MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
