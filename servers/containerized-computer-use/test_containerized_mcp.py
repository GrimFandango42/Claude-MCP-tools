#!/usr/bin/env python3
"""
Test script for Containerized Computer Use MCP Server
Validates all tools and container integration.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from containerized_mcp_server import ContainerizedComputerUseMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestContainerizedMCP:
    """Test suite for the containerized MCP server."""
    
    def __init__(self):
        self.server = ContainerizedComputerUseMCP()
        self.passed = 0
        self.failed = 0
        
    async def test_tool_listing(self):
        """Test that all tools are properly registered."""
        print("\n=== Testing Tool Listing ===")
        try:
            # Get the list tools handler
            list_tools_handler = None
            for handler in self.server.server._tool_handlers:
                if hasattr(handler, '__name__') and 'list_tools' in handler.__name__:
                    list_tools_handler = handler
                    break
            
            if not list_tools_handler:
                raise Exception("List tools handler not found")
                
            tools = await list_tools_handler()
            
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
            
            for expected in expected_tools:
                if expected in tool_names:
                    print(f"✓ Tool '{expected}' found")
                    self.passed += 1
                else:
                    print(f"✗ Tool '{expected}' missing")
                    self.failed += 1
                    
        except Exception as e:
            print(f"✗ Tool listing failed: {e}")
            self.failed += 1
    
    async def test_container_status(self):
        """Test container status checking."""
        print("\n=== Testing Container Status ===")
        try:
            result = await self.server._get_container_status()
            print(f"Container status: {result.get('status', 'unknown')}")
            
            if "output" in result:
                print(f"✓ Container status check completed: {result['output']}")
                self.passed += 1
            else:
                print("✗ No output from container status")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ Container status check failed: {e}")
            self.failed += 1
    
    async def test_container_lifecycle(self):
        """Test starting and stopping the container."""
        print("\n=== Testing Container Lifecycle ===")
        
        # Test starting container
        try:
            print("Starting container...")
            result = await self.server._start_container()
            
            if "ERROR" not in result.get("output", ""):
                print(f"✓ Container start: {result['output']}")
                self.passed += 1
                
                # Wait for container to be ready
                await asyncio.sleep(5)
                
                # Test container is running
                status = await self.server._get_container_status()
                if status.get("status") == "running":
                    print("✓ Container is running")
                    self.passed += 1
                else:
                    print(f"✗ Container status: {status.get('status')}")
                    self.failed += 1
                    
            else:
                print(f"✗ Container start failed: {result['output']}")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ Container lifecycle test failed: {e}")
            self.failed += 1
    
    async def test_computer_tools(self):
        """Test Computer Use API tools in container."""
        print("\n=== Testing Computer Use Tools ===")
        
        # Ensure container is running
        status = await self.server._get_container_status()
        if status.get("status") != "running":
            print("Starting container for tests...")
            await self.server._start_container()
            await asyncio.sleep(5)
        
        # Test bash command
        try:
            print("\nTesting bash_20250124...")
            result = await self.server._execute_in_container(
                "bash_20250124",
                {"command": "echo 'Hello from container!' && pwd"}
            )
            
            if "output" in result and "ERROR" not in result["output"]:
                print(f"✓ Bash command executed: {result['output'][:100]}...")
                self.passed += 1
            else:
                print(f"✗ Bash command failed: {result}")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ Bash test failed: {e}")
            self.failed += 1
        
        # Test text editor
        try:
            print("\nTesting text_editor_20250429...")
            
            # Create a file
            result = await self.server._execute_in_container(
                "text_editor_20250429",
                {
                    "command": "create",
                    "path": "/tmp/test_file.txt",
                    "file_text": "This is a test file from the containerized MCP!"
                }
            )
            
            if "output" in result and "Created" in result["output"]:
                print(f"✓ File created: {result['output']}")
                self.passed += 1
                
                # View the file
                result = await self.server._execute_in_container(
                    "text_editor_20250429",
                    {
                        "command": "view",
                        "path": "/tmp/test_file.txt"
                    }
                )
                
                if "output" in result and "test file" in result["output"]:
                    print(f"✓ File content verified")
                    self.passed += 1
                else:
                    print(f"✗ File view failed: {result}")
                    self.failed += 1
                    
            else:
                print(f"✗ File creation failed: {result}")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ Text editor test failed: {e}")
            self.failed += 1
        
        # Test screenshot
        try:
            print("\nTesting computer_20250124 screenshot...")
            result = await self.server._execute_in_container(
                "computer_20250124",
                {"action": "screenshot"}
            )
            
            if "screenshot" in result:
                print(f"✓ Screenshot captured (base64 length: {len(result['screenshot'])})")
                self.passed += 1
            else:
                print(f"✗ Screenshot failed: {result}")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ Screenshot test failed: {e}")
            self.failed += 1
    
    async def test_container_logs(self):
        """Test getting container logs."""
        print("\n=== Testing Container Logs ===")
        try:
            result = await self.server._get_container_logs(lines=10)
            
            if "output" in result and "logs" in result["output"]:
                print(f"✓ Retrieved container logs")
                print(f"First 200 chars: {result['output'][:200]}...")
                self.passed += 1
            else:
                print(f"✗ Log retrieval failed: {result}")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ Container logs test failed: {e}")
            self.failed += 1
    
    async def run_all_tests(self):
        """Run all test cases."""
        print("Starting Containerized Computer Use MCP Server Tests")
        print("=" * 60)
        
        await self.test_tool_listing()
        await self.test_container_status()
        await self.test_container_lifecycle()
        await self.test_computer_tools()
        await self.test_container_logs()
        
        print("\n" + "=" * 60)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        return self.failed == 0


async def main():
    """Run the test suite."""
    tester = TestContainerizedMCP()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✓ All tests passed! The server is ready for use.")
        print("\nTo add to Claude Desktop, use this configuration:")
        print(json.dumps({
            "containerized-computer-use": {
                "command": "cmd",
                "args": ["/c", f"{Path(__file__).parent}\\launch_containerized_mcp.bat"],
                "cwd": str(Path(__file__).parent),
                "keepAlive": True,
                "stderrToConsole": True,
                "description": "Containerized Computer Use with Docker isolation"
            }
        }, indent=2))
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        
    return success


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
