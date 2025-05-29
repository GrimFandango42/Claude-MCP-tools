import asyncio
import websockets
import json
import sys

async def send_receive(websocket, message_dict):
    message_json = json.dumps(message_dict)
    print(f"Client Sending: {message_json}", file=sys.stderr)
    await websocket.send(message_json)
    response_json = await websocket.recv()
    print(f"Client Received: {response_json}", file=sys.stderr)
    return json.loads(response_json)

async def main():
    uri = "ws://localhost:8000/"
    results = {}
    try:
        async with websockets.connect(uri, open_timeout=10) as websocket:
            print(f"Client Connected to {uri}", file=sys.stderr)

            # 1. Initialize (using a new ID for clarity)
            init_msg = {
                "jsonrpc": "2.0", "id": "client-init-4", "method": "initialize",
                "params": {"protocolVersion": "2.0", "clientInfo": {"name": "TestClient", "version": "0.4"}, "capabilities": {}}
            }
            results["initialize_response"] = await send_receive(websocket, init_msg)

            # 2. Test `code /tmp/dummyfile.txt` (VSCode CLI basic file open)
            code_open_msg = {
                "jsonrpc": "2.0", "id": "test-code-open", "method": "tools/call",
                "params": {"name": "execute_shell_command", "arguments": {"command": "code /tmp/dummyfile.txt"}}
            }
            results["code_open_response"] = await send_receive(websocket, code_open_msg)

        print("Client Interaction complete.", file=sys.stderr)
        print(json.dumps(results)) # Final JSON output to stdout

    except ConnectionRefusedError:
        print(f"ERROR: Connection to {uri} refused. Ensure the server is running.", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catching broader exceptions including websockets.exceptions.InvalidStatusCode
        print(f"ERROR: An exception occurred in client: {type(e).__name__} - {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
