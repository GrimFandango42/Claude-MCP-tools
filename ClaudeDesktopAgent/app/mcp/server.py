import json
import logging
import asyncio
from fastapi import FastAPI, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
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
execute_shell_command_tool = ExecuteShellCommandTool() # New tool

# Get Anthropic API key from environment variables
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_api_url = "https://api.anthropic.com/v1/messages"

# Initialize analyze screenshot tool if API key is available
if anthropic_api_key:
    analyze_screenshot_tool = AnalyzeScreenshotTool(anthropic_api_key, anthropic_api_url)
    logger.info("Initialized AnalyzeScreenshotTool with Anthropic API key")
else:
    analyze_screenshot_tool = None
    logger.warning("ANTHROPIC_API_KEY not found, AnalyzeScreenshotTool will not be available")

# Register all tools
tools = {
    "screenshot": screenshot_tool,
    "execute_shell_command": execute_shell_command_tool # New tool registered
}

# Add analyze_screenshot_tool if available
if analyze_screenshot_tool:
    tools["analyze_screenshot"] = analyze_screenshot_tool

# MCP Protocol Implementation
@mcp_app.websocket("/")
async def mcp_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received message: {message}")
            
            # Handle message based on method
            method = message.get("method")
            message_id = message.get("id")
            
            if method == "initialize":
                # Handle initialization
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "capabilities": {
                            "tools": {} # Standard capabilities, tools are listed via tools/list
                        },
                        "serverInfo": {
                            "name": "Claude Desktop Custom MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }))
            
            elif method == "tools/list":
                # List available tools by fetching their schemas
                tool_list = []
                for tool_instance in tools.values():
                    tool_list.append(tool_instance.get_schema()) # Using get_schema() from BaseTool
                
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "tools": tool_list
                    }
                }))
            
            elif method == "tools/call":
                # Call a tool
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
                
                if tool_name not in tools:
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }))
                    continue
                
                try:
                    tool = tools[tool_name]
                    result_data = await tool.execute(**arguments) # result_data is the direct output from tool.execute
                    
                    # Construct the MCP result content.
                    # For execute_shell_command, the result_data is already the dictionary we want to send.
                    # For others, it might need specific formatting.
                    
                    content_items = []
                    if tool_name == "screenshot":
                        content_items = [
                            {
                                "type": "image",
                                "url": f"file://{result_data['file_path']}", # Assuming file_path is in result_data
                                "mime_type": "image/png"
                            },
                            {
                                "type": "text",
                                "text": f"Screenshot captured at {result_data['timestamp']}. Dimensions: {result_data['width']}x{result_data['height']}"
                            }
                        ]
                    elif tool_name == "analyze_screenshot":
                         content_items = [
                            {
                                "type": "text",
                                "text": result_data.get('description', 'Analysis complete.') # Use .get for safety
                            }
                        ]
                    elif tool_name == "execute_shell_command":
                        # The result_data from ExecuteShellCommandTool is already the desired JSON object
                        # We can wrap it in a text block or send as structured data if MCP spec allows
                        # For simplicity, sending stdout and stderr as text, and success/return_code as part of a structured message.
                        # The prompt asks for the tool's return to be the direct dictionary.
                        # MCP's "result" field can be any JSON value. So we can directly pass it.
                        # However, the example responses for other tools wrap results in a "content" list.
                        # Let's be consistent if possible, or just return the raw dict if that's simpler.
                        # The prompt's return schema for the tool itself IS the dict.
                        # The MCP spec for "tools/call" usually expects a "result" that could be this dict.
                        # Let's assume the result of the tool call is the direct dictionary from execute_command.
                         await websocket.send_text(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "result": result_data # Directly sending the tool's output dict
                        }))
                         continue # Skip generic response packaging
                    else:
                        # Generic response for other tools if any
                        content_items = [
                            {
                                "type": "text",
                                "text": str(result_data)
                            }
                        ]

                    # If not execute_shell_command (which has its own send_text above)
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": {
                            "content": content_items
                        }
                    }))

                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32000,
                            "message": str(e)
                        }
                    }))
            
            else:
                # Unknown method
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

# HTTP endpoints for health check and info
@mcp_app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

@mcp_app.get("/info")
async def server_info() -> Dict[str, Any]:
    """Server information endpoint"""
    return {
        "name": "Claude Desktop Custom MCP Server",
        "version": "1.0.0",
        "description": "Custom MCP server for Claude Desktop with screenshot and shell command capabilities"
    }
