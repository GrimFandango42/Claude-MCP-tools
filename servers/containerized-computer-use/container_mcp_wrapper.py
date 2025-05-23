#!/usr/bin/env python3
"""
MCP Server Wrapper for Containerized Computer Use
Handles JSON-RPC communication and delegates to the Computer Use API
"""

import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from computer_use_container import ContainerizedComputerUseAPI

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='[container-mcp] %(asctime)s - %(message)s',
    stream=sys.stderr
)


class ContainerMCPServer:
    """MCP Server implementation for containerized Computer Use."""
    
    def __init__(self):
        self.api = ContainerizedComputerUseAPI()
        self.running = True
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC requests."""
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        logging.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "0.1.0",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "containerized-computer-use",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "computer_20250124",
                                "description": "Control computer with actions: screenshot, mouse, keyboard, etc.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {
                                            "type": "string",
                                            "enum": ["screenshot", "key", "type", "mouse_move", "left_click", 
                                                   "right_click", "middle_click", "double_click", "triple_click",
                                                   "left_click_drag", "scroll", "wait", "cursor_position",
                                                   "left_mouse_down", "left_mouse_up", "hold_key"]
                                        },
                                        "coordinate": {"type": "array", "items": {"type": "integer"}},
                                        "text": {"type": "string"},
                                        "start_coordinate": {"type": "array", "items": {"type": "integer"}},
                                        "end_coordinate": {"type": "array", "items": {"type": "integer"}},
                                        "direction": {"type": "string", "enum": ["up", "down"]},
                                        "clicks": {"type": "integer"},
                                        "duration": {"type": "integer"}
                                    },
                                    "required": ["action"]
                                }
                            },
                            {
                                "name": "text_editor_20250429",
                                "description": "View and edit text files",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {
                                            "type": "string",
                                            "enum": ["view", "create", "str_replace"]
                                        },
                                        "path": {"type": "string"},
                                        "file_text": {"type": "string"},
                                        "old_str": {"type": "string"},
                                        "new_str": {"type": "string"},
                                        "view_range": {"type": "array", "items": {"type": "integer"}}
                                    },
                                    "required": ["command"]
                                }
                            },
                            {
                                "name": "bash_20250124",
                                "description": "Execute bash commands",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string"}
                                    },
                                    "required": ["command"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "computer_20250124":
                    result = self.api.computer_20250124(**arguments)
                elif tool_name == "text_editor_20250429":
                    result = self.api.text_editor_20250429(**arguments)
                elif tool_name == "bash_20250124":
                    result = self.api.bash_20250124(**arguments)
                else:
                    result = {"output": f"ERROR: Unknown tool: {tool_name}"}
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result.get("output", "")
                            }
                        ] + ([{
                            "type": "image",
                            "data": result["screenshot"]
                        }] if "screenshot" in result else [])
                    }
                }
            
            elif method == "resources/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"resources": []}
                }
            
            elif method == "prompts/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"prompts": []}
                }
                
            elif method == "shutdown":
                self.running = False
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logging.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Main server loop."""
        logging.info("Container MCP Server starting...")
        
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        
        while self.running:
            try:
                # Read line from stdin
                line = await reader.readline()
                if not line:
                    break
                
                # Parse JSON-RPC request
                request = json.loads(line.decode())
                
                # Handle request
                response = await self.handle_request(request)
                
                # Send response
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logging.error(f"Server error: {e}")
        
        logging.info("Container MCP Server shutting down...")


async def main():
    """Entry point."""
    server = ContainerMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
