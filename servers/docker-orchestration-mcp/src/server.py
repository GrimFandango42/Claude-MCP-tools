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
                ),
                Tool(
                    name="remove_container",
                    description="Remove a container (must be stopped first)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {"type": "string", "description": "Container ID or name"},
                            "force": {"type": "boolean", "description": "Force removal of running container", "default": False}
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="get_container_logs",
                    description="Get logs from a container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {"type": "string", "description": "Container ID or name"},
                            "tail": {"type": "integer", "description": "Number of lines to return", "default": 100},
                            "follow": {"type": "boolean", "description": "Follow log output", "default": False}
                        },
                        "required": ["container_id"]
                    }
                ),
                
                # Network Management Tools
                Tool(
                    name="create_network",
                    description="Create a Docker network",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Network name"},
                            "driver": {"type": "string", "description": "Network driver", "default": "bridge"},
                            "options": {"type": "object", "description": "Network options"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="list_networks",
                    description="List Docker networks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filters": {"type": "object", "description": "Filter criteria"}
                        }
                    }
                ),
                
                # Volume Management Tools
                Tool(
                    name="create_volume",
                    description="Create a Docker volume",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Volume name"},
                            "driver": {"type": "string", "description": "Volume driver", "default": "local"},
                            "options": {"type": "object", "description": "Volume options"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="list_volumes",
                    description="List Docker volumes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filters": {"type": "object", "description": "Filter criteria"}
                        }
                    }
                ),
                
                # Multi-Container Application Tools
                Tool(
                    name="deploy_application_stack",
                    description="Deploy a multi-container application stack",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Application stack name"},
                            "services": {"type": "array", "description": "List of service configurations"},
                            "network_name": {"type": "string", "description": "Network name for services"},
                            "create_network": {"type": "boolean", "description": "Create network if it doesn't exist", "default": True}
                        },
                        "required": ["name", "services"]
                    }
                ),
                
                # Health & Monitoring Tools
                Tool(
                    name="check_container_health",
                    description="Check the health status of a container",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {"type": "string", "description": "Container ID or name"}
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="get_system_resources",
                    description="Get Docker system resource usage",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                
                # Debugging & Diagnostics Tools
                Tool(
                    name="validate_configuration",
                    description="Validate deployment configuration before execution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "config": {"type": "object", "description": "Configuration to validate"}
                        },
                        "required": ["config"]
                    }
                ),
                Tool(
                    name="diagnose_container_issues",
                    description="Diagnose and analyze container problems",
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
                elif name == "remove_container":
                    result = await self._remove_container(**arguments)
                elif name == "get_container_logs":
                    result = await self._get_container_logs(**arguments)
                elif name == "create_network":
                    result = await self._create_network(**arguments)
                elif name == "list_networks":
                    result = await self._list_networks(**arguments)
                elif name == "create_volume":
                    result = await self._create_volume(**arguments)
                elif name == "list_volumes":
                    result = await self._list_volumes(**arguments)
                elif name == "deploy_application_stack":
                    result = await self._deploy_application_stack(**arguments)
                elif name == "check_container_health":
                    result = await self._check_container_health(**arguments)
                elif name == "get_system_resources":
                    result = await self._get_system_resources(**arguments)
                elif name == "validate_configuration":
                    result = await self._validate_configuration(**arguments)
                elif name == "diagnose_container_issues":
                    result = await self._diagnose_container_issues(**arguments)
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
    
    # Additional method implementations would continue here...
    # (I'll create the remaining methods in subsequent files to keep this manageable)
    
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
    
    # Complete implementations for all Docker operations
    async def _remove_container(self, container_id: str, force: bool = False) -> Dict[str, Any]:
        """Remove a container (must be stopped first unless force=True)"""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            
            return {
                "success": True,
                "container_id": container_id,
                "action": "removed",
                "forced": force,
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_container_logs(self, container_id: str, tail: int = 100, follow: bool = False) -> Dict[str, Any]:
        """Get logs from a container"""
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail, follow=follow).decode('utf-8')
            
            return {
                "success": True,
                "container_id": container_id,
                "logs": logs,
                "tail": tail,
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_network(self, name: str, driver: str = "bridge", options: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a Docker network"""
        try:
            network = self.client.networks.create(
                name=name,
                driver=driver,
                options=options or {}
            )
            
            return {
                "success": True,
                "network_id": network.id,
                "network_name": name,
                "driver": driver,
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.APIError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_networks(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """List Docker networks"""
        try:
            networks = self.client.networks.list(filters=filters or {})
            
            network_list = []
            for network in networks:
                network_info = {
                    "id": network.id,
                    "name": network.name,
                    "driver": network.attrs.get('Driver'),
                    "scope": network.attrs.get('Scope'),
                    "created": network.attrs.get('Created'),
                    "containers": list(network.attrs.get('Containers', {}).keys())
                }
                network_list.append(network_info)
            
            return {
                "success": True,
                "networks": network_list,
                "count": len(network_list),
                "filters_applied": filters or {}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_volume(self, name: str, driver: str = "local", options: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a Docker volume"""
        try:
            volume = self.client.volumes.create(
                name=name,
                driver=driver,
                driver_opts=options or {}
            )
            
            return {
                "success": True,
                "volume_name": name,
                "driver": driver,
                "mountpoint": volume.attrs.get('Mountpoint'),
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.APIError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_volumes(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """List Docker volumes"""
        try:
            volumes = self.client.volumes.list(filters=filters or {})
            
            volume_list = []
            for volume in volumes:
                volume_info = {
                    "name": volume.name,
                    "driver": volume.attrs.get('Driver'),
                    "mountpoint": volume.attrs.get('Mountpoint'),
                    "created": volume.attrs.get('CreatedAt'),
                    "labels": volume.attrs.get('Labels', {})
                }
                volume_list.append(volume_info)
            
            return {
                "success": True,
                "volumes": volume_list,
                "count": len(volume_list),
                "filters_applied": filters or {}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _deploy_application_stack(self, name: str, services: List[Dict], 
                                       network_name: Optional[str] = None, 
                                       create_network: bool = True) -> Dict[str, Any]:
        """Deploy a multi-container application stack"""
        try:
            deployed_containers = []
            network_created = False
            
            # Create network if specified and doesn't exist
            if network_name and create_network:
                try:
                    self.client.networks.get(network_name)
                except docker.errors.NotFound:
                    await self._create_network(network_name)
                    network_created = True
            
            # Deploy each service
            for i, service_config in enumerate(services):
                service_config['name'] = f"{name}_{service_config.get('name', f'service_{i}')}"
                if network_name:
                    service_config['network'] = network_name
                
                result = await self._deploy_container(**service_config)
                deployed_containers.append(result)
            
            return {
                "success": True,
                "stack_name": name,
                "network_name": network_name,
                "network_created": network_created,
                "services_deployed": len(services),
                "containers": deployed_containers,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e), "stack_name": name}
    
    async def _check_container_health(self, container_id: str) -> Dict[str, Any]:
        """Check the health status of a container"""
        try:
            container = self.client.containers.get(container_id)
            
            # Get health status from container attributes
            health_status = container.attrs.get('State', {}).get('Health', {})
            
            return {
                "success": True,
                "container_id": container_id,
                "container_name": container.name,
                "status": container.status,
                "health": health_status,
                "running": container.status == 'running',
                "timestamp": datetime.now().isoformat()
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_system_resources(self) -> Dict[str, Any]:
        """Get Docker system resource usage"""
        try:
            # Get system information
            system_info = self.client.info()
            
            # Get container statistics
            containers = self.client.containers.list(all=True)
            running_containers = [c for c in containers if c.status == 'running']
            
            return {
                "success": True,
                "system_info": {
                    "containers": system_info.get('Containers', 0),
                    "containers_running": system_info.get('ContainersRunning', 0),
                    "containers_paused": system_info.get('ContainersPaused', 0),
                    "containers_stopped": system_info.get('ContainersStopped', 0),
                    "images": system_info.get('Images', 0),
                    "server_version": system_info.get('ServerVersion'),
                    "total_memory": system_info.get('MemTotal', 0),
                    "cpu_count": system_info.get('NCPU', 0)
                },
                "running_containers": len(running_containers),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment configuration before execution"""
        try:
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Validate required fields
            if not config.get('image'):
                validation_results['errors'].append("Missing required 'image' field")
                validation_results['valid'] = False
            
            # Validate port mappings
            ports = config.get('ports', {})
            if ports and not isinstance(ports, dict):
                validation_results['errors'].append("Ports must be a dictionary")
                validation_results['valid'] = False
            
            # Validate environment variables
            environment = config.get('environment', {})
            if environment and not isinstance(environment, dict):
                validation_results['errors'].append("Environment must be a dictionary")
                validation_results['valid'] = False
            
            # Check if image exists (warning, not error)
            if config.get('image'):
                try:
                    self.client.images.get(config['image'])
                except docker.errors.ImageNotFound:
                    validation_results['warnings'].append(f"Image '{config['image']}' not found locally - will attempt to pull")
            
            return {
                "success": True,
                "validation": validation_results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _diagnose_container_issues(self, container_id: str) -> Dict[str, Any]:
        """Diagnose and analyze container problems"""
        try:
            container = self.client.containers.get(container_id)
            
            # Gather diagnostic information
            diagnostics = {
                "container_info": {
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "created": container.attrs.get('Created'),
                    "started": container.attrs.get('State', {}).get('StartedAt'),
                    "finished": container.attrs.get('State', {}).get('FinishedAt')
                },
                "state": container.attrs.get('State', {}),
                "recent_logs": container.logs(tail=50).decode('utf-8', errors='ignore'),
                "resource_usage": None,
                "network_info": container.attrs.get('NetworkSettings', {}),
                "mount_info": container.attrs.get('Mounts', []),
                "recommendations": []
            }
            
            # Get resource usage if running
            if container.status == 'running':
                try:
                    stats = container.stats(stream=False)
                    diagnostics['resource_usage'] = stats
                except:
                    diagnostics['recommendations'].append("Could not retrieve resource usage statistics")
            
            # Add recommendations based on status
            if container.status == 'exited':
                exit_code = container.attrs.get('State', {}).get('ExitCode', 0)
                if exit_code != 0:
                    diagnostics['recommendations'].append(f"Container exited with code {exit_code} - check logs for errors")
            
            if not diagnostics['recent_logs'].strip():
                diagnostics['recommendations'].append("No recent logs available - container may have startup issues")
            
            return {
                "success": True,
                "container_id": container_id,
                "diagnostics": diagnostics,
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
