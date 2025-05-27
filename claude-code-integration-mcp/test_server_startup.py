#!/usr/bin/env python3
"""
Test script to diagnose Claude Code Integration MCP Server startup issues
"""

import sys
import os
import subprocess
import traceback

def test_basic_imports():
    """Test basic Python imports required by the server"""
    print("=== Testing Basic Imports ===")
    
    try:
        import json
        print("✓ json import successful")
    except ImportError as e:
        print(f"✗ json import failed: {e}")
        return False
    
    try:
        import asyncio
        print("✓ asyncio import successful")
    except ImportError as e:
        print(f"✗ asyncio import failed: {e}")
        return False
    
    try:
        import subprocess
        print("✓ subprocess import successful")
    except ImportError as e:
        print(f"✗ subprocess import failed: {e}")
        return False
    
    return True

def test_mcp_imports():
    """Test MCP-specific imports"""
    print("\n=== Testing MCP Imports ===")
    
    try:
        from mcp.server.fastmcp import FastMCP
        print("✓ FastMCP import successful")
        return True
    except ImportError as e:
        print(f"✗ FastMCP import failed: {e}")
        print("This is likely the cause of the server startup issue.")
        return False

def test_optional_imports():
    """Test optional imports"""
    print("\n=== Testing Optional Imports ===")
    
    try:
        import psutil
        print("✓ psutil import successful")
    except ImportError as e:
        print(f"⚠ psutil import failed (optional): {e}")

def test_server_initialization():
    """Test if the server can be initialized"""
    print("\n=== Testing Server Initialization ===")
    
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Test Claude Code Integration")
        print("✓ FastMCP server initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        traceback.print_exc()
        return False

def test_claude_code_cli():
    """Test Claude Code CLI availability"""
    print("\n=== Testing Claude Code CLI ===")
    
    try:
        result = subprocess.run(
            ["claude-code", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ Claude Code CLI available: {result.stdout.strip()}")
            return True
        else:
            print(f"⚠ Claude Code CLI returned error code {result.returncode}")
            print(f"  stderr: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠ Claude Code CLI not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Error testing Claude Code CLI: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("Claude Code Integration MCP Server Diagnostic")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tests = [
        test_basic_imports,
        test_mcp_imports,
        test_optional_imports,
        test_server_initialization,
        test_claude_code_cli
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            results.append(False)
        print()
    
    print("=== Diagnostic Summary ===")
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    print(f"Tests passed: {success_count}/{total_count}")
    
    if not results[1]:  # MCP import test
        print("\n🔧 RECOMMENDED FIX:")
        print("The FastMCP import is failing. Try installing the required dependencies:")
        print("pip install fastmcp>=0.2.0")
        print("or")
        print("pip install -r requirements.txt")
    
    if not results[4]:  # Claude Code CLI test
        print("\n📋 NOTE:")
        print("Claude Code CLI is not available, but the server can still function")
        print("as a framework for task delegation and project management.")

if __name__ == "__main__":
    main()
