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
from http.server import HTTPServer, BaseHTTPRequestHandler

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("screenshot_server.log")
    ]
)
logger = logging.getLogger("screenshot_server")

# Create screenshots directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
    logger.info(f"Created screenshots directory at {screenshots_dir}")

# Capture screenshot
def capture_screenshot(full_screen=True, region=None):
    try:
        # Capture screenshot
        if full_screen:
            screenshot = pyautogui.screenshot()
        else:
            if region is None:
                region = [0, 0, 800, 600]  # Default region
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
        return {"error": str(e)}

class MCPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self._set_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode())
            logger.info(f"Received request: {request}")
            
            method = request.get("method")
            message_id = request.get("id")
            
            # Handle initialize method
            if method == "initialize":
                logger.debug("Handling initialize request")
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "capabilities": {},
                        "serverInfo": {
                            "name": "Simple MCP Screenshot Server",
                            "version": "1.0.0"
                        }
                    }
                }
                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
                logger.info("Sent initialize response")
            
            # Handle tools/list method
            elif method == "tools/list":
                logger.debug("Handling tools/list request")
                response = {
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
                }
                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
                logger.info("Sent tools/list response")
            
            # Handle tools/call method
            elif method == "tools/call":
                logger.debug("Handling tools/call request")
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
                
                if tool_name == "screenshot":
                    try:
                        # Capture screenshot
                        full_screen = arguments.get("full_screen", True)
                        region = arguments.get("region")
                        result = capture_screenshot(full_screen, region)
                        
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
                        self._set_headers()
                        self.wfile.write(json.dumps(response).encode())
                        logger.info("Sent screenshot response")
                    except Exception as e:
                        logger.error(f"Error executing screenshot tool: {str(e)}", exc_info=True)
                        response = {
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "error": {
                                "code": -32000,
                                "message": str(e)
                            }
                        }
                        self._set_headers()
                        self.wfile.write(json.dumps(response).encode())
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
                    response = {
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
                    self._set_headers()
                    self.wfile.write(json.dumps(response).encode())
            
            # Handle unknown methods
            else:
                logger.warning(f"Unknown method: {method}")
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error"
                }
            }
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())

def run_server(host="127.0.0.1", port=8765):  
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    logger.info(f"Starting HTTP MCP server on {host}:{port}")
    print("MCP SERVER READY", file=sys.stderr)
    sys.stderr.flush()
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
