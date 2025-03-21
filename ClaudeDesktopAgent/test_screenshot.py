import os
import sys
import json
import struct

def send_message(message):
    # Convert message to JSON string and encode to bytes
    message_bytes = json.dumps(message).encode('utf-8')
    
    # Write message length followed by message content
    sys.stdout.buffer.write(struct.pack('<I', len(message_bytes)))
    sys.stdout.buffer.write(message_bytes)
    sys.stdout.buffer.flush()

def read_message():
    # Read message length (4 bytes)
    length_bytes = sys.stdin.buffer.read(4)
    if not length_bytes or len(length_bytes) < 4:
        return None
    
    # Convert to integer (little-endian)
    length = struct.unpack('<I', length_bytes)[0]
    
    # Read message content
    content_bytes = sys.stdin.buffer.read(length)
    if not content_bytes or len(content_bytes) < length:
        return None
    
    # Parse message
    content = content_bytes.decode('utf-8')
    return json.loads(content)

def main():
    # Initialize the server
    send_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "Test Client",
                "version": "1.0.0"
            }
        }
    })
    
    # Read response
    response = read_message()
    print("Initialize response:", json.dumps(response, indent=2), file=sys.stderr)
    
    # Get tools list
    send_message({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    
    # Read response
    response = read_message()
    print("Tools list response:", json.dumps(response, indent=2), file=sys.stderr)
    
    # Call screenshot tool
    send_message({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "mcp2_puppeteer_screenshot",
            "arguments": {
                "name": "test_screenshot",
                "width": 1024,
                "height": 768
            }
        }
    })
    
    # Read response
    response = read_message()
    print("Screenshot response:", json.dumps(response, indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()
