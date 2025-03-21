import json
import logging
import os
import sys
import struct
from datetime import datetime

import pyautogui
from PIL import Image

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "basic_mcp_server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("basic_mcp_server")

# Create screenshots directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
    logger.info(f"Created screenshots directory at {screenshots_dir}")

# Capture screenshot
def capture_screenshot(name=None, width=800, height=600):
    try:
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        
        # Get image dimensions
        width, height = screenshot.size
        
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
            "width": width,
            "height": height,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
        return {"error": str(e)}

# Handle initialize request
def handle_initialize(message_id, params):
    logger.info(f"Handling initialize request with params: {params}")
    protocol_version = params.get("protocolVersion", "2024-11-05")
    client_info = params.get("clientInfo", {})
    logger.info(f"Client info: {client_info}, Protocol version: {protocol_version}")
    
    # Respond with proper capabilities format
    response = {
        "jsonrpc": "2.0",
        "id": message_id,
        "result": {
            "capabilities": {
                "tools": {
                    "supportsToolCalls": True
                }
            },
            "serverInfo": {
                "name": "Puppeteer MCP Server",
                "version": "1.0.0"
            }
        }
    }
    logger.info(f"Sending initialize response: {json.dumps(response)}")
    return response

# Handle tools/list request
def handle_tools_list(message_id):
    logger.info("Handling tools/list request")
    
    # Define the screenshot tool with proper schema
    tools = [
        {
            "name": "mcp2_puppeteer_screenshot",
            "description": "Take a screenshot of the current page or a specific element",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element to screenshot"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the screenshot"
                    },
                    "width": {
                        "type": "number",
                        "description": "Width in pixels (default: 800)"
                    },
                    "height": {
                        "type": "number",
                        "description": "Height in pixels (default: 600)"
                    }
                }
            }
        }
    ]
    
    response = {
        "jsonrpc": "2.0",
        "id": message_id,
        "result": {"tools": tools}
    }
    
    logger.info(f"Sending tools/list response: {json.dumps(response)}")
    return response

# Handle tools/call request
def handle_tools_call(message_id, params):
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
    
    if tool_name == "mcp2_puppeteer_screenshot":
        try:
            # Extract parameters
            name = arguments.get("name")
            width = arguments.get("width", 800)
            height = arguments.get("height", 600)
            
            # Capture screenshot
            result = capture_screenshot(name, width, height)
            
            if "error" in result:
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32000,
                        "message": result["error"]
                    }
                }
            
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
                            "text": f"Screenshot captured. Dimensions: {result['width']}x{result['height']}"
                        }
                    ]
                }
            }
            logger.info(f"Sending screenshot response: {json.dumps(response)}")
            return response
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

# Handle message
def handle_message(message):
    try:
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params", {})
        
        logger.info(f"Handling method: {method} with id: {message_id}")
        
        if method == "initialize":
            return handle_initialize(message_id, params)
        elif method == "tools/list":
            return handle_tools_list(message_id)
        elif method == "tools/call":
            return handle_tools_call(message_id, params)
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
                "code": -32000,
                "message": str(e)
            }
        }

def read_message(stdin):
    """Read a message from stdin using the MCP binary protocol."""
    try:
        # Read the 4-byte header (uint32 little-endian)
        header = stdin.read(4)
        if not header or len(header) < 4:
            logger.info("End of input stream")
            return None
            
        # Interpret the header as message length
        message_len = struct.unpack("<I", header)[0]
        logger.debug(f"Message length from header: {message_len}")
        
        # Sanity check on message length
        if message_len > 10 * 1024 * 1024:  # 10 MB limit
            logger.error(f"Message too large: {message_len} bytes")
            return None
            
        # Read the message content
        content = stdin.read(message_len)
        if not content or len(content) < message_len:
            logger.error(f"Incomplete message: expected {message_len} bytes, got {len(content) if content else 0}")
            return None
            
        # Parse JSON content
        message = json.loads(content.decode('utf-8'))
        return message
    except struct.error as e:
        logger.error(f"Failed to unpack message header: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading message: {e}")
        return None

def write_message(stdout, message):
    """Write a message to stdout using the MCP binary protocol."""
    try:
        # Convert message to JSON string and encode to bytes
        message_bytes = json.dumps(message).encode('utf-8')
        message_len = len(message_bytes)
        
        # Write 4-byte header (uint32 little-endian) containing message length
        stdout.write(struct.pack("<I", message_len))
        
        # Write message content
        stdout.write(message_bytes)
        stdout.flush()
        logger.debug(f"Wrote message of length {message_len} bytes")
        return True
    except Exception as e:
        logger.error(f"Error writing message: {e}")
        return False

def main():
    # Signal that we're ready
    logger.info("MCP Server is ready")
    print("MCP SERVER READY", file=sys.stderr)
    sys.stderr.flush()
    
    # Use binary mode for stdin/stdout
    stdin = os.fdopen(sys.stdin.fileno(), 'rb')
    stdout = os.fdopen(sys.stdout.fileno(), 'wb')
    
    try:
        while True:
            # Read message
            message = read_message(stdin)
            if message is None:
                # Error reading message or end of stream
                continue
                
            logger.debug(f"Received message: {json.dumps(message)}")
            
            # Handle message
            response = handle_message(message)
            
            # Write response
            if not write_message(stdout, response):
                logger.error("Failed to write response")
                
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
