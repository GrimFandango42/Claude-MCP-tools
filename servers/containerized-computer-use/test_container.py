#!/usr/bin/env python3
"""
Test suite for containerized Computer Use MCP Server
Tests all functionality within the Docker container
"""

import json
import subprocess
import time
import base64
from typing import Dict, Any, List
import sys


class ContainerTester:
    """Test harness for containerized Computer Use server."""
    
    def __init__(self):
        self.container_name = "windows-computer-use"
        self.test_results = []
        
    def run_mcp_command(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an MCP command in the container."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        # Execute command in container
        cmd = [
            "docker", "exec", "-i", self.container_name,
            "python3", "-c",
            f"import sys, json; from container_mcp_wrapper import ContainerMCPServer; "
            f"import asyncio; server = ContainerMCPServer(); "
            f"result = asyncio.run(server.handle_request({json.dumps(request)})); "
            f"print(json.dumps(result))"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": f"Command failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            return {"error": f"Execution error: {str(e)}"}
    
    def test_initialization(self):
        """Test MCP server initialization."""
        print("Testing initialization...")
        response = self.run_mcp_command("initialize")
        
        success = "result" in response and "serverInfo" in response.get("result", {})
        self.test_results.append({
            "test": "Initialization",
            "success": success,
            "details": response
        })
        
        if success:
            print("✓ Initialization successful")
        else:
            print("✗ Initialization failed:", response)
        
        return success
    
    def test_tools_list(self):
        """Test tools listing."""
        print("\nTesting tools list...")
        response = self.run_mcp_command("tools/list")
        
        success = False
        if "result" in response and "tools" in response.get("result", {}):
            tools = response["result"]["tools"]
            expected_tools = ["computer_20250124", "text_editor_20250429", "bash_20250124"]
            found_tools = [tool["name"] for tool in tools]
            success = all(tool in found_tools for tool in expected_tools)
        
        self.test_results.append({
            "test": "Tools List",
            "success": success,
            "details": response
        })
        
        if success:
            print("✓ All tools available")
        else:
            print("✗ Tools list incomplete:", response)
        
        return success
    
    def test_bash_command(self):
        """Test bash command execution."""
        print("\nTesting bash command...")
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "echo 'Container test' && date && pwd"}
        })
        
        success = "result" in response and "content" in response.get("result", {})
        output = ""
        if success:
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                output = content[0].get("text", "")
                success = "Container test" in output
        
        self.test_results.append({
            "test": "Bash Command",
            "success": success,
            "output": output,
            "details": response
        })
        
        if success:
            print(f"✓ Bash command executed: {output[:50]}...")
        else:
            print("✗ Bash command failed:", response)
        
        return success
    
    def test_file_operations(self):
        """Test text editor file operations."""
        print("\nTesting file operations...")
        test_file = "/tmp/container_test.txt"
        test_content = "Hello from containerized Computer Use!"
        
        # Create file
        response = self.run_mcp_command("tools/call", {
            "name": "text_editor_20250429",
            "arguments": {
                "command": "create",
                "path": test_file,
                "file_text": test_content
            }
        })
        
        create_success = "result" in response and "content" in response.get("result", {})
        
        # View file
        response = self.run_mcp_command("tools/call", {
            "name": "text_editor_20250429",
            "arguments": {
                "command": "view",
                "path": test_file
            }
        })
        
        view_success = False
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                output = content[0].get("text", "")
                view_success = test_content in output
        
        success = create_success and view_success
        
        self.test_results.append({
            "test": "File Operations",
            "success": success,
            "create": create_success,
            "view": view_success,
            "details": response
        })
        
        if success:
            print("✓ File operations successful")
        else:
            print("✗ File operations failed")
        
        return success
    
    def test_screenshot(self):
        """Test screenshot functionality."""
        print("\nTesting screenshot...")
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {"action": "screenshot"}
        })
        
        success = False
        screenshot_size = 0
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            for item in content:
                if item.get("type") == "image":
                    screenshot_data = item.get("data", "")
                    if screenshot_data:
                        try:
                            # Verify it's valid base64
                            decoded = base64.b64decode(screenshot_data)
                            screenshot_size = len(decoded)
                            success = screenshot_size > 1000  # At least 1KB
                        except:
                            pass
        
        self.test_results.append({
            "test": "Screenshot",
            "success": success,
            "size": screenshot_size,
            "details": response if not success else "Screenshot captured successfully"
        })
        
        if success:
            print(f"✓ Screenshot captured: {screenshot_size:,} bytes")
        else:
            print("✗ Screenshot failed:", response)
        
        return success
    
    def test_gui_automation(self):
        """Test GUI automation capabilities."""
        print("\nTesting GUI automation...")
        
        # Move mouse
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "mouse_move",
                "coordinate": [500, 300]
            }
        })
        
        move_success = "result" in response and "content" in response.get("result", {})
        
        # Type text
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "type",
                "text": "Container automation test"
            }
        })
        
        type_success = "result" in response and "content" in response.get("result", {})
        
        success = move_success and type_success
        
        self.test_results.append({
            "test": "GUI Automation",
            "success": success,
            "move": move_success,
            "type": type_success
        })
        
        if success:
            print("✓ GUI automation working")
        else:
            print("✗ GUI automation failed")
        
        return success
    
    def test_container_health(self):
        """Test container health and services."""
        print("\nTesting container health...")
        
        # Check container status
        cmd = ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        container_running = result.returncode == 0 and "Up" in result.stdout
        
        # Check VNC service
        cmd = ["docker", "exec", self.container_name, "ps", "aux"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        vnc_running = "x11vnc" in result.stdout
        xvfb_running = "Xvfb" in result.stdout
        
        # Check Python process
        python_running = "python" in result.stdout
        
        success = all([container_running, vnc_running, xvfb_running, python_running])
        
        self.test_results.append({
            "test": "Container Health",
            "success": success,
            "container": container_running,
            "vnc": vnc_running,
            "xvfb": xvfb_running,
            "python": python_running
        })
        
        if success:
            print("✓ All container services healthy")
        else:
            print(f"✗ Container health issues: Container={container_running}, VNC={vnc_running}, XVFB={xvfb_running}, Python={python_running}")
        
        return success
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        print("="*50)
        print("Containerized Computer Use Test Suite")
        print("="*50)
        
        # Check if container is running
        cmd = ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if self.container_name not in result.stdout:
            print(f"✗ Container '{self.container_name}' is not running!")
            print("Please start the container with: .\\start-container.ps1")
            return False
        
        # Run tests
        tests = [
            self.test_container_health,
            self.test_initialization,
            self.test_tools_list,
            self.test_bash_command,
            self.test_file_operations,
            self.test_screenshot,
            self.test_gui_automation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"✗ Test failed with exception: {e}")
                self.test_results.append({
                    "test": test.__name__,
                    "success": False,
                    "error": str(e)
                })
        
        # Generate report
        print("\n" + "="*50)
        print("Test Results Summary")
        print("="*50)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            print(f"{status} - {result['test']}")
        
        print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print("\nDetailed results saved to test_results.json")
        
        return passed == total


def main():
    """Run the test suite."""
    tester = ContainerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
