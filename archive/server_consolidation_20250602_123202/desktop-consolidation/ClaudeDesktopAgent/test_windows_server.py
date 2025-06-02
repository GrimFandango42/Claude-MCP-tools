#!/usr/bin/env python3
"""
Test script for the Windows-Compatible Fixed MCP Server
"""

import subprocess
import json
import sys
import time
import os

def test_server():
    """Test the MCP server with basic commands."""
    
    print("Starting MCP Server test...")
    
    # Path to the server
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "windows_fixed_mcp_server.py")
    
    # Start the server process
    cmd = [sys.executable, server_path]
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # Use binary mode
    )
    
    print("Server process started. Testing commands...")
    
    try:
        # Test 1: Initialize
        print("\nTest 1: Initialize")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
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
        
        # Send request
        request_json = json.dumps(init_request) + '\n'
        process.stdin.write(request_json.encode('utf-8'))
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode('utf-8'))
            print(f"Response: {json.dumps(response, indent=2)}")
        else:
            print("No response received")
            
        # Send initialized notification
        print("\nSending initialized notification...")
        notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        notif_json = json.dumps(notif) + '\n'
        process.stdin.write(notif_json.encode('utf-8'))
        process.stdin.flush()
        time.sleep(0.5)  # Give it time to process
        
        # Test 2: List tools
        print("\nTest 2: List tools")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        request_json = json.dumps(list_request) + '\n'
        process.stdin.write(request_json.encode('utf-8'))
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode('utf-8'))
            print(f"Response: {json.dumps(response, indent=2)}")
        else:
            print("No response received")
            
        # Test 3: Call screenshot tool
        print("\nTest 3: Call screenshot tool")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "take_screenshot",
                "arguments": {
                    "name": "test_screenshot"
                }
            }
        }
        
        request_json = json.dumps(call_request) + '\n'
        process.stdin.write(request_json.encode('utf-8'))
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode('utf-8'))
            print(f"Response: {json.dumps(response, indent=2)}")
        else:
            print("No response received")
            
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Terminate the server
        print("\nTerminating server...")
        process.terminate()
        time.sleep(1)
        if process.poll() is None:
            process.kill()
            
    print("\nTest completed!")
    
    # Check if log file exists and show recent entries
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "windows_fixed_mcp_server.log")
    if os.path.exists(log_file):
        print(f"\nServer log file: {log_file}")
        print("Recent log entries:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:  # Show last 10 lines
                print(f"  {line.rstrip()}")

if __name__ == "__main__":
    test_server()
