import json
import logging
import asyncio
from fastapi import FastAPI, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field # type: ignore 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import tools
from app.mcp.tools import ScreenshotTool, AnalyzeScreenshotTool, ExecuteShellCommandTool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Create FastAPI app
mcp_app = FastAPI(
    title="Claude Desktop MCP Server",
    description="Model Context Protocol server for Claude Desktop",
    version="1.0.0"
)

# Add CORS middleware
mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools
screenshot_tool = ScreenshotTool()
execute_shell_command_tool = ExecuteShellCommandTool()

# Get Anthropic API key from environment variables
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_api_url = "https://api.anthropic.com/v1/messages"

# Initialize analyze screenshot tool if API key is available
analyze_screenshot_tool_instance = None # Ensure it's defined
if anthropic_api_key:
    analyze_screenshot_tool_instance = AnalyzeScreenshotTool(anthropic_api_key, anthropic_api_url)
    logger.info("Initialized AnalyzeScreenshotTool with Anthropic API key")
else:
    logger.warning("ANTHROPIC_API_KEY not found, AnalyzeScreenshotTool will not be available")

# Register all tools
tools: Dict[str, Any] = { # Explicitly type tools
    "screenshot": screenshot_tool,
    "execute_shell_command": execute_shell_command_tool
}

if analyze_screenshot_tool_instance: # Check the instance, not the class
    tools["analyze_screenshot"] = analyze_screenshot_tool_instance

# --- Functions for HTTP MCP Route ---
async def get_tools() -> Dict[str, Any]:
    """Returns a list of available tool schemas for HTTP endpoint."""
    logger.info("HTTP /tools endpoint called")
    tool_list = []
    for tool_instance in tools.values():
        tool_list.append(tool_instance.get_schema())
    return {"tools": tool_list}

async def handle_mcp_request(request: Request) -> Response:
    """
    Handles an MCP request received over HTTP.
    This is a simplified handler for HTTP; main MCP is via WebSocket.
    """
    logger.info("HTTP MCP request received")
    try:
        message = await request.json()
        method = message.get("method")
        message_id = message.get("id", "http-request") # Default ID for HTTP

        if method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in tools:
                return Response(content=json.dumps({
                    "jsonrpc": "2.0", "id": message_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }), media_type="application/json", status_code=400)

            try:
                tool = tools[tool_name]
                result_data = await tool.execute(**arguments)
                return Response(content=json.dumps({
                    "jsonrpc": "2.0", "id": message_id, "result": result_data
                }), media_type="application/json")
            except Exception as e:
                logger.error(f"Error executing tool {tool_name} via HTTP: {str(e)}", exc_info=True)
                return Response(content=json.dumps({
                    "jsonrpc": "2.0", "id": message_id,
                    "error": {"code": -32000, "message": str(e)}
                }), media_type="application/json", status_code=500)
        else:
            # For other methods like 'initialize', 'tools/list' via HTTP,
            # return method not supported or a generic info.
            # 'tools/list' is handled by its own GET endpoint.
            logger.warning(f"Unsupported HTTP MCP method: {method}")
            return Response(content=json.dumps({
                "jsonrpc": "2.0", "id": message_id,
                "error": {"code": -32601, "message": f"Method '{method}' not fully supported over HTTP for this server. Use WebSocket or specific HTTP endpoints."}
            }), media_type="application/json", status_code=400)

    except json.JSONDecodeError:
        logger.error("HTTP MCP request: Invalid JSON received")
        return Response(content=json.dumps({
            "jsonrpc": "2.0", "id": "unknown",
            "error": {"code": -32700, "message": "Parse error: Invalid JSON."}
        }), media_type="application/json", status_code=400)
    except Exception as e:
        logger.error(f"Generic error in handle_mcp_request (HTTP): {str(e)}", exc_info=True)
        return Response(content=json.dumps({
            "jsonrpc": "2.0", "id": "unknown",
            "error": {"code": -32603, "message": "Internal server error handling HTTP MCP request."}
        }), media_type="application/json", status_code=500)

# --- End Functions for HTTP MCP Route ---


# MCP Protocol Implementation (WebSocket)
@mcp_app.websocket("/")
async def mcp_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received WebSocket message: {message}")
            
            method = message.get("method")
            message_id = message.get("id")
            
            response_payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": message_id}

            if method == "initialize":
                response_payload["result"] = {
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "Claude Desktop Custom MCP Server", "version": "1.0.0"}
                }
            elif method == "tools/list":
                tool_schemas = []
                for tool_instance in tools.values():
                    tool_schemas.append(tool_instance.get_schema())
                response_payload["result"] = {"tools": tool_schemas}
            
            elif method == "tools/call":
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f"Calling tool via WebSocket: {tool_name} with arguments: {arguments}")
                
                if tool_name not in tools:
                    response_payload["error"] = {"code": -32601, "message": f"Tool not found: {tool_name}"}
                else:
                    try:
                        tool = tools[tool_name]
                        result_data = await tool.execute(**arguments)
                        # The ExecuteShellCommandTool returns the exact dict desired for the result.
                        # ScreenshotTool also returns a dict that can be the result.
                        # AnalyzeScreenshotTool also returns a dict.
                        response_payload["result"] = result_data 
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name} via WebSocket: {str(e)}", exc_info=True)
                        response_payload["error"] = {"code": -32000, "message": str(e)}
            else:
                response_payload["error"] = {"code": -32601, "message": f"Method not found: {method}"}
            
            await websocket.send_text(json.dumps(response_payload))
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)
        # Attempt to send error to client if websocket is still open
        try:
            await websocket.send_text(json.dumps({
                "jsonrpc": "2.0", "id": "error-notification", 
                "error": {"code": -32002, "message": f"Unhandled server error: {str(e)}"}
            }))
        except Exception: # nosec
            pass # Ignore if cannot send error


# HTTP endpoints for health check and info (these are part of mcp_app, not the api_router)
@mcp_app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}

@mcp_app.get("/info")
async def server_info() -> Dict[str, Any]:
    return {
        "name": "Claude Desktop Custom MCP Server",
        "version": "1.0.0",
        "description": "Custom MCP server for Claude Desktop with various tools."
    }

# Note: The main app for Uvicorn is `app.main:app` which includes an api_router.
# This mcp_app is usually mounted onto that main app, or `app.main.py` should use this directly.
# For the import in `app.api.routes.mcp.py` to work, these functions need to be available.
# If `app.main.app` is actually `mcp_app`, then the API routes are added to it.
# Let's assume `app.main.app` is this `mcp_app` for now.
# The `uvicorn.run("app.main:app", ...)` in `run.py` refers to the `app` object in `app/main.py`.
# `app/main.py` creates its own FastAPI app and includes `api_router`.
# `api_router` includes the router from `app/api/routes/mcp.py`.
# So `app.mcp.server.py` isn't directly run as the main app, but its functions are imported.
# This means `mcp_app` defined here is not the one Uvicorn runs from `run.py`.
# The functions `get_tools` and `handle_mcp_request` are fine as standalone functions.
# The WebSocket endpoint `@mcp_app.websocket("/")` needs to be on the *actual* app Uvicorn runs.
# This structure is a bit confusing. Let's assume the `api_router` in `app/main.py`
# is meant to include these HTTP MCP handlers.
# The WebSocket endpoint for MCP should be on the main app instance in `app/main.py`.
# For now, providing the functions `get_tools` and `handle_mcp_request` should fix the import error.
# The `mcp_app` FastAPI instance created in this file is distinct from the one in `app/main.py`.
# The `tools` dictionary and helper functions are what's valuable for `app.api.routes.mcp.py`.
