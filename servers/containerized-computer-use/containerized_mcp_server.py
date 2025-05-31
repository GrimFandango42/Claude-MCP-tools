#!/usr/bin/env python3
"""
Containerized Computer Use MCP Server
Provides secure, isolated desktop automation through Docker containers.

This server implements the Computer Use API in a containerized environment,
offering enhanced security and cross-platform compatibility.
"""

import json
import asyncio
import logging
import subprocess
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import docker
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='[containerized-computer-use] %(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

class ContainerizedComputerUseMCP:
    """MCP Server for containerized Computer Use with Docker integration."""
    
    def __init__(self):
        self.server = Server("containerized-computer-use")
        self.container_name = "windows-computer-use"
        self.docker_client = None
        self.container = None
        
        # Initialize Docker client
        try:
            # Try to connect to Docker Desktop on Windows
            self.docker_client = docker.DockerClient(base_url='npipe://./pipe/docker_engine')
            # Test the connection
            self.docker_client.ping()
            logging.info("Docker client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Docker client: {e}")
            try:
                # Fallback to default environment
                self.docker_client = docker.from_env()
                self.docker_client.ping()
                logging.info("Docker client initialized via fallback method")
            except Exception as e2:
                logging.error(f"Docker fallback also failed: {e2}")
                self.docker_client = None
        self._register_tools()
        
    def _register_tools(self):
        """Register all Computer Use tools with the MCP server."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="computer_20250124",
                    description="Control computer with actions like screenshot, mouse, keyboard operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["screenshot", "key", "type", "mouse_move", "left_click", 
                                       "right_click", "middle_click", "double_click", "triple_click",
                                       "left_click_drag", "scroll", "wait", "cursor_position",
                                       "left_mouse_down", "left_mouse_up", "hold_key"],
                                "description": "The action to perform"
                            },
                            "coordinate": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Coordinates [x, y] for mouse operations"
                            },
                            "text": {
                                "type": "string",
                                "description": "Text for keyboard operations or key combos"
                            },
                            "start_coordinate": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Start coordinates for drag operations"
                            },
                            "end_coordinate": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "End coordinates for drag operations"
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["up", "down"],
                                "description": "Scroll direction"
                            },
                            "clicks": {
                                "type": "integer",
                                "description": "Number of scroll clicks"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Duration in milliseconds"
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="text_editor_20250429",
                    description="View and edit text files within the container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum": ["view", "create", "str_replace"],
                                "description": "The command to execute"
                            },
                            "path": {
                                "type": "string",
                                "description": "File path within the container"
                            },
                            "file_text": {
                                "type": "string",
                                "description": "Content for file creation"
                            },
                            "old_str": {
                                "type": "string",
                                "description": "String to replace"
                            },
                            "new_str": {
                                "type": "string",
                                "description": "Replacement string"
                            },
                            "view_range": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Line range to view [start, end]"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="bash_20250124",
                    description="Execute bash commands in the container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Bash command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="container_status",
                    description="Check the status of the Docker container",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="container_start",
                    description="Start the Computer Use container",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="container_stop",
                    description="Stop the Computer Use container",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="container_logs",
                    description="Get recent logs from the container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lines": {
                                "type": "integer",
                                "description": "Number of log lines to retrieve",
                                "default": 50
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool execution requests."""
            logging.info(f"Executing tool: {name} with arguments: {arguments}")
            
            try:
                # Container management tools
                if name == "container_status":
                    result = await self._get_container_status()
                elif name == "container_start":
                    result = await self._start_container()
                elif name == "container_stop":
                    result = await self._stop_container()
                elif name == "container_logs":
                    lines = arguments.get("lines", 50)
                    result = await self._get_container_logs(lines)
                
                # Computer Use API tools - delegate to container
                elif name in ["computer_20250124", "text_editor_20250429", "bash_20250124"]:
                    result = await self._execute_in_container(name, arguments)
                else:
                    result = {"output": f"ERROR: Unknown tool: {name}"}
                
                # Handle screenshot in result
                if "screenshot" in result:
                    # Return both text and image content
                    return [
                        TextContent(type="text", text=result.get("output", "Screenshot captured")),
                        ImageContent(type="image", data=result["screenshot"], mimeType="image/png")
                    ]
                else:
                    return [TextContent(type="text", text=json.dumps(result))]
                    
            except Exception as e:
                logging.error(f"Error executing tool {name}: {e}")
                error_result = {"output": f"ERROR: {str(e)}"}
                return [TextContent(type="text", text=json.dumps(error_result))]
    
    async def _get_container_status(self) -> Dict[str, Any]:
        """Check if the container is running."""
        try:
            if not self.docker_client:
                return {"output": "ERROR: Docker client not initialized"}
            
            try:
                container = self.docker_client.containers.get(self.container_name)
                status = container.status
                attrs = container.attrs
                
                # Get resource stats
                stats = container.stats(stream=False)
                
                # Calculate resource usage
                cpu_percent = 0.0
                if stats['cpu_stats']['cpu_usage']['total_usage'] > 0:
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100.0
                
                memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)  # MB
                memory_limit = stats['memory_stats']['limit'] / (1024 * 1024)  # MB
                
                return {
                    "output": f"Container Status: {status.upper()}",
                    "status": status,
                    "id": container.short_id,
                    "created": attrs['Created'],
                    "ports": attrs['NetworkSettings']['Ports'],
                    "cpu_percent": f"{cpu_percent:.2f}%",
                    "memory_usage": f"{memory_usage:.2f}MB / {memory_limit:.2f}MB",
                    "vnc_url": "vnc://localhost:5900" if status == "running" else None
                }
            except docker.errors.NotFound:
                return {
                    "output": "Container not found. Run 'container_start' to create it.",
                    "status": "not_found"
                }
        except Exception as e:
            logging.error(f"Error checking container status: {e}")
            return {"output": f"ERROR: Failed to check container status: {str(e)}"}
    
    async def _start_container(self) -> Dict[str, Any]:
        """Start the Computer Use container."""
        try:
            if not self.docker_client:
                return {"output": "ERROR: Docker client not initialized"}
            
            # Check if container exists
            try:
                container = self.docker_client.containers.get(self.container_name)
                if container.status == "running":
                    return {"output": "Container is already running"}
                else:
                    container.start()
                    await asyncio.sleep(3)  # Wait for services to start
                    return {"output": "Container started successfully"}
            except docker.errors.NotFound:
                # Container doesn't exist, create it
                logging.info("Container not found, creating new container...")
                
                # Build image if needed
                image_name = "containerized-computer-use:latest"
                try:
                    self.docker_client.images.get(image_name)
                except docker.errors.ImageNotFound:
                    logging.info("Building Docker image...")
                    # Use docker-compose to build
                    compose_path = Path(__file__).parent / "docker-compose.yml"
                    result = subprocess.run(
                        ["docker-compose", "-f", str(compose_path), "build"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        return {"output": f"ERROR: Failed to build image: {result.stderr}"}
                
                # Create and start container
                container = self.docker_client.containers.run(
                    image_name,
                    name=self.container_name,
                    detach=True,
                    ports={'5900/tcp': 5900},
                    environment={
                        'DISPLAY': ':1',
                        'VNC_RESOLUTION': '1920x1080',
                        'VNC_PW': 'vnc123'
                    },
                    volumes={
                        str(Path(__file__).parent / "shared"): {'bind': '/app/shared', 'mode': 'rw'},
                        str(Path(__file__).parent / "workspaces"): {'bind': '/app/workspaces', 'mode': 'rw'}
                    },
                    mem_limit="4g",
                    cpu_quota=200000,  # 2 CPUs
                    remove=False
                )
                
                await asyncio.sleep(5)  # Wait for services to fully start
                return {
                    "output": "Container created and started successfully",
                    "vnc_url": "vnc://localhost:5900",
                    "vnc_password": "vnc123"
                }
                
        except Exception as e:
            logging.error(f"Error starting container: {e}")
            return {"output": f"ERROR: Failed to start container: {str(e)}"}
    
    async def _stop_container(self) -> Dict[str, Any]:
        """Stop the Computer Use container."""
        try:
            if not self.docker_client:
                return {"output": "ERROR: Docker client not initialized"}
                
            container = self.docker_client.containers.get(self.container_name)
            container.stop(timeout=10)
            return {"output": "Container stopped successfully"}
            
        except docker.errors.NotFound:
            return {"output": "Container not found"}
        except Exception as e:
            logging.error(f"Error stopping container: {e}")
            return {"output": f"ERROR: Failed to stop container: {str(e)}"}
    
    async def _get_container_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get recent logs from the container."""
        try:
            if not self.docker_client:
                return {"output": "ERROR: Docker client not initialized"}
                
            container = self.docker_client.containers.get(self.container_name)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            
            return {
                "output": f"Last {lines} lines of container logs:\n{logs}"
            }
            
        except docker.errors.NotFound:
            return {"output": "Container not found"}
        except Exception as e:
            logging.error(f"Error getting container logs: {e}")
            return {"output": f"ERROR: Failed to get logs: {str(e)}"}
    
    async def _execute_in_container(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Computer Use tool inside the container."""
        try:
            if not self.docker_client:
                return {"output": "ERROR: Docker client not initialized"}
            
            # Ensure container is running
            status = await self._get_container_status()
            if status.get("status") != "running":
                # Try to start container
                start_result = await self._start_container()
                if "ERROR" in start_result.get("output", ""):
                    return start_result
            
            container = self.docker_client.containers.get(self.container_name)
            
            # Prepare the command to execute in container
            cmd_data = {
                "tool": tool_name,
                "arguments": arguments
            }
            
            # Execute the command
            exec_command = [
                "python3", "-c",
                f"""
import json
import sys
from computer_use_container import ContainerizedComputerUseAPI

api = ContainerizedComputerUseAPI()
data = {json.dumps(cmd_data)}
tool_name = data['tool']
arguments = data['arguments']

if tool_name == 'computer_20250124':
    result = api.computer_20250124(**arguments)
elif tool_name == 'text_editor_20250429':
    result = api.text_editor_20250429(**arguments)
elif tool_name == 'bash_20250124':
    result = api.bash_20250124(**arguments)
else:
    result = {{'output': f'Unknown tool: {{tool_name}}'}}

print(json.dumps(result))
"""
            ]
            
            result = container.exec_run(exec_command, stdout=True, stderr=True)
            
            if result.exit_code != 0:
                error_msg = result.output.decode('utf-8')
                logging.error(f"Container execution error: {error_msg}")
                return {"output": f"ERROR: Container execution failed: {error_msg}"}
            
            # Parse the result
            output = result.output.decode('utf-8')
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # If not JSON, return as plain text
                return {"output": output}
                
        except Exception as e:
            logging.error(f"Error executing in container: {e}")
            return {"output": f"ERROR: Failed to execute in container: {str(e)}"}
    
    async def run(self):
        """Run the MCP server."""
        logging.info("Starting Containerized Computer Use MCP Server...")
        
        # Check Docker availability
        if self.docker_client:
            logging.info("Docker client connected successfully")
            status = await self._get_container_status()
            logging.info(f"Initial container status: {status.get('status', 'unknown')}")
        else:
            logging.warning("Docker client not available - container management disabled")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Entry point for the MCP server."""
    server = ContainerizedComputerUseMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
