import asyncio
import base64
import io
import json
import logging
import os
import sys
from datetime import datetime

import pyautogui
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_screenshot.log")
    ]
)
logger = logging.getLogger("mcp_screenshot")

# Create screenshots directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
    logger.info(f"Created screenshots directory at {screenshots_dir}")

# Function to capture screenshot
def capture_screenshot(full_screen=True, region=None):
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
        
        return {
            "file_path": filepath,
            "width": width,
            "height": height,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
        raise

# MCP Server implementation
class MCPServer:
    def __init__(self):
        self.tools = {
            "screenshot": {
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
        }
    
    async def handle_initialize(self, message_id):
        logger.info("Handling initialize request")
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "capabilities": {},
                "serverInfo": {
                    "name": "MCP Screenshot Server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_tools_list(self, message_id):
        logger.info("Handling tools/list request")
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            })
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {"tools": tools_list}
        }
    
    async def handle_tools_call(self, message_id, params):
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
        
        if tool_name == "screenshot":
            try:
                full_screen = arguments.get("full_screen", True)
                region = arguments.get("region")
                result = capture_screenshot(full_screen, region)
                
                return {
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
            except Exception as e:
                logger.error(f"Error executing screenshot tool: {str(e)}", exc_info=True)
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }
        else:
            logger.warning(f"Unknown tool: {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }
    
    async def handle_message(self, message):
        try:
            method = message.get("method")
            message_id = message.get("id")
            
            if method == "initialize":
                return await self.handle_initialize(message_id)
            elif method == "tools/list":
                return await self.handle_tools_list(message_id)
            elif method == "tools/call":
                params = message.get("params", {})
                return await self.handle_tools_call(message_id, params)
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
                "id": message_id if 'message_id' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error"
                }
            }

async def main():
    # Create MCP server instance
    mcp_server = MCPServer()
    
    # Signal that we're ready
    print("MCP SERVER READY", file=sys.stderr)
    sys.stderr.flush()
    
    # Read from stdin and write to stdout
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())
    
    # Process messages
    while True:
        try:
            # Read message length (4 bytes)
            length_bytes = await reader.read(4)
            if not length_bytes:
                logger.info("End of input, exiting")
                break
            
            # Convert to integer
            length = int.from_bytes(length_bytes, byteorder='little')
            
            # Read message content
            content_bytes = await reader.read(length)
            if not content_bytes:
                logger.info("End of input, exiting")
                break
            
            # Parse message
            content = content_bytes.decode('utf-8')
            logger.debug(f"Received message: {content}")
            message = json.loads(content)
            
            # Handle message
            response = await mcp_server.handle_message(message)
            response_bytes = json.dumps(response).encode('utf-8')
            
            # Write response length and content
            writer.write(len(response_bytes).to_bytes(4, byteorder='little'))
            writer.write(response_bytes)
            await writer.drain()
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        sys.exit(1)
