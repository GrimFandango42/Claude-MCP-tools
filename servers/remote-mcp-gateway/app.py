#!/usr/bin/env python3
"""
Remote MCP Gateway - HTTP/WebSocket Bridge for Mobile Access

This service converts your local MCP servers into HTTP REST APIs
that can be accessed from Claude mobile app or any HTTP client.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remote-mcp-gateway")

# FastAPI app
app = FastAPI(
    title="Remote MCP Gateway",
    description="HTTP/WebSocket bridge for MCP servers - Access your MCP skills from anywhere!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security (optional)
security = HTTPBearer(auto_error=False)

# Request/Response Models
class MCPToolRequest(BaseModel):
    """Generic MCP tool request."""
    tool_name: str = Field(description="Name of the MCP tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    server_id: Optional[str] = Field(default=None, description="Specific MCP server to use")

class MCPToolResponse(BaseModel):
    """Generic MCP tool response."""
    success: bool = Field(description="Whether the tool execution succeeded")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Tool response data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(description="Execution time in seconds")
    server_used: str = Field(description="Which server processed the request")

class ServerStatus(BaseModel):
    """MCP server status information."""
    server_id: str
    name: str
    status: str  # "running", "error", "stopped"
    tools: List[str]
    last_health_check: datetime
    endpoint_url: Optional[str] = None

# MCP Server Registry
class MCPServerRegistry:
    """Registry of available MCP servers and their capabilities."""
    
    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.load_server_configs()
    
    def load_server_configs(self):
        """Load MCP server configurations."""
        # Travel Booking Server
        self.servers["travel-booking"] = {
            "name": "Travel Booking Assistant",
            "status": "running",
            "tools": [
                "search_accommodations",
                "search_accommodations_with_airbnb",
                "get_recommendations",
                "analyze_price_trends",
                "get_booking_links",
                "get_destination_insights",
                "get_smart_travel_recommendations",
                "visual_property_verification",
                "configure_mcp_integrations"
            ],
            "description": "Intelligent travel booking with multi-platform search and AI recommendations",
            "local_path": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\travel-booking-mcp",
            "import_module": "travel_booking.server"
        }
        
        # Enhanced Memory Server
        self.servers["enhanced-memory"] = {
            "name": "Enhanced Memory System",
            "status": "running", 
            "tools": [
                "create_experiment",
                "update_experiment",
                "get_similar_experiments",
                "analyze_patterns",
                "generate_learning_insights",
                "get_experiment_recommendations"
            ],
            "description": "Self-improving memory with experiment tracking and pattern recognition",
            "local_path": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\enhanced-memory-mcp",
            "import_module": "enhanced_memory.server"
        }
        
        # Auto-Accept Server
        self.servers["auto-accept"] = {
            "name": "Auto-Accept Autonomous Coding",
            "status": "running",
            "tools": [
                "start_autonomous_loop",
                "execute_loop_iteration", 
                "get_loop_status",
                "pause_loop",
                "resume_loop",
                "rollback_to_checkpoint",
                "complete_loop"
            ],
            "description": "Autonomous coding loops with safety checkpoints and test verification",
            "local_path": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\auto-accept-mcp",
            "import_module": "auto_accept.server"
        }
        
        # Visual Debugging Server
        self.servers["visual-debugging"] = {
            "name": "Visual Infrastructure Debugging",
            "status": "running",
            "tools": [
                "analyze_screenshot",
                "analyze_kubernetes_dashboard",
                "suggest_troubleshooting_commands",
                "interpret_dashboard_metrics"
            ],
            "description": "Visual analysis of infrastructure dashboards and screenshots",
            "local_path": "C:\\AI_Projects\\Claude-MCP-tools\\servers\\visual-debugging-mcp",
            "import_module": "visual_debugging.server"
        }

    def get_server_info(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific server."""
        return self.servers.get(server_id)
    
    def list_servers(self) -> List[ServerStatus]:
        """List all registered servers."""
        servers = []
        for server_id, config in self.servers.items():
            servers.append(ServerStatus(
                server_id=server_id,
                name=config["name"],
                status=config["status"],
                tools=config["tools"],
                last_health_check=datetime.now(),
                endpoint_url=f"/api/v1/servers/{server_id}"
            ))
        return servers
    
    def get_all_tools(self) -> Dict[str, List[str]]:
        """Get all available tools across all servers."""
        all_tools = {}
        for server_id, config in self.servers.items():
            all_tools[server_id] = config["tools"]
        return all_tools

