#!/usr/bin/env python3
"""
Windows-Compatible Fixed Claude Desktop Agent MCP Server
Provides screenshot capabilities with proper MCP protocol implementation for Windows
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
import threading
import queue

import pyautogui
from PIL import Image

# Setup logging to file only (not stderr to avoid MCP protocol conflicts)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "windows_fixed_mcp_server.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("windows_fixed_mcp_server")

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
        
    def capture_screenshot(self, name: Optional[str] = None, width: int = 1920, height: int = 1080) -> Dict[str, Any]:
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

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
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

    def handle_tools_list(self) -> Dict[str, Any]:
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

    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
                result = self.capture_screenshot(name, width, height)
                
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

    def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP message."""
        try:
            method = message.get("method")
            message_id = message.get("id")
            params = message.get("params", {})
            
            logger.info(f"Handling method: {method} with id: {message_id}")
            
            if method == "initialize":
                result = self.handle_initialize(params)
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": result
                }
            elif method == "tools/list":
                result = self.handle_tools_list()
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": result
                }
            elif method == "tools/call":
                result = self.handle_tools_call(params)
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

def read_stdin():
    """Read from stdin in a blocking manner."""
    try:
        for line in sys.stdin:
            line = line.strip()
            if line:
                yield line
    except Exception as e:
        logger.error(f"Error reading stdin: {e}")

def main():
    """Main server loop for Windows."""
    logger.info("Starting Windows-Compatible Fixed MCP Server")
    
    # Create MCP server instance
    server = MCPServer()
    
    logger.info("MCP Server ready for connections")
    
    # Set stdout to binary mode on Windows to avoid encoding issues
    if sys.platform == "win32":
        import msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    
    try:
        # Read messages from stdin
        for line in read_stdin():
            try:
                # Parse JSON message
                message = json.loads(line)
                logger.debug(f"Received message: {json.dumps(message)}")
                
                # Handle message
                response = server.handle_message(message)
                
                # Write response if needed
                if response is not None:
                    response_json = json.dumps(response) + '\n'
                    sys.stdout.buffer.write(response_json.encode('utf-8'))
                    sys.stdout.buffer.flush()
                    logger.debug(f"Sent response: {response_json.strip()}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e} - Line: {line}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": 0,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                error_json = json.dumps(error_response) + '\n'
                sys.stdout.buffer.write(error_json.encode('utf-8'))
                sys.stdout.buffer.flush()
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        return 1
    
    logger.info("MCP Server shutting down")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
