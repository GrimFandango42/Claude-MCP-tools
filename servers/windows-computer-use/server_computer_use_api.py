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
import pywin32
from PIL import ImageGrab, Image
import tempfile
import os
from pathlib import Path

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
        
    def computer_20250124(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Enhanced computer control tool compatible with Computer Use API.
        
        Actions: key, hold_key, type, cursor_position, mouse_move, left_mouse_down,
        left_mouse_up, left_click, left_click_drag, right_click, middle_click, 
        double_click, triple_click, scroll, wait, screenshot
        """
        try:
            if action == "screenshot":
                return self._take_screenshot()
            
            elif action == "cursor_position":
                x, y = pyautogui.position()
                return {
                    "output": f"Cursor position: ({x}, {y})",
                    "coordinate": [x, y]
                }
            
            elif action == "mouse_move":
                coordinate = kwargs.get("coordinate")
                if not coordinate or len(coordinate) != 2:
                    return {"error": "mouse_move requires coordinate [x, y]"}
                x, y = coordinate
                pyautogui.moveTo(x, y)
                return {"output": f"Moved cursor to ({x}, {y})"}
            
            elif action == "left_click":
                coordinate = kwargs.get("coordinate")
                text = kwargs.get("text", "")  # Key combo to hold during click
                
                if coordinate:
                    x, y = coordinate
                    if text:  # Hold keys while clicking
                        with pyautogui.hold(text.split('+')):
                            pyautogui.click(x, y)
                    else:
                        pyautogui.click(x, y)
                    return {"output": f"Left clicked at ({x}, {y})"}
                else:
                    # Click at current position
                    if text:
                        with pyautogui.hold(text.split('+')):
                            pyautogui.click()
                    else:
                        pyautogui.click()
                    return {"output": "Left clicked at current position"}
            
            elif action == "right_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.rightClick(x, y)
                    return {"output": f"Right clicked at ({x}, {y})"}
                else:
                    pyautogui.rightClick()
                    return {"output": "Right clicked at current position"}
            
            elif action == "middle_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.middleClick(x, y)
                    return {"output": f"Middle clicked at ({x}, {y})"}
                else:
                    pyautogui.middleClick()
                    return {"output": "Middle clicked at current position"}
            
            elif action == "double_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.doubleClick(x, y)
                    return {"output": f"Double clicked at ({x}, {y})"}
                else:
                    pyautogui.doubleClick()
                    return {"output": "Double clicked at current position"}
            
            elif action == "triple_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.tripleClick(x, y)
                    return {"output": f"Triple clicked at ({x}, {y})"}
                else:
                    pyautogui.tripleClick()
                    return {"output": "Triple clicked at current position"}
            
            elif action == "left_mouse_down":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.moveTo(x, y)
                    pyautogui.mouseDown()
                    return {"output": f"Left mouse button pressed down at ({x}, {y})"}
                else:
                    pyautogui.mouseDown()
                    return {"output": "Left mouse button pressed down at current position"}
            
            elif action == "left_mouse_up":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.moveTo(x, y)
                    pyautogui.mouseUp()
                    return {"output": f"Left mouse button released at ({x}, {y})"}
                else:
                    pyautogui.mouseUp()
                    return {"output": "Left mouse button released at current position"}
            
            elif action == "left_click_drag":
                start_coordinate = kwargs.get("start_coordinate")
                coordinate = kwargs.get("coordinate")
                
                if not start_coordinate or not coordinate:
                    return {"error": "left_click_drag requires start_coordinate and coordinate"}
                
                start_x, start_y = start_coordinate
                end_x, end_y = coordinate
                
                pyautogui.dragTo(end_x, end_y, startPositionXY=(start_x, start_y))
                return {"output": f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"}
            
            elif action == "scroll":
                coordinate = kwargs.get("coordinate")
                scroll_direction = kwargs.get("scroll_direction", "up")
                scroll_amount = kwargs.get("scroll_amount", 3)
                text = kwargs.get("text", "")  # Key combo to hold during scroll
                
                if coordinate:
                    x, y = coordinate
                    pyautogui.moveTo(x, y)
                
                # Convert direction to scroll amount
                if scroll_direction == "up":
                    scroll_clicks = scroll_amount
                elif scroll_direction == "down":
                    scroll_clicks = -scroll_amount
                else:
                    scroll_clicks = scroll_amount if scroll_direction == "right" else -scroll_amount
                
                if text:  # Hold keys while scrolling
                    with pyautogui.hold(text.split('+')):
                        pyautogui.scroll(scroll_clicks)
                else:
                    pyautogui.scroll(scroll_clicks)
                
                location = f" at ({x}, {y})" if coordinate else ""
                return {"output": f"Scrolled {scroll_direction} {scroll_amount} clicks{location}"}
            
            elif action == "type":
                text = kwargs.get("text", "")
                if not text:
                    return {"error": "type action requires text parameter"}
                
                pyautogui.typewrite(text)
                return {"output": f"Typed: {text}"}
            
            elif action == "key":
                text = kwargs.get("text", "")
                if not text:
                    return {"error": "key action requires text parameter"}
                
                # Handle key combinations (e.g., "ctrl+s", "alt+Tab")
                if '+' in text:
                    pyautogui.hotkey(*text.split('+'))
                else:
                    pyautogui.press(text)
                
                return {"output": f"Pressed key: {text}"}
            
            elif action == "hold_key":
                text = kwargs.get("text", "")
                duration = kwargs.get("duration", 1)
                
                if not text:
                    return {"error": "hold_key action requires text parameter"}
                
                # Hold key for specified duration
                pyautogui.keyDown(text)
                time.sleep(duration)
                pyautogui.keyUp(text)
                
                return {"output": f"Held key '{text}' for {duration} seconds"}
            
            elif action == "wait":
                duration = kwargs.get("duration", 1)
                time.sleep(duration)
                return {"output": f"Waited for {duration} seconds"}
            
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"error": f"Computer action failed: {str(e)}"}
    
    def text_editor_20250429(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Text editor tool compatible with Computer Use API.
        Note: undo_edit command is NOT supported in this version.
        
        Commands: view, create, str_replace, str_replace_editor
        """
        try:
            if command == "view":
                path = kwargs.get("path", "")
                if not path:
                    return {"error": "view command requires path parameter"}
                
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.editor_files[path] = content
                    return {
                        "output": f"File content of {path}:\n{content}",
                        "path": path,
                        "content": content
                    }
                except FileNotFoundError:
                    return {"error": f"File not found: {path}"}
                except Exception as e:
                    return {"error": f"Failed to read file: {str(e)}"}
            
            elif command == "create":
                path = kwargs.get("path", "")
                file_text = kwargs.get("file_text", "")
                
                if not path:
                    return {"error": "create command requires path parameter"}
                
                try:
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(file_text)
                    
                    self.editor_files[path] = file_text
                    return {"output": f"Created file: {path}"}
                except Exception as e:
                    return {"error": f"Failed to create file: {str(e)}"}
            
            elif command == "str_replace":
                path = kwargs.get("path", "")
                old_str = kwargs.get("old_str", "")
                new_str = kwargs.get("new_str", "")
                
                if not all([path, old_str is not None]):
                    return {"error": "str_replace requires path and old_str parameters"}
                
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if old_str not in content:
                        return {"error": f"String not found in file: {old_str}"}
                    
                    new_content = content.replace(old_str, new_str)
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.editor_files[path] = new_content
                    return {"output": f"Replaced text in {path}"}
                except Exception as e:
                    return {"error": f"Failed to replace text: {str(e)}"}
            
            elif command == "str_replace_editor":
                # Alternative command name for compatibility
                return self.text_editor_20250429("str_replace", **kwargs)
            
            else:
                return {"error": f"Unknown text editor command: {command}. Supported: view, create, str_replace"}
                
        except Exception as e:
            return {"error": f"Text editor operation failed: {str(e)}"}
    
    def bash_20250124(self, command: str) -> Dict[str, Any]:
        """
        Enhanced bash shell tool for WSL command execution.
        Compatible with Computer Use API.
        """
        try:
            # Execute command in WSL environment
            if sys.platform == "win32":
                # Use WSL if available
                wsl_command = ["wsl", "bash", "-c", command]
                result = subprocess.run(
                    wsl_command,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.current_directory
                )
            else:
                # Direct bash execution on Unix systems
                result = subprocess.run(
                    ["bash", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.current_directory
                )
            
            output = result.stdout
            error = result.stderr
            exit_code = result.returncode
            
            response = {
                "output": output,
                "exit_code": exit_code
            }
            
            if error:
                response["error"] = error
            
            return response
            
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}
        except FileNotFoundError:
            return {"error": "WSL or bash not found. Please ensure WSL is installed and configured."}
        except Exception as e:
            return {"error": f"Bash command failed: {str(e)}"}
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot and return base64 encoded image."""
        try:
            screenshot = ImageGrab.grab()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                screenshot.save(tmp_file.name, 'PNG')
                
                # Read and encode as base64
                with open(tmp_file.name, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Clean up temp file
                os.unlink(tmp_file.name)
            
            return {
                "output": f"Screenshot taken: {screenshot.size[0]}x{screenshot.size[1]}",
                "image": image_data,
                "width": screenshot.size[0],
                "height": screenshot.size[1]
            }
            
        except Exception as e:
            return {"error": f"Screenshot failed: {str(e)}"}


def main():
    """Main MCP server implementation."""
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
                response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "computer_20250124",
                                "description": "Enhanced computer control with advanced features for Claude 4. Use mouse and keyboard to interact with a computer, and take screenshots.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {
                                            "type": "string",
                                            "enum": [
                                                "key", "hold_key", "type", "cursor_position", "mouse_move",
                                                "left_mouse_down", "left_mouse_up", "left_click", "left_click_drag",
                                                "right_click", "middle_click", "double_click", "triple_click",
                                                "scroll", "wait", "screenshot"
                                            ],
                                            "description": "The action to perform"
                                        },
                                        "coordinate": {
                                            "type": "array",
                                            "description": "(x, y) coordinates for mouse actions"
                                        },
                                        "start_coordinate": {
                                            "type": "array",
                                            "description": "Start coordinates for drag operations"
                                        },
                                        "text": {
                                            "type": "string",
                                            "description": "Text for type/key actions or key combinations for clicks"
                                        },
                                        "duration": {
                                            "type": "integer",
                                            "description": "Duration in seconds for hold_key/wait actions"
                                        },
                                        "scroll_direction": {
                                            "type": "string",
                                            "enum": ["up", "down", "left", "right"],
                                            "description": "Direction to scroll"
                                        },
                                        "scroll_amount": {
                                            "type": "integer",
                                            "description": "Number of scroll clicks"
                                        }
                                    },
                                    "required": ["action"]
                                }
                            },
                            {
                                "name": "text_editor_20250429",
                                "description": "Updated text editor without undo_edit command. Custom editing tool for viewing, creating and editing files.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {
                                            "type": "string",
                                            "enum": ["view", "create", "str_replace"],
                                            "description": "Text editor command to execute"
                                        },
                                        "path": {
                                            "type": "string",
                                            "description": "File path for the operation"
                                        },
                                        "file_text": {
                                            "type": "string",
                                            "description": "File content for create command"
                                        },
                                        "old_str": {
                                            "type": "string",
                                            "description": "String to replace in str_replace command"
                                        },
                                        "new_str": {
                                            "type": "string",
                                            "description": "Replacement string in str_replace command"
                                        }
                                    },
                                    "required": ["command"]
                                }
                            },
                            {
                                "name": "bash_20250124",
                                "description": "Enhanced bash shell with improved capabilities. Execute bash commands in WSL environment.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {
                                            "type": "string",
                                            "description": "Bash command to execute"
                                        }
                                    },
                                    "required": ["command"]
                                }
                            }
                        ]
                    }
                }
            
            elif request.get("method") == "tools/call":
                tool_name = request["params"]["name"]
                arguments = request["params"]["arguments"]
                
                if tool_name == "computer_20250124":
                    result = computer_api.computer_20250124(**arguments)
                elif tool_name == "text_editor_20250429":
                    result = computer_api.text_editor_20250429(**arguments)
                elif tool_name == "bash_20250124":
                    result = computer_api.bash_20250124(**arguments)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
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
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()