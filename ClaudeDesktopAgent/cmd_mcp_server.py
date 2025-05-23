import asyncio
import json
import logging
import os
import sys
import base64
import io
from datetime import datetime
from typing import Dict, Any, List, Optional

import pyautogui
from PIL import Image
import websockets

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_server.log")
    ]
)
logger = logging.getLogger("cmd_mcp_server")

# Create screenshots directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
    logger.info(f"Created screenshots directory at {screenshots_dir}")

# Screenshot tool implementation
async def capture_screenshot(full_screen: bool = True, region: Optional[List[int]] = None) -> Dict[str, Any]:
    """Capture a screenshot of the desktop or a specific region"""
    try:
        # Capture screenshot
        if full_screen:
            screenshot = pyautogui.screenshot()
        else:
            if region is None:
                raise ValueError("Region must be specified when full_screen is False")
            if len(region) != 4:
                raise ValueError("Region must be a list of 4 integers [left, top, width, height]")
            screenshot = pyautogui.screenshot(region=tuple(region))
        
        # Get image dimensions
        width, height = screenshot.size
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Save screenshot to file
        filename = f"screenshot_{timestamp.replace(':', '-').replace('.', '-')}.png"
        filepath = os.path.join(screenshots_dir, filename)
        screenshot.save(filepath)
        logger.info(f"Saved screenshot to {filepath}")
        
        # Convert to base64
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image_data": img_str,
            "width": width,
            "height": height,
            "timestamp": timestamp,
            "file_path": filepath
        }
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
        raise

# WebSocket handler
async def handle_client(websocket, path):
    logger.info("WebSocket connection established")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"Received message: {data}")
                
                # Extract message details
                method = data.get("method")
                message_id = data.get("id")
                
                # Handle initialize method
                if method == "initialize":
                    logger.debug("Handling initialize request")
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": {
                            "capabilities": {},
                            "serverInfo": {
                                "name": "Simple MCP Screenshot Server",
                                "version": "1.0.0"
                            }
                        }
                    }))
                    logger.info("Sent initialize response")
                
                # Handle tools/list method
                elif method == "tools/list":
                    logger.debug("Handling tools/list request")
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "screenshot",
                                    "description": "Capture a screenshot of the screen",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "full_screen": {
                                                "type": "boolean",
                                                "description": "Whether to capture the full screen or a specific region",
                                                "default": True
                                            },
                                            "region": {
                                                "type": "array",
                                                "items": {"type": "integer"},
                                                "description": "Region to capture [x, y, width, height]"
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }))
                    logger.info("Sent tools/list response")
                
                # Handle tools/call method
                elif method == "tools/call":
                    logger.debug("Handling tools/call request")
                    params = data.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
                    
                    if tool_name == "screenshot":
                        try:
                            # Capture screenshot
                            full_screen = arguments.get("full_screen", True)
                            region = arguments.get("region")
                            result = await capture_screenshot(full_screen, region)
                            
                            # Send response
                            response = {
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
                            }
                            logger.debug(f"Sending response: {json.dumps(response)}")
                            await websocket.send(json.dumps(response))
                            logger.info("Sent screenshot response")
                        except Exception as e:
                            logger.error(f"Error executing screenshot tool: {str(e)}", exc_info=True)
                            await websocket.send(json.dumps({
                                "jsonrpc": "2.0",
                                "id": message_id,
                                "error": {
                                    "code": -32000,
                                    "message": str(e)
                                }
                            }))
                    else:
                        logger.warning(f"Unknown tool: {tool_name}")
                        await websocket.send(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "error": {
                                "code": -32601,
                                "message": f"Tool not found: {tool_name}"
                            }
                        }))
                
                # Handle unknown methods
                else:
                    logger.warning(f"Unknown method: {method}")
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }))
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)

# Run the server
async def main():
    host = "127.0.0.1"
    port = 8095  # Changed from 8090 to avoid conflicts
    logger.info(f"Starting WebSocket MCP server on {host}:{port}")
    
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"Server started successfully on {host}:{port}")
    
    # Print a message that Claude Desktop can parse
    print("MCP SERVER READY")
    sys.stdout.flush()
    
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)
