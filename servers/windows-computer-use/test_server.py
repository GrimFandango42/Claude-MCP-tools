#!/usr/bin/env python3
"""
Test script for Windows Computer Use MCP Server
Validates server startup and basic functionality.
"""

import sys
import os
import subprocess
import json
import asyncio
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

def test_server_import():
    """Test that the server can be imported."""
    try:
        from server import WindowsComputerUseMCP
        print("✅ Server module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def test_server_initialization():
    """Test server initialization."""
    try:
        from server import WindowsComputerUseMCP
        server = WindowsComputerUseMCP()
        print("✅ Server initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

async def test_tools_registration():
    """Test that tools are properly registered."""
    try:
        from server import WindowsComputerUseMCP
        server = WindowsComputerUseMCP()
        
        # Simulate the tools list call
        tools = await server.server._handle_list_tools()
        
        expected_tools = ["computer_20250124", "text_editor_20250429", "bash_20250124"]
        tool_names = [tool.name for tool in tools]
        
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print(f"✅ Tool '{expected_tool}' registered")
            else:
                print(f"❌ Tool '{expected_tool}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Tools registration test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    try:
        import pyautogui
        print("✅ pyautogui available")
        
        from PIL import ImageGrab
        print("✅ PIL ImageGrab available")
        
        import mcp
        print("✅ MCP framework available")
        
        return True
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False

async def run_tests():
    """Run all tests."""
    print("Windows Computer Use MCP Server - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Server Import", test_server_import),
        ("Server Initialize", test_server_initialization),
        ("Tools Registration", test_tools_registration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Server is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    print("[test] Starting Windows Computer Use MCP Server tests...", file=sys.stderr)
    
    # Run the async tests
    success = asyncio.run(run_tests())
    
    if success:
        print("\n[test] Server validation completed successfully!", file=sys.stderr)
        sys.exit(0)
    else:
        print("\n[test] Server validation failed!", file=sys.stderr)
        sys.exit(1)
