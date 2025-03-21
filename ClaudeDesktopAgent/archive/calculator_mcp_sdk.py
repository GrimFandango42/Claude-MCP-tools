import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculator_mcp_sdk.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("calculator_mcp_sdk")

# Define tool schemas
CALCULATOR_TOOLS = [
    {
        "name": "mcp2_calculator_add",
        "description": "Add two numbers together",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                }
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "mcp2_calculator_subtract",
        "description": "Subtract second number from first number",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                }
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "mcp2_calculator_multiply",
        "description": "Multiply two numbers",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                }
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "mcp2_calculator_divide",
        "description": "Divide first number by second number",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number (dividend)"
                },
                "b": {
                    "type": "number",
                    "description": "Second number (divisor)"
                }
            },
            "required": ["a", "b"]
        }
    }
]

# Helper functions for binary protocol
def read_message_from_stdin():
    """Read a message from stdin using the MCP binary protocol."""
    try:
        # Read the 4-byte header (uint32 little-endian)
        header = sys.stdin.buffer.read(4)
        if not header or len(header) < 4:
            logger.info("End of input stream")
            return None
            
        # Parse content length
        content_length = int.from_bytes(header, byteorder='little')
        logger.debug(f"Reading message with content length: {content_length}")
        
        # Sanity check on message length
        if content_length <= 0 or content_length > 10 * 1024 * 1024:  # 10 MB limit
            logger.error(f"Invalid content length: {content_length}, must be between 1 and 10MB")
            return None
            
        # Read content
        content = sys.stdin.buffer.read(content_length)
        if not content or len(content) < content_length:
            logger.error(f"Invalid content received, expected {content_length} bytes, got {len(content) if content else 0}")
            return None
            
        # Parse JSON
        message = json.loads(content.decode('utf-8'))
        logger.debug(f"Read message: {json.dumps(message)}")
        return message
    except Exception as e:
        logger.error(f"Error reading message: {str(e)}", exc_info=True)
        return None

def write_message_to_stdout(message):
    """Write a message to stdout using the MCP binary protocol."""
    try:
        # Convert message to JSON
        content = json.dumps(message).encode("utf-8")
        content_length = len(content)
        
        # Write header (4 bytes for content length, little-endian)
        header = content_length.to_bytes(4, byteorder='little')
        sys.stdout.buffer.write(header)
        sys.stdout.buffer.write(content)
        sys.stdout.buffer.flush()
        logger.debug(f"Wrote message with content length {content_length}: {json.dumps(message)}")
    except Exception as e:
        logger.error(f"Error writing message: {str(e)}", exc_info=True)

# Handler functions
def handle_initialize(message_id, params):
    """Handle initialize request"""
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
                "name": "Calculator MCP Server",
                "version": "1.0.0"
            }
        }
    }
    logger.info(f"Sending initialize response: {json.dumps(response)}")
    return response

def handle_tools_list(message_id):
    """Handle tools/list request"""
    logger.info("Handling tools/list request")
    
    response = {
        "jsonrpc": "2.0",
        "id": message_id,
        "result": {"tools": CALCULATOR_TOOLS}
    }
    
    logger.info(f"Sending tools/list response: {json.dumps(response)}")
    return response

def handle_tools_call(message_id, params):
    """Handle tools/call request"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
    
    try:
        if tool_name == "mcp2_calculator_add":
            a = float(arguments.get("a", 0))
            b = float(arguments.get("b", 0))
            result = a + b
            operation = "addition"
            equation = f"{a} + {b} = {result}"
            
        elif tool_name == "mcp2_calculator_subtract":
            a = float(arguments.get("a", 0))
            b = float(arguments.get("b", 0))
            result = a - b
            operation = "subtraction"
            equation = f"{a} - {b} = {result}"
            
        elif tool_name == "mcp2_calculator_multiply":
            a = float(arguments.get("a", 0))
            b = float(arguments.get("b", 0))
            result = a * b
            operation = "multiplication"
            equation = f"{a} × {b} = {result}"
            
        elif tool_name == "mcp2_calculator_divide":
            a = float(arguments.get("a", 0))
            b = float(arguments.get("b", 0))
            if b == 0:
                raise ValueError("Cannot divide by zero")
            result = a / b
            operation = "division"
            equation = f"{a} ÷ {b} = {result}"
            
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
        
        # Send response
        response = {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Performed {operation}: {equation}"
                    }
                ]
            }
        }
        logger.info(f"Sending calculator response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error executing calculator tool: {str(e)}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }

def handle_message(message):
    """Handle an incoming message"""
    try:
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params", {})
        
        logger.info(f"Received message: {json.dumps(message)}")
        
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
            "id": message_id if message_id else None,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }

def main():
    """Main function"""
    logger.info("Starting calculator MCP server with SDK-compatible protocol")
    
    try:
        while True:
            # Read message
            message = read_message_from_stdin()
            if not message:
                logger.error("Failed to read message, exiting")
                return 1
                
            # Handle message
            response = handle_message(message)
            if response:
                # Write response
                write_message_to_stdout(response)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, exiting")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
