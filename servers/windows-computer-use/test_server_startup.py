#!/usr/bin/env python3
"""
Quick test to verify the Windows Computer Use server starts without errors.
"""

import sys
import json
import subprocess
import tempfile
import os

def test_server_startup():
    """Test that the server can start and respond to basic initialization."""
    
    print("Testing Windows Computer Use MCP Server startup...")
    
    # Prepare test input for server initialization
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        # Start the server process
        server_path = os.path.join(os.path.dirname(__file__), "server.py")
        venv_python = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
        
        print(f"Starting server: {venv_python} {server_path}")
        
        process = subprocess.Popen(
            [venv_python, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Send initialization request
        init_json = json.dumps(init_request) + "\n"
        print(f"Sending: {init_json.strip()}")
        
        stdout, stderr = process.communicate(input=init_json, timeout=10)
        
        print("=== STDOUT ===")
        print(stdout)
        print("=== STDERR ===") 
        print(stderr)
        print("=== RETURN CODE ===")
        print(process.returncode)
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                print("=== PARSED RESPONSE ===")
                print(json.dumps(response, indent=2))
                
                if response.get("result", {}).get("serverInfo", {}).get("name") == "windows-computer-use":
                    print("✅ SUCCESS: Server initialized correctly!")
                    return True
                else:
                    print("❌ FAILED: Unexpected response format")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ FAILED: Invalid JSON response: {e}")
                return False
        else:
            print("❌ FAILED: No response from server")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FAILED: Server timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ FAILED: Exception occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_server_startup()
    sys.exit(0 if success else 1)