# Global registry instance
registry = MCPServerRegistry()

# Tool execution engine
class MCPToolExecutor:
    """Executes MCP tools by routing to appropriate servers."""
    
    def __init__(self, registry: MCPServerRegistry):
        self.registry = registry
        self.loaded_modules = {}
    
    async def execute_tool(self, request: MCPToolRequest) -> MCPToolResponse:
        """Execute a tool request."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Find which server has this tool
            server_id = self._find_server_for_tool(request.tool_name, request.server_id)
            if not server_id:
                return MCPToolResponse(
                    success=False,
                    error=f"Tool '{request.tool_name}' not found in any server",
                    execution_time=0,
                    server_used="none"
                )
            
            # Load and execute the tool
            result = await self._execute_server_tool(server_id, request.tool_name, request.parameters)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return MCPToolResponse(
                success=True,
                data=result,
                execution_time=execution_time,
                server_used=server_id
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Tool execution failed: {e}")
            
            return MCPToolResponse(
                success=False,
                error=str(e),
                execution_time=execution_time,
                server_used=request.server_id or "unknown"
            )
    
    def _find_server_for_tool(self, tool_name: str, preferred_server: Optional[str] = None) -> Optional[str]:
        """Find which server implements a specific tool."""
        if preferred_server and preferred_server in self.registry.servers:
            server_config = self.registry.servers[preferred_server]
            if tool_name in server_config["tools"]:
                return preferred_server
        
        # Search all servers
        for server_id, config in self.registry.servers.items():
            if tool_name in config["tools"]:
                return server_id
        
        return None
    
    async def _execute_server_tool(self, server_id: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool on a specific server."""
        # For demo purposes, we'll simulate tool execution
        # In production, this would dynamically import and call the actual MCP server functions
        
        server_config = self.registry.servers[server_id]
        
        # Mock responses for demonstration
        if server_id == "travel-booking":
            return await self._execute_travel_booking_tool(tool_name, parameters)
        elif server_id == "enhanced-memory":
            return await self._execute_memory_tool(tool_name, parameters)
        elif server_id == "auto-accept":
            return await self._execute_auto_accept_tool(tool_name, parameters)
        elif server_id == "visual-debugging":
            return await self._execute_visual_debug_tool(tool_name, parameters)
        else:
            raise ValueError(f"Unknown server: {server_id}")
    
    async def _execute_travel_booking_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute travel booking tools."""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if tool_name == "search_accommodations":
            return {
                "search_id": f"remote_search_{int(asyncio.get_event_loop().time())}",
                "destination": parameters.get("destination", "Unknown"),
                "accommodations": [
                    {
                        "name": "Remote Hotel Example",
                        "price_per_night": 120.0,
                        "currency": "USD",
                        "rating": 8.5,
                        "platform": "booking.com",
                        "booking_url": "https://booking.com/example"
                    }
                ],
                "total_results": 1,
                "note": "This is a remote MCP server response!",
                "accessed_via": "HTTP Gateway"
            }
        
        elif tool_name == "search_accommodations_with_airbnb":
            return {
                "search_type": "integrated_multi_mcp_remote",
                "traditional_results": {"accommodations": []},
                "integrated_results": {
                    "accommodations": [
                        {
                            "name": "Remote Airbnb Example",
                            "platform": "airbnb",
                            "price_per_night": 85.0,
                            "booking_url": "https://airbnb.com/rooms/example"
                        }
                    ],
                    "mcp_servers_used": ["firecrawl", "agenticseek"]
                },
                "summary": {
                    "airbnb_included": parameters.get("include_airbnb", False),
                    "total_accommodations": 1
                },
                "note": "Remote multi-MCP integration working!"
            }
        
        else:
            return {"message": f"Tool {tool_name} executed remotely", "parameters": parameters}
    
    async def _execute_memory_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced memory tools."""
        await asyncio.sleep(0.1)
        
        return {
            "tool": tool_name,
            "status": "executed_remotely",
            "memory_system": "enhanced-memory-mcp",
            "result": f"Remote execution of {tool_name} with parameters: {parameters}"
        }
    
    async def _execute_auto_accept_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute auto-accept tools."""
        await asyncio.sleep(0.1)
        
        return {
            "tool": tool_name,
            "status": "executed_remotely", 
            "auto_accept_system": "autonomous-coding-mcp",
            "result": f"Remote execution of {tool_name} with parameters: {parameters}"
        }
    
    async def _execute_visual_debug_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute visual debugging tools."""
        await asyncio.sleep(0.1)
        
        return {
            "tool": tool_name,
            "status": "executed_remotely",
            "visual_debug_system": "infrastructure-analysis-mcp", 
            "result": f"Remote execution of {tool_name} with parameters: {parameters}"
        }

