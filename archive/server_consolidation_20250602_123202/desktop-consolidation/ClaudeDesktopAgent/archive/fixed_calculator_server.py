import json
import logging
import os
import sys
import struct
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixed_calculator_server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fixed_calculator_server")

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
                "name": "Calculator MCP Server",
                "version": "1.0.0"
            }
        }
    }
    logger.info(f"Sending initialize response: {json.dumps(response)}")
    return response

# Handle tools/list request
def handle_tools_list(message_id):
    logger.info("Handling tools/list request")
    
    # Define the calculator tool with proper schema
    tools = [
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

# Handle message
def handle_message(message):
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

# Read a message from stdin using the MCP binary protocol
def read_message():
    try:
        # Try to read the first byte to see if there's any input
        first_byte = sys.stdin.buffer.read(1)
        if not first_byte:
            logger.info("End of input stream")
            return None
            
        # Read the remaining 3 bytes of the header
        header_rest = sys.stdin.buffer.read(3)
        if not header_rest or len(header_rest) < 3:
            logger.error(f"Invalid header received: {first_byte + header_rest if header_rest else first_byte}")
            return None
            
        # Combine the bytes and parse content length
        header = first_byte + header_rest
        
        # Try different byte orders to see which one gives a reasonable size
        content_length_le = struct.unpack("<I", header)[0]  # Little-endian
        content_length_be = struct.unpack(">I", header)[0]  # Big-endian
        
        # Choose the smaller, more reasonable size (assuming messages won't be larger than 1MB)
        if content_length_le < content_length_be and content_length_le < 1024 * 1024:
            content_length = content_length_le
            logger.debug(f"Using little-endian content length: {content_length}")
        else:
            content_length = content_length_be
            logger.debug(f"Using big-endian content length: {content_length}")
        
        # Sanity check on message length
        if content_length <= 0 or content_length > 1024 * 1024:  # 1 MB limit
            logger.error(f"Invalid content length: {content_length}, must be between 1 and 1MB")
            # Instead of failing, try a fixed small size that should be enough for initialization
            content_length = 1024  # Try reading 1KB
            logger.info(f"Attempting to read {content_length} bytes instead")
            
        # Read content
        logger.debug(f"Reading {content_length} bytes of content")
        content = sys.stdin.buffer.read(content_length)
        if not content:
            logger.error("Failed to read content")
            return None
            
        # Try to parse JSON, handling potential truncation
        try:
            message = json.loads(content.decode('utf-8'))
            logger.debug(f"Successfully parsed JSON message: {json.dumps(message)}")
            return message
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            # Try to find a valid JSON object by looking for closing brace
            content_str = content.decode('utf-8', errors='ignore')
            if '{' in content_str and '}' in content_str:
                last_brace = content_str.rindex('}')
                try:
                    message = json.loads(content_str[:last_brace+1])
                    logger.info(f"Recovered partial JSON message: {json.dumps(message)}")
                    return message
                except json.JSONDecodeError:
                    pass
            return None
    except Exception as e:
        logger.error(f"Error reading message: {str(e)}", exc_info=True)
        return None

# Write a message to stdout using the MCP binary protocol
def write_message(message):
    try:
        # Convert message to JSON
        content = json.dumps(message).encode("utf-8")
        content_length = len(content)
        
        # Write header (4 bytes for content length, little-endian)
        header = struct.pack("<I", content_length)  # Little-endian
        sys.stdout.buffer.write(header)
        sys.stdout.buffer.write(content)
        sys.stdout.buffer.flush()
        logger.debug(f"Wrote message with content length {content_length}: {json.dumps(message)}")
    except Exception as e:
        logger.error(f"Error writing message: {str(e)}", exc_info=True)

# Main function
def main():
    logger.info("Starting fixed calculator MCP server")
    
    try:
        while True:
            # Read message
            message = read_message()
            if not message:
                logger.warning("Failed to read message, will try again")
                # Instead of exiting, let's try to respond with a dummy initialize response
                dummy_response = {
                    "jsonrpc": "2.0",
                    "id": 0,
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
                write_message(dummy_response)
                continue
                
            # Handle message
            response = handle_message(message)
            if response:
                # Write response
                write_message(response)
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
