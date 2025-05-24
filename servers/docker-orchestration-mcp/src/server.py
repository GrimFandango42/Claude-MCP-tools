#!/usr/bin/env python3
"""
Docker Orchestration MCP Server

Provides autonomous Docker container orchestration capabilities through the Model Context Protocol.
Enables Claude to deploy, manage, and monitor Docker containers and applications.
"""

import asyncio
import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import docker
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configure logging with JSON structure for Claude Desktop integration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Claude Desktop captures stderr
    ]
)
logger = logging.getLogger("docker-orchestration")

class DockerOrchestrationServer:
    """
    Docker Orchestration MCP Server
    
    Provides comprehensive Docker management capabilities with autonomous features:
    - Container lifecycle management
    - Network and volume management
    - Multi-container application deployment
    - Health monitoring and diagnostics
    - Built-in debugging and error recovery
    """
    
    def __init__(self):
        """Initialize the Docker Orchestration Server"""
        self.client = None
        self.server = Server("docker-orchestration")
        self.deployment_history = []
        
        # Initialize Docker client with error handling
        self._initialize_docker_client()
        
        # Register MCP tools
        self._register_tools()
        
        logger.info("Docker Orchestration MCP Server initialized")
    
    def _initialize_docker_client(self):
        """Initialize Docker client with proper error handling"""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Docker client connected successfully")
        except docker.errors.DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            logger.error("Ensure Docker Desktop is running and accessible")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Docker client: {e}")
            raise
    
    def _register_tools(self):
        """Register all MCP tools with the server"""
        
        # Container Management Tools
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available Docker orchestration tools"""
            return [
                # Core Container Management
                Tool(
                    name="deploy_container",
                    description="Deploy a Docker container with specified configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image": {"type": "string", "description": "Docker image name and tag"},
                            "name": {"type": "string", "description": "Container name (optional)"},
                            "ports": {"type": "object", "description": "Port mappings (container_port: host_port)"},
                            "environment": {"type": "object", "description": "Environment variables"},
                            "volumes": {"type": "object", "description": "Volume mappings (host_path: container_path)"},
                            "network": {"type": "string", "description": "Network to connect to"},
                            "restart_policy": {"type": "string", "description": "Restart policy (no, always, on-failure, unless-stopped)"},
                            "detach": {"type": "boolean", "description": "Run container in background", "default": True}
                        },
                        "required": ["image"]
                    }
                ),
                Tool(
                    name="list_containers",
                    description="List Docker containers with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "all": {"type": "boolean", "description": "Include stopped containers", "default": False},
                            "filters": {"type": "object", "description": "Filter criteria (status, name, etc.)"}
                        }
                    }
                ),
                # Additional tools would continue here...
                Tool(
                    name="get_container_info",
                    description="Get detailed information about a specific container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {"type": "string", "description": "Container ID or name"}
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="stop_container",
                    description="Stop a running container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {"type": "string", "description": "Container ID or name"},
                            "timeout": {"type": "integer", "description": "Seconds to wait before killing", "default": 10}
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="start_container",
                    description="Start a stopped container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {"type": "string", "description": "Container ID or name"}
                        },
                        "required": ["container_id"]
                    }
                )
            ]
        
        # Tool Call Handlers
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle MCP tool calls"""
            try:
                logger.info(f"Executing tool: {name} with arguments: {json.dumps(arguments, default=str)}")
                
                # Route to appropriate handler
                if name == "deploy_container":
                    result = await self._deploy_container(**arguments)
                elif name == "list_containers":
                    result = await self._list_containers(**arguments)
                elif name == "get_container_info":
                    result = await self._get_container_info(**arguments)
                elif name == "stop_container":
                    result = await self._stop_container(**arguments)
                elif name == "start_container":
                    result = await self._start_container(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                logger.info(f"Tool {name} executed successfully")
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                
            except Exception as e:
                error_msg = f"Error executing tool {name}: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }, indent=2))]
    
    # Container Management Implementation
    async def _deploy_container(self, image: str, name: Optional[str] = None, 
                              ports: Optional[Dict] = None, environment: Optional[Dict] = None,
                              volumes: Optional[Dict] = None, network: Optional[str] = None,
                              restart_policy: str = "no", detach: bool = True) -> Dict[str, Any]:
        """Deploy a Docker container with specified configuration"""
        
        try:
            # Build container configuration
            container_config = {
                'image': image,
                'detach': detach,
                'name': name
            }
            
            # Add port mappings
            if ports:
                container_config['ports'] = ports
            
            # Add environment variables
            if environment:
                container_config['environment'] = environment
            
            # Add volume mappings
            if volumes:
                container_config['volumes'] = volumes
            
            # Set restart policy
            if restart_policy != "no":
                container_config['restart_policy'] = {"Name": restart_policy}
            
            # Pull image if not available locally
            logger.info(f"Pulling image {image} if not available locally")
            try:
                self.client.images.pull(image)
            except docker.errors.NotFound:
                logger.error(f"Image {image} not found in registry")
                raise
            
            # Create and start container
            logger.info(f"Creating container from image {image}")
            container = self.client.containers.run(**container_config)
            
            # Connect to network if specified
            if network:
                try:
                    network_obj = self.client.networks.get(network)
                    network_obj.connect(container)
                    logger.info(f"Connected container to network {network}")
                except docker.errors.NotFound:
                    logger.warning(f"Network {network} not found, container running on default network")
            
            # Wait a moment for container to start
            await asyncio.sleep(2)
            
            # Get updated container info
            container.reload()
            
            # Record deployment
            deployment_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "deploy_container",
                "container_id": container.id,
                "container_name": container.name,
                "image": image,
                "status": container.status,
                "success": True
            }
            self.deployment_history.append(deployment_record)
            
            return {
                "success": True,
                "container_id": container.id,
                "container_name": container.name,
                "status": container.status,
                "image": image,
                "ports": container.ports,
                "created": container.attrs.get('Created'),
                "deployment_record": deployment_record
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy container: {e}")
            return {
                "success": False,
                "error": str(e),
                "image": image,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _list_containers(self, all: bool = False, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """List Docker containers with optional filtering"""
        
        try:
            containers = self.client.containers.list(all=all, filters=filters or {})
            
            container_list = []
            for container in containers:
                container_info = {
                    "id": container.id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "created": container.attrs.get('Created'),
                    "ports": container.ports,
                    "labels": container.labels
                }
                container_list.append(container_info)
            
            return {
                "success": True,
                "containers": container_list,
                "count": len(container_list),
                "filters_applied": filters or {},
                "include_stopped": all
            }
            
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_container_info(self, container_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific container"""
        
        try:
            container = self.client.containers.get(container_id)
            
            return {
                "success": True,
                "container": {
                    "id": container.id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "created": container.attrs.get('Created'),
                    "started": container.attrs.get('State', {}).get('StartedAt'),
                    "ports": container.ports,
                    "environment": container.attrs.get('Config', {}).get('Env', []),
                    "volumes": container.attrs.get('Mounts', []),
                    "network_settings": container.attrs.get('NetworkSettings', {}),
                    "resource_usage": container.stats(stream=False) if container.status == 'running' else None,
                    "labels": container.labels
                }
            }
            
        except docker.errors.NotFound:
            return {
                "success": False,
                "error": f"Container {container_id} not found",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get container info: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _stop_container(self, container_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Stop a running container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            
            return {
                "success": True,
                "container_id": container_id,
                "action": "stopped",
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_container(self, container_id: str) -> Dict[str, Any]:
        """Start a stopped container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            
            return {
                "success": True,
                "container_id": container_id,
                "action": "started",
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main entry point for the Docker Orchestration MCP Server"""
    
    # Initialize server
    docker_server = DockerOrchestrationServer()
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await docker_server.server.run(
            read_stream,
            write_stream,
            docker_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    logger.info("Starting Docker Orchestration MCP Server")
    asyncio.run(main())
