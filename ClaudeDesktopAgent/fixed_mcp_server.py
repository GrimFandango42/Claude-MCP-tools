#!/usr/bin/env python3
"""
Fixed Claude Desktop Agent MCP Server
Provides screenshot capabilities with proper MCP protocol implementation
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import pyautogui
from PIL import Image

# Setup logging to file only (not stderr to avoid MCP protocol conflicts)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixed_mcp_server.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("fixed_mcp_server")

# Create screenshots directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
    logger.info(f"Created screenshots directory at {screenshots_dir}")

class MCPServer:
    def __init__(self):
        self.capabilities = {
            "tools": {},
            "prompts": {},
            "resources": {}
        }
        
    async def capture_screenshot(self, name: Optional[str] = None, width: int = 1920, height: int = 1080) -> Dict[str, Any]:
        """Capture a screenshot and save to file."""
        try:
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
            # Get image dimensions
            img_width, img_height = screenshot.size
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            
            # Save screenshot to file
            if name:
                filename = f"{name}_{timestamp}.png"
            else:
                filename = f"screenshot_{timestamp}.png"
                
            filepath = os.path.join(screenshots_dir, filename)
            screenshot.save(filepath)
            logger.info(f"Saved screenshot to {filepath}")
            
            return {
                "file_path": filepath,
                "width": img_width,
                "height": img_height,
                "timestamp": timestamp,
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
            raise e

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        logger.info(f"Handling initialize request with params: {params}")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "claude-desktop-agent",
                "version": "1.0.0"
            }
        }

    async def handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools/list request."""
        logger.info("Handling tools/list request")
        
        tools = [
            {
                "name": "take_screenshot",
                "description": "Take a screenshot of the current desktop",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Optional name for the screenshot file"
                        },
                        "width": {
                            "type": "integer",
                            "description": "Width in pixels (default: 1920)",
                            "default": 1920
                        },
                        "height": {
                            "type": "integer",
                            "description": "Height in pixels (default: 1080)",
                            "default": 1080
                        }
                    }
                }
            }
        ]
        
        return {"tools": tools}

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
        
        if tool_name == "take_screenshot":
            try:
                # Extract parameters
                name = arguments.get("name")
                width = arguments.get("width", 1920)
                height = arguments.get("height", 1080)
                
                # Capture screenshot
                result = await self.capture_screenshot(name, width, height)
                
                # Return result
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Screenshot captured successfully!\n"
                                   f"File: {result['filename']}\n"
                                   f"Path: {result['file_path']}\n"
                                   f"Dimensions: {result['width']}x{result['height']}\n"
                                   f"Timestamp: {result['timestamp']}"
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"Error executing screenshot tool: {str(e)}", exc_info=True)
                raise e
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP message."""
        try:
            method = message.get("method")
            message_id = message.get("id")
            params = message.get("params", {})
            
            logger.info(f"Handling method: {method} with id: {message_id}")
            
            if method == "initialize":
                result = await self.handle_initialize(params)
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": result
                }
            elif method == "tools/list":
                result = await self.handle_tools_list()
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": result
                }
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": result
                }
            elif method == "notifications/initialized":
                # No response needed for notifications
                logger.info("Received initialized notification")
                return None
            else:
                logger.warning(f"Unknown method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": message_id if message_id else 0,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

async def read_message(reader: asyncio.StreamReader) -> Optional[Dict[str, Any]]:
    """Read a message from stdin."""
    try:
        # Read line (JSON-RPC over stdio)
        line = await reader.readline()
        if not line:
            return None
            
        line = line.decode('utf-8').strip()
        if not line:
            return None
            
        message = json.loads(line)
        return message
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading message: {e}")
        return None

async def write_message(writer: asyncio.StreamWriter, message: Dict[str, Any]) -> bool:
    """Write a message to stdout."""
    try:
        # Convert message to JSON string
        message_json = json.dumps(message) + '\n'
        message_bytes = message_json.encode('utf-8')
        
        # Write message
        writer.write(message_bytes)
        await writer.drain()
        logger.debug(f"Wrote message: {message_json.strip()}")
        return True
    except Exception as e:
        logger.error(f"Error writing message: {e}")
        return False

async def main():
    """Main server loop."""
    logger.info("Starting Fixed MCP Server")
    
    # Create MCP server instance
    server = MCPServer()
    
    # Setup stdin/stdout streams
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())
    
    logger.info("MCP Server ready for connections")
    
    try:
        while True:
            # Read message
            message = await read_message(reader)
            if message is None:
                # EOF or error
                break
                
            logger.debug(f"Received message: {json.dumps(message)}")
            
            # Handle message
            response = await server.handle_message(message)
            
            # Write response if needed
            if response is not None:
                if not await write_message(writer, response):
                    logger.error("Failed to write response")
                    
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        return 1
    
    logger.info("MCP Server shutting down")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
