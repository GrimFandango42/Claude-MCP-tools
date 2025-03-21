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
from app.mcp.tools import ScreenshotTool, AnalyzeScreenshotTool

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
    "screenshot": screenshot_tool
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
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "Claude Desktop Custom MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }))
            
            elif method == "tools/list":
                # List available tools
                tool_list = []
                
                # Add screenshot tool
                tool_list.append({
                    "name": "screenshot",
                    "description": "Capture a screenshot of the screen",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "full_screen": {
                                "type": "boolean",
                                "description": "Whether to capture the full screen or a specific region"
                            },
                            "region": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Region to capture [x, y, width, height]"
                            }
                        }
                    }
                })
                
                # Add analyze_screenshot tool if available
                if analyze_screenshot_tool:
                    tool_list.append({
                        "name": "analyze_screenshot",
                        "description": "Analyze a screenshot using Claude Vision API",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "image_path": {
                                    "type": "string",
                                    "description": "Path to the image file to analyze"
                                },
                                "prompt": {
                                    "type": "string",
                                    "description": "Prompt to send to Claude Vision API"
                                }
                            },
                            "required": ["image_path"]
                        }
                    })
                
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
                    result = await tool.execute(**arguments)
                    
                    # Convert result to MCP response format
                    if tool_name == "screenshot":
                        # Return image content
                        await websocket.send_text(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "image",
                                        "url": f"file://{result['file_path']}",
                                        "mime_type": "image/png"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"Screenshot captured at {result['timestamp']}. Dimensions: {result['width']}x{result['height']}"
                                    }
                                ]
                            }
                        }))
                    elif tool_name == "analyze_screenshot":
                        # Return text content
                        await websocket.send_text(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": result['analysis']
                                    }
                                ]
                            }
                        }))
                    else:
                        # Generic response
                        await websocket.send_text(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": str(result)
                                    }
                                ]
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
        "description": "Custom MCP server for Claude Desktop with screenshot capabilities"
    }
