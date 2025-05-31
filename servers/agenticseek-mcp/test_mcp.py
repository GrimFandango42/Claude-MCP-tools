#!/usr/bin/env python3

import asyncio
import json
import subprocess
import sys
import os

async def test_agenticseek_mcp():
    """Test the AgenticSeek MCP server"""
    print("Testing AgenticSeek MCP Server...")
    
    # Change to the server directory
    server_dir = "C:\\AI_Projects\\Claude-MCP-tools\\servers\\agenticseek-mcp"
    python_path = os.path.join(server_dir, ".venv", "Scripts", "python.exe")
    server_path = os.path.join(server_dir, "server.py")
    
    print(f"Server directory: {server_dir}")
    print(f"Python path: {python_path}")
    print(f"Server script: {server_path}")
    
    # Check if files exist
    if not os.path.exists(python_path):
        print(f"Python executable not found: {python_path}")
        return False
    
    if not os.path.exists(server_path):
        print(f"Server script not found: {server_path}")
        return False
    
    print("Files exist, testing server...")
    
    # Test 1: Check if server starts without errors
    try:
        # Start the server process
        print("Starting MCP server...")
        process = subprocess.Popen(
            [python_path, server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=server_dir,
            text=True
        )
        
        # Send an initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\\n")
        process.stdin.flush()
        
        # Wait for response (with timeout)
        try:
            stdout, stderr = process.communicate(timeout=10)
            
            if stderr:
                print(f"Server stderr: {stderr}")
            
            if stdout:
                print(f"Server response: {stdout[:500]}...")  # First 500 chars
                print("Server started successfully!")
                return True
            else:
                print("No response from server")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("Server startup timeout")
            return False
            
    except Exception as e:
        print(f"Error testing server: {e}")
        return False

async def test_agenticseek_api():
    """Test if AgenticSeek API is running"""
    print("\\nTesting AgenticSeek API...")
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("AgenticSeek API is running")
                return True
            else:
                print(f"AgenticSeek API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"AgenticSeek API not available: {e}")
        print("Make sure to start AgenticSeek first:")
        print("   cd /mnt/c/AI_Projects/agenticSeek")
        print("   ./agentic_seek_env/Scripts/python.exe api.py")
        return False

async def main():
    print("AgenticSeek MCP Debugging Suite")
    print("=" * 50)
    
    # Test API first
    api_running = await test_agenticseek_api()
    
    # Test MCP server
    mcp_working = await test_agenticseek_mcp()
    
    print("\\nRESULTS:")
    print(f"   AgenticSeek API: {'Running' if api_running else 'Not Running'}")
    print(f"   MCP Server: {'Working' if mcp_working else 'Issues Found'}")
    
    if api_running and mcp_working:
        print("\\nEverything looks good! MCP server should work with Claude.")
        print("\\nNext steps:")
        print("   1. Add the server to Claude Desktop config")
        print("   2. Restart Claude Desktop")
        print("   3. Test with: 'Use smart_routing to analyze this text'")
    else:
        print("\\nIssues found - see details above")

if __name__ == "__main__":
    asyncio.run(main())