# Global executor instance
executor = MCPToolExecutor(registry)

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """API documentation homepage."""
    return """
    <html>
        <head>
            <title>Remote MCP Gateway</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .server { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
                .tools { color: #666; }
                .endpoint { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h1>🌐 Remote MCP Gateway</h1>
            <p>Your MCP skills are now accessible from anywhere!</p>
            
            <h2>📡 Available Endpoints</h2>
            <div class="endpoint">GET /api/v1/servers - List all MCP servers</div>
            <div class="endpoint">GET /api/v1/tools - List all available tools</div>
            <div class="endpoint">POST /api/v1/execute - Execute any MCP tool</div>
            <div class="endpoint">WebSocket /ws - Real-time MCP communication</div>
            
            <h2>📚 Interactive Documentation</h2>
            <p><a href="/docs">Swagger UI Documentation</a> | <a href="/redoc">ReDoc Documentation</a></p>
            
            <h2>🎯 Example Usage</h2>
            <pre><code>
# Search accommodations from your phone
curl -X POST "https://your-gateway.com/api/v1/execute" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tool_name": "search_accommodations",
    "parameters": {
      "destination": "Paris",
      "check_in": "2025-07-15",
      "check_out": "2025-07-18",
      "guests": 2
    }
  }'
            </code></pre>
        </body>
    </html>
    """

@app.get("/api/v1/servers", response_model=List[ServerStatus])
async def list_servers():
    """List all available MCP servers."""
    return registry.list_servers()

@app.get("/api/v1/tools")
async def list_tools():
    """List all available tools across all servers."""
    return {
        "tools_by_server": registry.get_all_tools(),
        "total_servers": len(registry.servers),
        "total_tools": sum(len(tools) for tools in registry.get_all_tools().values())
    }

@app.get("/api/v1/servers/{server_id}")
async def get_server_info(server_id: str):
    """Get detailed information about a specific server."""
    server_info = registry.get_server_info(server_id)
    if not server_info:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")
    return server_info

@app.post("/api/v1/execute", response_model=MCPToolResponse)
async def execute_tool(request: MCPToolRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Execute any MCP tool remotely."""
    logger.info(f"Executing tool: {request.tool_name} with parameters: {request.parameters}")
    
    # Optional authentication check
    # if credentials and not verify_auth_token(credentials.credentials):
    #     raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    response = await executor.execute_tool(request)
    
    logger.info(f"Tool execution result: success={response.success}, time={response.execution_time:.3f}s")
    
    return response

# Travel Booking Specific Endpoints (for convenience)
@app.post("/api/v1/travel/search")
async def travel_search(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    include_airbnb: bool = False
):
    """Convenience endpoint for travel booking search."""
    tool_name = "search_accommodations_with_airbnb" if include_airbnb else "search_accommodations"
    
    request = MCPToolRequest(
        tool_name=tool_name,
        parameters={
            "destination": destination,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "include_airbnb": include_airbnb
        },
        server_id="travel-booking"
    )
    
    return await executor.execute_tool(request)

@app.post("/api/v1/travel/recommendations")
async def travel_recommendations(
    destination: str,
    travel_purpose: str = "leisure",
    duration: int = 3,
    budget_level: str = "moderate"
):
    """Get AI-powered travel recommendations."""
    request = MCPToolRequest(
        tool_name="get_smart_travel_recommendations",
        parameters={
            "destination": destination,
            "travel_purpose": travel_purpose,
            "duration": duration,
            "budget_level": budget_level
        },
        server_id="travel-booking"
    )
    
    return await executor.execute_tool(request)

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP communication."""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Execute tool request
            request = MCPToolRequest(**message)
            response = await executor.execute_tool(request)
            
            # Send response
            await websocket.send_text(response.json())
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "servers": len(registry.servers),
        "gateway_version": "1.0.0"
    }

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Remote MCP Gateway on {host}:{port}")
    logger.info(f"Available servers: {list(registry.servers.keys())}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )