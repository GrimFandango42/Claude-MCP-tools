#!/usr/bin/env python3
"""
Minimal Windows Computer Use MCP Server
Stripped-down implementation focusing on protocol compliance.
"""

import sys
import json
import base64
import subprocess
import time
import io
from typing import Dict, Any
import pyautogui
from PIL import ImageGrab

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Never use print() for logging - only for JSON-RPC protocol messages
# All logs must go to stderr
def log(message):
    print(f"[windows-computer-use] {message}", file=sys.stderr, flush=True)

class ComputerUseAPI:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        log(f"Initialized: {self.screen_width}x{self.screen_height}")
        
    def take_screenshot(self):
        try:
            screenshot = ImageGrab.grab()
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            image_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            img_buffer.close()
            
            return {
                "output": f"Screenshot taken: {screenshot.size[0]}x{screenshot.size[1]}",
                "image": image_data
            }
        except Exception as e:
            return {"output": f"ERROR: Screenshot failed: {str(e)}"}
            
    def execute_bash(self, command):
        try:
            process = subprocess.Popen(
                ['wsl', 'bash', '-c', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=30)
            if process.returncode == 0:
                return {"output": stdout.strip()}
            else:
                return {"output": f"ERROR: {stderr.strip()}\n{stdout.strip()}"}
        except Exception as e:
            return {"output": f"ERROR: Failed to execute bash command: {str(e)}"}

def main():
    log("Starting minimal server...")
    api = ComputerUseAPI()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method", "")
            request_id = request.get("id")
            
            log(f"Received method: {method} (id: {request_id})")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "windows-computer-use", "version": "1.0.0"}
                    }
                }
                
            elif method == "tools/list":
                tools = [
                    {
                        "name": "computer_20250124",
                        "description": "Computer control",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["screenshot"]}
                            },
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "bash_20250124",
                        "description": "Execute bash",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string"}
                            },
                            "required": ["command"]
                        }
                    }
                ]
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
                
            elif method == "resources/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"resources": []}
                }
                
            elif method == "prompts/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"prompts": []}
                }
                
            elif method == "tools/call":
                tool_name = request["params"]["name"]
                arguments = request["params"]["arguments"]
                
                if tool_name == "computer_20250124":
                    action = arguments.get("action")
                    if action == "screenshot":
                        result = api.take_screenshot()
                    else:
                        result = {"output": f"ERROR: Unknown action: {action}"}
                        
                elif tool_name == "bash_20250124":
                    command = arguments.get("command")
                    result = api.execute_bash(command)
                    
                else:
                    result = {"output": f"ERROR: Unknown tool: {tool_name}"}
                    
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Send JSON-RPC response to stdout - CRITICAL to separate from logging
            json_response = json.dumps(response)
            sys.stdout.write(json_response + '\n')
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            log(f"ERROR: Invalid JSON: {str(e)}")
            
        except Exception as e:
            log(f"ERROR: {str(e)}")
            try:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except:
                pass

if __name__ == "__main__":
    main()