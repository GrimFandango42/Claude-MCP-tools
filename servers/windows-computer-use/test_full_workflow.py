#!/usr/bin/env python3
"""
Full workflow test for Windows Computer Use MCP Server - simulates Claude Desktop interaction.
"""

import sys
import json
import subprocess
import os
import time

def test_full_workflow():
    """Test the complete MCP workflow that Claude Desktop would use."""
    
    print("🧪 Testing Full Windows Computer Use MCP Server Workflow...")
    print("=" * 60)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    venv_python = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
    
    try:
        # Start the server process
        print(f"🚀 Starting server: {venv_python} {server.py}")
        process = subprocess.Popen(
            [venv_python, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        def send_request(request, description):
            """Send a request and get response"""
            print(f"\n📤 {description}")
            request_json = json.dumps(request) + "\n"
            print(f"   Request: {request_json.strip()}")
            
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    print(f"   ✅ Response: {json.dumps(response, indent=2)}")
                    return response
                except json.JSONDecodeError as e:
                    print(f"   ❌ Invalid JSON: {response_line.strip()}")
                    print(f"   Error: {e}")
                    return None
            else:
                print("   ❌ No response received")
                return None
        
        # Test 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "claude-desktop", "version": "1.0.0"}
            }
        }
        
        response = send_request(init_request, "INITIALIZATION")
        if not response or "error" in response:
            print("❌ FAILED: Initialization failed")
            return False
        
        # Test 2: List Tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_request(tools_request, "TOOLS LIST")
        if not response or "error" in response:
            print("❌ FAILED: Tools list failed")
            return False
        
        # Test 3: Take Screenshot (Computer Use Tool)
        screenshot_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "computer_20250124",
                "arguments": {
                    "action": "screenshot"
                }
            }
        }
        
        response = send_request(screenshot_request, "SCREENSHOT TEST")
        if not response or "error" in response:
            print("❌ FAILED: Screenshot failed")
            return False
        
        # Test 4: Optional Methods
        resources_request = {
            "jsonrpc": "2.0", 
            "id": 4,
            "method": "resources/list",
            "params": {}
        }
        
        response = send_request(resources_request, "RESOURCES LIST")
        if not response or "error" in response:
            print("❌ FAILED: Resources list failed")
            return False
        
        prompts_request = {
            "jsonrpc": "2.0",
            "id": 5, 
            "method": "prompts/list",
            "params": {}
        }
        
        response = send_request(prompts_request, "PROMPTS LIST")
        if not response or "error" in response:
            print("❌ FAILED: Prompts list failed")
            return False
        
        print("\n🎉 SUCCESS: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Exception occurred: {e}")
        return False
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            # Check stderr for any errors
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"\n⚠️  STDERR OUTPUT:")
                print(stderr_output)

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)