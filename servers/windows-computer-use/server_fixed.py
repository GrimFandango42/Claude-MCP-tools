#!/usr/bin/env python3
"""
Windows Computer Use MCP Server - Computer Use API Compliant
Provides Computer Use API compatible tools for Windows desktop automation.

This server implements the exact tool specifications from Anthropic's Computer Use API:
- computer_20250124: Enhanced computer control with all actions
- text_editor_20250429: File editing without undo_edit command  
- bash_20250124: WSL command execution

Compatible with Claude 4, Claude Sonnet 3.7, and Claude Desktop.
"""

import sys
import json
import base64
import subprocess
import time
from typing import Dict, Any, List, Optional, Tuple
import pyautogui
from PIL import ImageGrab, Image
import tempfile
import os
from pathlib import Path
import io

try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class ComputerUseAPI:
    """Computer Use API compliant implementation for Windows."""
    
    def __init__(self):
        # Get screen dimensions for tool configuration
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_directory = os.getcwd()
        self.editor_files = {}  # Track open files for text editor
        
        # Log initialization to stderr only
        print(f"[windows-computer-use] Initialized: {self.screen_width}x{self.screen_height}", file=sys.stderr)
        
    def computer_20250124(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Enhanced computer control tool compatible with Computer Use API.
        
        Actions: key, hold_key, type, cursor_position, mouse_move, left_mouse_down,
        left_mouse_up, left_click, left_click_drag, right_click, middle_click, 
        double_click, triple_click, scroll, wait, screenshot
        """
        try:
            # Dispatch to appropriate handler based on action
            if action == "screenshot":
                return self._take_screenshot()
            
            elif action == "cursor_position":
                x, y = pyautogui.position()
                return {"output": f"Cursor position: {x}, {y}", "position": [x, y]}
            
            elif action == "mouse_move":
                coordinate = kwargs.get("coordinate", [0, 0])
                if len(coordinate) != 2:
                    return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                
                pyautogui.moveTo(coordinate[0], coordinate[1])
                return {"output": f"Mouse moved to {coordinate[0]}, {coordinate[1]}"}
            
            elif action == "left_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.click(coordinate[0], coordinate[1])
                    return {"output": f"Left click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.click()
                    x, y = pyautogui.position()
                    return {"output": f"Left click at current position {x}, {y}"}
            
            elif action == "right_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.rightClick(coordinate[0], coordinate[1])
                    return {"output": f"Right click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.rightClick()
                    x, y = pyautogui.position()
                    return {"output": f"Right click at current position {x}, {y}"}
            
            elif action == "middle_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.middleClick(coordinate[0], coordinate[1])
                    return {"output": f"Middle click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.middleClick()
                    x, y = pyautogui.position()
                    return {"output": f"Middle click at current position {x}, {y}"}
            
            elif action == "double_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.doubleClick(coordinate[0], coordinate[1])
                    return {"output": f"Double click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.doubleClick()
                    x, y = pyautogui.position()
                    return {"output": f"Double click at current position {x}, {y}"}
                    
            elif action == "triple_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.tripleClick(coordinate[0], coordinate[1])
                    return {"output": f"Triple click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.tripleClick()
                    x, y = pyautogui.position()
                    return {"output": f"Triple click at current position {x}, {y}"}
            
            elif action == "left_click_drag":
                start = kwargs.get("start_coordinate")
                end = kwargs.get("end_coordinate")
                if not start or not end or len(start) != 2 or len(end) != 2:
                    return {"output": "ERROR: Invalid drag coordinates. Expected start_coordinate and end_coordinate as [x, y]"}
                
                pyautogui.moveTo(start[0], start[1])
                pyautogui.dragTo(end[0], end[1], button='left')
                return {"output": f"Dragged from {start[0]}, {start[1]} to {end[0]}, {end[1]}"}
                
            elif action == "left_mouse_down":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.moveTo(coordinate[0], coordinate[1])
                    pyautogui.mouseDown(button='left')
                    return {"output": f"Left mouse down at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.mouseDown(button='left')
                    x, y = pyautogui.position()
                    return {"output": f"Left mouse down at current position {x}, {y}"}
                    
            elif action == "left_mouse_up":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    if len(coordinate) != 2:
                        return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
                    pyautogui.moveTo(coordinate[0], coordinate[1])
                    pyautogui.mouseUp(button='left')
                    return {"output": f"Left mouse up at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.mouseUp(button='left')
                    x, y = pyautogui.position()
                    return {"output": f"Left mouse up at current position {x}, {y}"}
            
            elif action == "key":
                key_to_press = kwargs.get("key")
                if not key_to_press:
                    return {"output": "ERROR: No key specified"}
                
                pyautogui.press(key_to_press)
                return {"output": f"Pressed key: {key_to_press}"}
                
            elif action == "hold_key":
                key_to_hold = kwargs.get("key")
                if not key_to_hold:
                    return {"output": "ERROR: No key specified"}
                
                duration = kwargs.get("duration", 1.0)
                pyautogui.keyDown(key_to_hold)
                time.sleep(duration)
                pyautogui.keyUp(key_to_hold)
                return {"output": f"Held key {key_to_hold} for {duration} seconds"}
            
            elif action == "type":
                text = kwargs.get("text")
                if not text:
                    return {"output": "ERROR: No text specified"}
                
                pyautogui.typewrite(text)
                return {"output": f"Typed text: '{text}'"}
                
            elif action == "scroll":
                direction = kwargs.get("direction", "down")
                clicks = kwargs.get("clicks", 1)
                
                if direction == "down":
                    pyautogui.scroll(-clicks)  # Negative for down
                    return {"output": f"Scrolled down {clicks} clicks"}
                elif direction == "up":
                    pyautogui.scroll(clicks)  # Positive for up
                    return {"output": f"Scrolled up {clicks} clicks"}
                else:
                    return {"output": f"ERROR: Invalid scroll direction: {direction}. Use 'up' or 'down'"}
                    
            elif action == "wait":
                duration = kwargs.get("duration", 1.0)
                time.sleep(duration)
                return {"output": f"Waited for {duration} seconds"}
            
            else:
                return {"output": f"ERROR: Unknown action: {action}"}
                
        except Exception as e:
            return {"output": f"ERROR: Action '{action}' failed: {str(e)}"}
    
    def text_editor_20250429(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Enhanced text editor tool without undo_edit (Claude 4 Computer Use API spec).
        
        Commands: view, create, str_replace
        """
        try:
            if command == "view":
                path = kwargs.get("path")
                if not path:
                    return {"output": "ERROR: No file path specified"}
                
                # Convert to Path object for proper handling
                file_path = Path(path)
                
                if not file_path.exists():
                    return {"output": f"ERROR: File not found: {path}"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Handle view range if specified
                view_range = kwargs.get("view_range")
                if view_range and len(view_range) == 2:
                    start, end = view_range
                    lines = content.split('\n')
                    
                    if start < 0:
                        start = 0
                    if end >= len(lines):
                        end = len(lines) - 1
                    
                    if start <= end:
                        limited_content = '\n'.join(lines[start:end+1])
                        return {
                            "output": f"Viewing file {path} (lines {start}-{end})",
                            "file_text": limited_content,
                            "start_line": start,
                            "end_line": end
                        }
                    else:
                        return {"output": f"ERROR: Invalid view range: {start}-{end}"}
                
                return {
                    "output": f"Viewing file {path}",
                    "file_text": content
                }
            
            elif command == "create":
                path = kwargs.get("path")
                file_text = kwargs.get("file_text", "")
                
                if not path:
                    return {"output": "ERROR: No file path specified"}
                
                # Convert to Path object for proper handling
                file_path = Path(path)
                
                # Create directory if it doesn't exist
                if not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_text)
                
                return {"output": f"Created file: {path}"}
            
            elif command == "str_replace":
                path = kwargs.get("path")
                old_str = kwargs.get("old_str")
                new_str = kwargs.get("new_str")
                
                if not path:
                    return {"output": "ERROR: No file path specified"}
                if old_str is None:
                    return {"output": "ERROR: No text to replace specified"}
                if new_str is None:
                    return {"output": "ERROR: No replacement text specified"}
                
                # Convert to Path object for proper handling
                file_path = Path(path)
                
                if not file_path.exists():
                    return {"output": f"ERROR: File not found: {path}"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Perform the replacement
                new_content = content.replace(old_str, new_str)
                
                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Count replacements
                count = content.count(old_str)
                return {"output": f"Replaced {count} occurrence(s) in {path}"}
            
            else:
                return {"output": f"ERROR: Unknown command: {command}"}
        
        except Exception as e:
            return {"output": f"ERROR: Text editor command '{command}' failed: {str(e)}"}
    
    def bash_20250124(self, command: str) -> Dict[str, Any]:
        """
        Enhanced bash tool with improved capabilities. Execute bash commands in WSL environment.
        """
        try:
            # Use wsl command to execute bash commands in WSL
            process = subprocess.Popen(
                ['wsl', 'bash', '-c', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Set a timeout to prevent hanging
            try:
                stdout, stderr = process.communicate(timeout=30)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                return {"output": "ERROR: Command timed out after 30 seconds"}
            
            # Return results
            if exit_code == 0:
                return {"output": stdout.strip()}
            else:
                error_msg = stderr.strip() if stderr else f"Command failed with exit code {exit_code}"
                return {"output": f"ERROR: {error_msg}\n{stdout.strip()}"}
                
        except Exception as e:
            return {"output": f"ERROR: Failed to execute bash command: {str(e)}"}
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot and return base64 encoded image."""
        try:
            # Capture screenshot using PIL's ImageGrab
            screenshot = ImageGrab.grab()
            
            # Save to bytes buffer instead of file
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            
            # Encode as base64
            image_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            img_buffer.close()
            
            return {
                "output": f"Screenshot taken: {screenshot.size[0]}x{screenshot.size[1]}",
                "image": image_data,
                "width": screenshot.size[0],
                "height": screenshot.size[1]
            }
            
        except Exception as e:
            return {"output": f"ERROR: Screenshot failed: {str(e)}"}


def main():
    """Main MCP server implementation."""
    print("[windows-computer-use] Starting server...", file=sys.stderr)
    computer_api = ComputerUseAPI()
    
    # Read input from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            
            # Handle MCP protocol
            if request.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "windows-computer-use",
                            "version": "2.0.0"
                        }
                    }
                }
            
            elif request.get("method") == "tools/list":
                tools = [
                    {
                        "name": "computer_20250124",
                        "description": "Computer control tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["screenshot", "cursor_position", "mouse_move", "left_click", 
                                           "right_click", "middle_click", "double_click", "triple_click",
                                           "left_click_drag", "left_mouse_down", "left_mouse_up", "scroll",
                                           "key", "hold_key", "type", "wait"]
                                },
                                "coordinate": {
                                    "type": "array",
                                    "items": {"type": "number"}
                                },
                                "start_coordinate": {
                                    "type": "array", 
                                    "items": {"type": "number"}
                                },
                                "end_coordinate": {
                                    "type": "array",
                                    "items": {"type": "number"}
                                },
                                "text": {
                                    "type": "string"
                                },
                                "key": {
                                    "type": "string"
                                },
                                "direction": {
                                    "type": "string",
                                    "enum": ["up", "down"]
                                },
                                "clicks": {
                                    "type": "number"
                                },
                                "duration": {
                                    "type": "number"
                                }
                            },
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "text_editor_20250429",
                        "description": "Text file editor",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "enum": ["view", "create", "str_replace"]
                                },
                                "path": {
                                    "type": "string"
                                },
                                "file_text": {
                                    "type": "string"
                                },
                                "old_str": {
                                    "type": "string"
                                },
                                "new_str": {
                                    "type": "string"
                                },
                                "view_range": {
                                    "type": "array",
                                    "items": {"type": "number"}
                                }
                            },
                            "required": ["command", "path"]
                        }
                    },
                    {
                        "name": "bash_20250124",
                        "description": "Execute bash commands in WSL",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string"
                                }
                            },
                            "required": ["command"]
                        }
                    }
                ]
                response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id"),
                    "result": {
                        "tools": tools
                    }
                }
            
            elif request.get("method") == "resources/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "resources": []
                    }
                }
            
            elif request.get("method") == "prompts/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "prompts": []
                    }
                }
            
            elif request.get("method") == "tools/call":
                tool_name = request["params"]["name"]
                arguments = request["params"]["arguments"]
                
                if tool_name == "computer_20250124":
                    action = arguments.get("action")
                    result = computer_api.computer_20250124(action, **arguments)
                
                elif tool_name == "text_editor_20250429":
                    command = arguments.get("command")
                    result = computer_api.text_editor_20250429(command, **arguments)
                
                elif tool_name == "bash_20250124":
                    command = arguments.get("command")
                    result = computer_api.bash_20250124(command)
                
                else:
                    result = {"output": f"ERROR: Unknown tool: {tool_name}"}
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {request.get('method')}"
                    }
                }
            
            # Send response
            print(json.dumps(response), flush=True)
            print(f"[windows-computer-use] Message from server: {json.dumps(response)}", file=sys.stderr)
            
        except json.JSONDecodeError as e:
            print(f"[windows-computer-use] ERROR: Invalid JSON: {str(e)}", file=sys.stderr)
        
        except Exception as e:
            print(f"[windows-computer-use] ERROR: {str(e)}", file=sys.stderr)
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
                pass  # Last resort error handling


if __name__ == "__main__":
    main()