#!/usr/bin/env python3
"""
Complete test suite for Containerized Computer Use MCP Server
Tests Docker integration, MCP framework compliance, and Computer Use API tools.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import os

# Add the server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from containerized_mcp_server import ContainerizedComputerUseMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestContainerizedComputerUse:
    """Comprehensive test suite for the containerized MCP server."""
    
    def __init__(self):
        self.server = None
        self.passed = 0
        self.failed = 0
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✓ PASSED" if passed else "✗ FAILED"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
        if passed:
            self.passed += 1
            print(f"{status}: {test_name}")
        else:
            self.failed += 1
            print(f"{status}: {test_name} - {details}")
    
    async def test_docker_availability(self):
        """Test if Docker is available and running."""
        print("\n=== Testing Docker Availability ===")
        
        try:
            # Check Docker version
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_test("Docker CLI available", True, result.stdout.strip())
                
                # Check if Docker daemon is running
                result = subprocess.run(
                    ["docker", "ps"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.log_test("Docker daemon running", True)
                else:
                    self.log_test("Docker daemon running", False, "Docker Desktop may not be running")
            else:
                self.log_test("Docker CLI available", False, "Docker not installed")
                
        except Exception as e:
            self.log_test("Docker availability", False, str(e))
    
    async def test_server_initialization(self):
        """Test MCP server initialization."""
        print("\n=== Testing Server Initialization ===")
        
        try:
            self.server = ContainerizedComputerUseMCP()
            self.log_test("Server initialization", True)
            
            # Check Docker client
            if self.server.docker_client:
                self.log_test("Docker client initialized", True)
            else:
                self.log_test("Docker client initialized", False, "Docker client not available")
                
        except Exception as e:
            self.log_test("Server initialization", False, str(e))
    
    async def test_tool_registration(self):
        """Test that all tools are properly registered."""
        print("\n=== Testing Tool Registration ===")
        
        if not self.server:
            self.log_test("Tool registration", False, "Server not initialized")
            return
            
        try:
            # Get registered tools
            tools = []
            for handler in self.server.server._handlers:
                if hasattr(handler, '__name__') and 'list_tools' in handler.__name__:
                    tools = await handler()
                    break
            
            expected_tools = [
                "computer_20250124",
                "text_editor_20250429",
                "bash_20250124",
                "container_status",
                "container_start",
                "container_stop",
                "container_logs"
            ]
            
            tool_names = [tool.name for tool in tools]
            
            # Check each expected tool
            for expected in expected_tools:
                if expected in tool_names:
                    self.log_test(f"Tool '{expected}' registered", True)
                else:
                    self.log_test(f"Tool '{expected}' registered", False, "Tool not found")
            
            # Verify tool schemas
            for tool in tools:
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    self.log_test(f"Tool '{tool.name}' has valid schema", True)
                else:
                    self.log_test(f"Tool '{tool.name}' has valid schema", False, "Missing schema")
                    
        except Exception as e:
            self.log_test("Tool registration", False, str(e))
    
    async def test_container_lifecycle(self):
        """Test container start, status, and stop operations."""
        print("\n=== Testing Container Lifecycle ===")
        
        if not self.server:
            self.log_test("Container lifecycle", False, "Server not initialized")
            return
        
        try:
            # Test container status
            result = await self.server._get_container_status()
            initial_status = result.get("status", "unknown")
            self.log_test("Container status check", True, f"Status: {initial_status}")
            
            # Start container if not running
            if initial_status != "running":
                print("Starting container...")
                result = await self.server._start_container()
                
                if "ERROR" not in result.get("output", ""):
                    self.log_test("Container start", True, result.get("output", ""))
                    
                    # Wait for container to be ready
                    print("Waiting for container to be ready...")
                    await asyncio.sleep(10)
                    
                    # Verify container is running
                    result = await self.server._get_container_status()
                    if result.get("status") == "running":
                        self.log_test("Container running verification", True)
                    else:
                        self.log_test("Container running verification", False, f"Status: {result.get('status')}")
                else:
                    self.log_test("Container start", False, result.get("output", ""))
            else:
                self.log_test("Container already running", True)
            
            # Test container logs
            result = await self.server._get_container_logs(lines=10)
            if "ERROR" not in result.get("output", ""):
                self.log_test("Container logs retrieval", True)
            else:
                self.log_test("Container logs retrieval", False, result.get("output", ""))
                
        except Exception as e:
            self.log_test("Container lifecycle", False, str(e))
    
    async def test_computer_use_tools(self):
        """Test Computer Use API tools in the container."""
        print("\n=== Testing Computer Use API Tools ===")
        
        if not self.server:
            self.log_test("Computer Use tools", False, "Server not initialized")
            return
        
        # Ensure container is running
        status = await self.server._get_container_status()
        if status.get("status") != "running":
            self.log_test("Computer Use tools", False, "Container not running - skipping tool tests")
            return
        
        # Test bash_20250124
        try:
            print("\nTesting bash_20250124...")
            result = await self.server._execute_in_container(
                "bash_20250124",
                {"command": "echo 'Test from MCP' && pwd && date"}
            )
            
            if "output" in result and "ERROR" not in result.get("output", ""):
                self.log_test("bash_20250124 execution", True, result["output"][:100])
            else:
                self.log_test("bash_20250124 execution", False, result.get("output", ""))
                
        except Exception as e:
            self.log_test("bash_20250124 execution", False, str(e))
        
        # Test text_editor_20250429
        try:
            print("\nTesting text_editor_20250429...")
            
            # Create a test file
            result = await self.server._execute_in_container(
                "text_editor_20250429",
                {
                    "command": "create",
                    "path": "/tmp/mcp_test.txt",
                    "file_text": "This is a test file created by the Containerized Computer Use MCP!"
                }
            )
            
            if "output" in result and "Created" in result.get("output", ""):
                self.log_test("text_editor create", True)
                
                # View the file
                result = await self.server._execute_in_container(
                    "text_editor_20250429",
                    {
                        "command": "view",
                        "path": "/tmp/mcp_test.txt"
                    }
                )
                
                if "output" in result and "test file" in result.get("output", ""):
                    self.log_test("text_editor view", True)
                else:
                    self.log_test("text_editor view", False, result.get("output", ""))
                    
                # Test str_replace
                result = await self.server._execute_in_container(
                    "text_editor_20250429",
                    {
                        "command": "str_replace",
                        "path": "/tmp/mcp_test.txt",
                        "old_str": "test file",
                        "new_str": "awesome file"
                    }
                )
                
                if "output" in result and "Replaced" in result.get("output", ""):
                    self.log_test("text_editor str_replace", True)
                else:
                    self.log_test("text_editor str_replace", False, result.get("output", ""))
                    
            else:
                self.log_test("text_editor create", False, result.get("output", ""))
                
        except Exception as e:
            self.log_test("text_editor_20250429", False, str(e))
        
        # Test computer_20250124 screenshot
        try:
            print("\nTesting computer_20250124 screenshot...")
            result = await self.server._execute_in_container(
                "computer_20250124",
                {"action": "screenshot"}
            )
            
            if "screenshot" in result:
                self.log_test("computer_20250124 screenshot", True, 
                            f"Screenshot captured ({len(result['screenshot'])} bytes)")
            else:
                self.log_test("computer_20250124 screenshot", False, 
                            result.get("output", "No screenshot data"))
                
        except Exception as e:
            self.log_test("computer_20250124 screenshot", False, str(e))
    
    async def test_mcp_protocol_compliance(self):
        """Test MCP protocol compliance."""
        print("\n=== Testing MCP Protocol Compliance ===")
        
        if not self.server:
            self.log_test("MCP protocol compliance", False, "Server not initialized")
            return
        
        try:
            # Check server has proper MCP Server instance
            if hasattr(self.server, 'server') and self.server.server.__class__.__name__ == 'Server':
                self.log_test("MCP Server instance", True)
            else:
                self.log_test("MCP Server instance", False, "Not using mcp.server.Server")
            
            # Check for required handlers
            has_list_tools = False
            has_call_tool = False
            
            for handler in self.server.server._handlers:
                if hasattr(handler, '__name__'):
                    if 'list_tools' in handler.__name__:
                        has_list_tools = True
                    elif 'call_tool' in handler.__name__:
                        has_call_tool = True
            
            self.log_test("list_tools handler registered", has_list_tools)
            self.log_test("call_tool handler registered", has_call_tool)
            
            # Check TextContent return type
            if has_call_tool:
                # Test a simple tool call
                for handler in self.server.server._handlers:
                    if hasattr(handler, '__name__') and 'call_tool' in handler.__name__:
                        result = await handler("container_status", {})
                        if result and all(hasattr(r, 'type') and r.type == 'text' for r in result):
                            self.log_test("TextContent return type", True)
                        else:
                            self.log_test("TextContent return type", False, "Not returning TextContent")
                        break
                        
        except Exception as e:
            self.log_test("MCP protocol compliance", False, str(e))
    
    async def generate_config_snippet(self):
        """Generate Claude Desktop configuration snippet."""
        print("\n=== Configuration Snippet ===")
        
        config = {
            "containerized-computer-use": {
                "command": "cmd",
                "args": ["/c", f"{Path(__file__).parent}\\launch_containerized_mcp.bat"],
                "cwd": str(Path(__file__).parent),
                "keepAlive": True,
                "stderrToConsole": True,
                "description": "Containerized Computer Use with Docker isolation and VNC access"
            }
        }
        
        print("\nAdd this to your Claude Desktop configuration:")
        print(json.dumps(config, indent=2))
        
        print("\nVNC Connection Details:")
        print("- URL: vnc://localhost:5900")
        print("- Password: vnc123")
    
    async def run_all_tests(self):
        """Run all test cases."""
        print("=" * 60)
        print("Containerized Computer Use MCP Server - Complete Test Suite")
        print("=" * 60)
        
        await self.test_docker_availability()
        await self.test_server_initialization()
        await self.test_tool_registration()
        await self.test_mcp_protocol_compliance()
        await self.test_container_lifecycle()
        await self.test_computer_use_tools()
        
        print("\n" + "=" * 60)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        if self.failed == 0:
            print("\n✓ All tests passed! The server is ready for production use.")
            await self.generate_config_snippet()
        else:
            print("\n✗ Some tests failed. Review the errors above and fix issues.")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.failed == 0


async def main():
    """Run the complete test suite."""
    tester = TestContainerizedComputerUse()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Server is production-ready!")
        print("\nNext steps:")
        print("1. Add the configuration snippet to Claude Desktop")
        print("2. Restart Claude Desktop")
        print("3. Test with: 'Take a screenshot using the containerized computer'")
    else:
        print("\n❌ Server needs fixes before deployment.")
        print("\nCommon issues:")
        print("- Docker Desktop not running")
        print("- Missing Python dependencies")
        print("- Container build failures")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
