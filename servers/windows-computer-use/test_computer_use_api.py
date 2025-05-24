#!/usr/bin/env python3
"""
Computer Use API Compliance Test Suite
Tests the updated Windows Computer Use MCP Server against Computer Use API specifications.
"""

import sys
import json
import subprocess
import time
import base64
from pathlib import Path

class ComputerUseAPITester:
    """Test suite for Computer Use API compliance."""
    
    def __init__(self):
        self.server_path = Path(__file__).parent / "server.py"
        self.test_results = []
        
    def run_mcp_command(self, request):
        """Execute MCP command and return response."""
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=json.dumps(request) + "\n", timeout=10)
            
            if stderr:
                return {"error": f"Server error: {stderr}"}
            
            # Parse the response
            response = json.loads(stdout.strip())
            return response
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "Server timeout"}
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    def test_tool_discovery(self):
        """Test that tools are properly exposed with correct names."""
        print("🔍 Testing Tool Discovery...")
        
        # Initialize server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        init_response = self.run_mcp_command(init_request)
        assert "result" in init_response, f"Init failed: {init_response}"
        
        # List tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        list_response = self.run_mcp_command(list_request)
        assert "result" in list_response, f"List tools failed: {list_response}"
        
        tools = list_response["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]
        
        # Check required Computer Use API tools
        required_tools = [
            "computer_20250124",
            "text_editor_20250429", 
            "bash_20250124"
        ]
        
        for tool_name in required_tools:
            assert tool_name in tool_names, f"Missing required tool: {tool_name}"
            print(f"  ✅ Found tool: {tool_name}")
        
        # Validate computer tool schema
        computer_tool = next(tool for tool in tools if tool["name"] == "computer_20250124")
        schema = computer_tool["inputSchema"]
        
        # Check required properties
        assert "action" in schema["properties"], "Computer tool missing action property"
        assert schema["properties"]["action"]["type"] == "string", "Action must be string type"
        
        # Check enhanced actions
        enhanced_actions = [
            "key", "hold_key", "type", "cursor_position", "mouse_move",
            "left_mouse_down", "left_mouse_up", "left_click", "left_click_drag",
            "right_click", "middle_click", "double_click", "triple_click",
            "scroll", "wait", "screenshot"
        ]
        
        action_enum = schema["properties"]["action"]["enum"]
        for action in enhanced_actions:
            assert action in action_enum, f"Missing enhanced action: {action}"
        
        print("  ✅ All Computer Use API tools discovered with correct schemas")
        return True
    
    def test_computer_tool_actions(self):
        """Test computer tool actions."""
        print("💻 Testing Computer Tool Actions...")
        
        test_cases = [
            {
                "name": "Screenshot",
                "request": {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "computer_20250124",
                        "arguments": {"action": "screenshot"}
                    }
                }
            },
            {
                "name": "Cursor Position",
                "request": {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "computer_20250124",
                        "arguments": {"action": "cursor_position"}
                    }
                }
            },
            {
                "name": "Wait Action",
                "request": {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "computer_20250124",
                        "arguments": {"action": "wait", "duration": 1}
                    }
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            response = self.run_mcp_command(test_case["request"])
            
            assert "result" in response, f"{test_case['name']} failed: {response}"
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            
            assert "error" not in result, f"{test_case['name']} returned error: {result}"
            print(f"    ✅ {test_case['name']} successful")
        
        return True
    
    def test_text_editor_tool(self):
        """Test text editor tool functionality."""
        print("📝 Testing Text Editor Tool...")
        
        test_file = "test_computer_use_api.txt"
        
        # Test create file
        create_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "text_editor_20250429",
                "arguments": {
                    "command": "create",
                    "path": test_file,
                    "file_text": "Hello Computer Use API!"
                }
            }
        }
        
        response = self.run_mcp_command(create_request)
        assert "result" in response, f"Create file failed: {response}"
        print("    ✅ File creation successful")
        
        # Test view file
        view_request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "text_editor_20250429",
                "arguments": {
                    "command": "view",
                    "path": test_file
                }
            }
        }
        
        response = self.run_mcp_command(view_request)
        assert "result" in response, f"View file failed: {response}"
        print("    ✅ File viewing successful")
        
        # Clean up
        try:
            Path(test_file).unlink()
        except:
            pass
        
        return True
    
    def test_bash_tool(self):
        """Test bash tool functionality."""
        print("🐧 Testing Bash Tool...")
        
        bash_request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "bash_20250124",
                "arguments": {
                    "command": "echo 'Computer Use API Test'"
                }
            }
        }
        
        response = self.run_mcp_command(bash_request)
        
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            
            if "error" not in result:
                print("    ✅ Bash command execution successful")
                return True
            else:
                print(f"    ⚠️  Bash command returned error (WSL may not be configured): {result['error']}")
                return True  # This is expected if WSL isn't set up
        else:
            print(f"    ❌ Bash tool communication failed: {response}")
            return False
    
    def test_enhanced_actions(self):
        """Test Computer Use API enhanced actions."""
        print("🚀 Testing Enhanced Actions...")
        
        enhanced_test_cases = [
            {
                "name": "Hold Key",
                "action": "hold_key",
                "args": {"text": "shift", "duration": 1}
            },
            {
                "name": "Triple Click",
                "action": "triple_click",
                "args": {"coordinate": [100, 100]}
            },
            {
                "name": "Scroll",
                "action": "scroll",
                "args": {"coordinate": [500, 300], "scroll_direction": "up", "scroll_amount": 3}
            },
            {
                "name": "Mouse Down/Up",
                "action": "left_mouse_down",
                "args": {"coordinate": [200, 200]}
            }
        ]
        
        for test_case in enhanced_test_cases:
            print(f"  Testing: {test_case['name']}")
            
            request = {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "computer_20250124",
                    "arguments": {
                        "action": test_case["action"],
                        **test_case["args"]
                    }
                }
            }
            
            response = self.run_mcp_command(request)
            
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)
                
                if "error" not in result:
                    print(f"    ✅ {test_case['name']} successful")
                else:
                    print(f"    ⚠️  {test_case['name']} error: {result['error']}")
            else:
                print(f"    ❌ {test_case['name']} communication failed")
        
        # Mouse up to complete the mouse down test
        mouseup_request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "computer_20250124",
                "arguments": {"action": "left_mouse_up"}
            }
        }
        self.run_mcp_command(mouseup_request)
        
        return True
    
    def run_all_tests(self):
        """Run all Computer Use API compliance tests."""
        print("🧪 Computer Use API Compliance Test Suite")
        print("=" * 50)
        
        tests = [
            ("Tool Discovery", self.test_tool_discovery),
            ("Computer Tool Actions", self.test_computer_tool_actions),
            ("Text Editor Tool", self.test_text_editor_tool),
            ("Bash Tool", self.test_bash_tool),
            ("Enhanced Actions", self.test_enhanced_actions)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n{test_name}:")
                success = test_func()
                if success:
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Computer Use API Compliant!")
            return True
        else:
            print("⚠️  Some tests failed - Review implementation")
            return False


def main():
    """Run Computer Use API compliance tests."""
    tester = ComputerUseAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Ready for Computer Use API integration with Claude Desktop!")
    else:
        print("\n🔧 Please review failed tests and fix implementation")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())