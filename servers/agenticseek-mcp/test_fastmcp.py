#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import time

def test_fastmcp_server():
    """Test the FastMCP server"""
    print("Testing FastMCP AgenticSeek Server...")
    
    server_dir = "C:\\AI_Projects\\Claude-MCP-tools\\servers\\agenticseek-mcp"
    python_path = os.path.join(server_dir, ".venv", "Scripts", "python.exe")
    server_path = os.path.join(server_dir, "server_fastmcp.py")
    
    print(f"Server directory: {server_dir}")
    print(f"Python path: {python_path}")
    print(f"Server script: {server_path}")
    
    # Test 1: Check if server starts without syntax errors
    try:
        print("\\nTesting server syntax...")
        result = subprocess.run(
            [python_path, "-m", "py_compile", server_path],
            cwd=server_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("Server syntax is valid")
        else:
            print(f"Syntax error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error checking syntax: {e}")
        return False
    
    # Test 2: Quick import test
    try:
        print("\\nTesting imports...")
        result = subprocess.run(
            [python_path, "-c", "import sys; sys.path.append('.'); import server_fastmcp; print('Imports successful')"],
            cwd=server_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("All imports successful")
            return True
        else:
            print(f"Import error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error testing imports: {e}")
        return False

if __name__ == "__main__":
    success = test_fastmcp_server()
    if success:
        print("\\nServer is ready for deployment!")
        print("\\nTo add to Claude Desktop, add this to claude_desktop_config.json:")
        print('''
{
  "mcpServers": {
    "agenticseek-mcp": {
      "command": "C:\\\\AI_Projects\\\\Claude-MCP-tools\\\\servers\\\\agenticseek-mcp\\\\.venv\\\\Scripts\\\\python.exe",
      "args": ["C:\\\\AI_Projects\\\\Claude-MCP-tools\\\\servers\\\\agenticseek-mcp\\\\server_fastmcp.py"],
      "cwd": "C:\\\\AI_Projects\\\\Claude-MCP-tools\\\\servers\\\\agenticseek-mcp",
      "keepAlive": true,
      "stderrToConsole": true,
      "description": "AgenticSeek multi-provider AI routing with cost optimization"
    }
  }
}
        ''')
    else:
        print("\\nServer has issues - check details above")
