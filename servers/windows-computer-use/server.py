#!/usr/bin/env python3
"""
Windows Computer Use MCP Server - MCP Framework Implementation
Computer Use API compliant server using proper MCP framework patterns.
"""

import sys
import json
import base64
import subprocess
import time
import asyncio
from typing import Dict, Any, List, Optional, Sequence
import pyautogui
from PIL import ImageGrab, Image
import tempfile
import os
from pathlib import Path
import io

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.server.stdio

try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("[windows-computer-use] WARNING: pywin32 not available", file=sys.stderr)

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class WindowsComputerUseMCP:
    """Windows Computer Use MCP Server with proper framework integration."""
    
    def __init__(self):
        self.server = Server("windows-computer-use")
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_directory = os.getcwd()
        
        print(f"[windows-computer-use] Initialized: {self.screen_width}x{self.screen_height}", file=sys.stderr)
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools with proper decorators."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="computer_20250124",
                    description="Computer control tool with enhanced capabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["screenshot", "cursor_position", "mouse_move", "left_click", 
                                       "right_click", "middle_click", "double_click", "triple_click",
                                       "left_click_drag", "left_mouse_down", "left_mouse_up", "scroll",
                                       "key", "hold_key", "type", "wait"],
                                "description": "The action to perform"
                            },
                            "coordinate": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Screen coordinates [x, y]"
                            },
                            "start_coordinate": {
                                "type": "array", 
                                "items": {"type": "number"},
                                "description": "Start coordinates for drag operations [x, y]"
                            },
                            "end_coordinate": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "End coordinates for drag operations [x, y]"
                            },
                            "text": {
                                "type": "string",
                                "description": "Text to type"
                            },
                            "key": {
                                "type": "string",
                                "description": "Key to press"
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["up", "down"],
                                "description": "Scroll direction"
                            },
                            "clicks": {
                                "type": "number",
                                "description": "Number of scroll clicks"
                            },
                            "duration": {
                                "type": "number",
                                "description": "Duration in seconds"
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="text_editor_20250429",
                    description="Text file editor without undo functionality",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum": ["view", "create", "str_replace"],
                                "description": "Editor command to execute"
                            },
                            "path": {
                                "type": "string",
                                "description": "File path"
                            },
                            "file_text": {
                                "type": "string",
                                "description": "Content for creating files"
                            },
                            "old_str": {
                                "type": "string",
                                "description": "Text to replace"
                            },
                            "new_str": {
                                "type": "string",
                                "description": "Replacement text"
                            },
                            "view_range": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Line range to view [start, end]"
                            }
                        },
                        "required": ["command", "path"]
                    }
                ),
                Tool(
                    name="bash_20250124",
                    description="Execute bash commands in WSL environment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Bash command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "computer_20250124":
                    result = await self._handle_computer_action(arguments)
                elif name == "text_editor_20250429":
                    result = await self._handle_text_editor(arguments)
                elif name == "bash_20250124":
                    result = await self._handle_bash_command(arguments)
                else:
                    result = {"output": f"ERROR: Unknown tool: {name}"}
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                error_msg = f"ERROR: Tool '{name}' failed: {str(e)}"
                print(f"[windows-computer-use] {error_msg}", file=sys.stderr)
                return [TextContent(type="text", text=json.dumps({"output": error_msg}))]
    
    async def _handle_computer_action(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle computer control actions."""
        action = arguments.get("action")
        
        if action == "screenshot":
            return await self._take_screenshot()
        
        elif action == "cursor_position":
            x, y = pyautogui.position()
            return {"output": f"Cursor position: {x}, {y}", "position": [x, y]}
        
        elif action == "mouse_move":
            coordinate = arguments.get("coordinate", [0, 0])
            if len(coordinate) != 2:
                return {"output": "ERROR: Invalid coordinates. Expected [x, y]"}
            
            pyautogui.moveTo(coordinate[0], coordinate[1])
            return {"output": f"Mouse moved to {coordinate[0]}, {coordinate[1]}"}
        
        elif action == "left_click":
            coordinate = arguments.get("coordinate")
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
            coordinate = arguments.get("coordinate")
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
            coordinate = arguments.get("coordinate")
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
            coordinate = arguments.get("coordinate")
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
            coordinate = arguments.get("coordinate")
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
            start = arguments.get("start_coordinate")
            end = arguments.get("end_coordinate")
            if not start or not end or len(start) != 2 or len(end) != 2:
                return {"output": "ERROR: Invalid drag coordinates. Expected start_coordinate and end_coordinate as [x, y]"}
            
            pyautogui.moveTo(start[0], start[1])
            pyautogui.dragTo(end[0], end[1], button='left')
            return {"output": f"Dragged from {start[0]}, {start[1]} to {end[0]}, {end[1]}"}
            
        elif action == "left_mouse_down":
            coordinate = arguments.get("coordinate")
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
            coordinate = arguments.get("coordinate")
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
            key_to_press = arguments.get("key")
            if not key_to_press:
                return {"output": "ERROR: No key specified"}
            
            pyautogui.press(key_to_press)
            return {"output": f"Pressed key: {key_to_press}"}
            
        elif action == "hold_key":
            key_to_hold = arguments.get("key")
            if not key_to_hold:
                return {"output": "ERROR: No key specified"}
            
            duration = arguments.get("duration", 1.0)
            pyautogui.keyDown(key_to_hold)
            await asyncio.sleep(duration)
            pyautogui.keyUp(key_to_hold)
            return {"output": f"Held key {key_to_hold} for {duration} seconds"}
        
        elif action == "type":
            text = arguments.get("text")
            if not text:
                return {"output": "ERROR: No text specified"}
            
            pyautogui.typewrite(text)
            return {"output": f"Typed text: '{text}'"}
            
        elif action == "scroll":
            direction = arguments.get("direction", "down")
            clicks = arguments.get("clicks", 1)
            
            if direction == "down":
                pyautogui.scroll(-clicks)  # Negative for down
                return {"output": f"Scrolled down {clicks} clicks"}
            elif direction == "up":
                pyautogui.scroll(clicks)  # Positive for up
                return {"output": f"Scrolled up {clicks} clicks"}
            else:
                return {"output": f"ERROR: Invalid scroll direction: {direction}. Use 'up' or 'down'"}
                
        elif action == "wait":
            duration = arguments.get("duration", 1.0)
            await asyncio.sleep(duration)
            return {"output": f"Waited for {duration} seconds"}
        
        else:
            return {"output": f"ERROR: Unknown action: {action}"}
    
    async def _handle_text_editor(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text editor commands."""
        command = arguments.get("command")
        
        if command == "view":
            path = arguments.get("path")
            if not path:
                return {"output": "ERROR: No file path specified"}
            
            file_path = Path(path)
            
            if not file_path.exists():
                return {"output": f"ERROR: File not found: {path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle view range if specified
            view_range = arguments.get("view_range")
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
            path = arguments.get("path")
            file_text = arguments.get("file_text", "")
            
            if not path:
                return {"output": "ERROR: No file path specified"}
            
            file_path = Path(path)
            
            # Create directory if it doesn't exist
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_text)
            
            return {"output": f"Created file: {path}"}
        
        elif command == "str_replace":
            path = arguments.get("path")
            old_str = arguments.get("old_str")
            new_str = arguments.get("new_str")
            
            if not path:
                return {"output": "ERROR: No file path specified"}
            if old_str is None:
                return {"output": "ERROR: No text to replace specified"}
            if new_str is None:
                return {"output": "ERROR: No replacement text specified"}
            
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
    
    async def _handle_bash_command(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bash commands via WSL."""
        command = arguments.get("command")
        if not command:
            return {"output": "ERROR: No command specified"}
        
        try:
            # Use asyncio.create_subprocess_exec for async execution
            process = await asyncio.create_subprocess_exec(
                'wsl', 'bash', '-c', command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
                exit_code = process.returncode
            except asyncio.TimeoutError:
                process.kill()
                return {"output": "ERROR: Command timed out after 30 seconds"}
            
            # Decode output
            stdout_text = stdout.decode('utf-8').strip()
            stderr_text = stderr.decode('utf-8').strip()
            
            # Return results
            if exit_code == 0:
                return {"output": stdout_text}
            else:
                error_msg = stderr_text if stderr_text else f"Command failed with exit code {exit_code}"
                return {"output": f"ERROR: {error_msg}\n{stdout_text}"}
                
        except Exception as e:
            return {"output": f"ERROR: Failed to execute bash command: {str(e)}"}
    
    async def _take_screenshot(self) -> Dict[str, Any]:
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


async def main():
    """Main entry point with proper MCP framework integration."""
    print("[windows-computer-use] Starting MCP framework server...", file=sys.stderr)
    
    server_instance = WindowsComputerUseMCP()
    
    # Use stdio_server for proper stream handling
    async with stdio_server() as (read_stream, write_stream):
        print("[windows-computer-use] Server streams initialized", file=sys.stderr)
        await server_instance.server.run(
            read_stream, 
            write_stream,
            server_instance.server.create_initialization_options()
        )


if __name__ == "__main__":
    print("[windows-computer-use] Starting server process...", file=sys.stderr)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[windows-computer-use] Server shutdown requested", file=sys.stderr)
    except Exception as e:
        print(f"[windows-computer-use] FATAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
