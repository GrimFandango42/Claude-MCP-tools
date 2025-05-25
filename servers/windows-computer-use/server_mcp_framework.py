#!/usr/bin/env python3
"""
Windows Computer Use MCP Server - Proper MCP Framework Implementation
Computer Use API compliant with proper async MCP framework integration.
"""

import asyncio
import base64
import json
import logging
import subprocess
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import pyautogui
from PIL import Image, ImageGrab
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("windows-computer-use")

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class WindowsComputerUseServer:
    """Windows Computer Use MCP Server with proper framework integration"""
    
    def __init__(self):
        self.server = Server("windows-computer-use")
        self.screen_width, self.screen_height = pyautogui.size()
        
        logger.info(f"Windows Computer Use Server initialized: {self.screen_width}x{self.screen_height}")
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Computer Use API compliant tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="computer_20250124",
                    description="Enhanced computer control with all Computer Use API actions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": [
                                    "screenshot", "cursor_position", "mouse_move", "left_click", 
                                    "right_click", "middle_click", "double_click", "triple_click",
                                    "left_click_drag", "left_mouse_down", "left_mouse_up", "scroll",
                                    "key", "hold_key", "type", "wait"
                                ]
                            },
                            "coordinate": {"type": "array", "items": {"type": "number"}},
                            "start_coordinate": {"type": "array", "items": {"type": "number"}},
                            "end_coordinate": {"type": "array", "items": {"type": "number"}},
                            "text": {"type": "string"},
                            "key": {"type": "string"},
                            "direction": {"type": "string", "enum": ["up", "down"]},
                            "clicks": {"type": "number"},
                            "duration": {"type": "number"}
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="text_editor_20250429",
                    description="Text file editor without undo_edit (Computer Use API spec)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "enum": ["view", "create", "str_replace"]},
                            "path": {"type": "string"},
                            "file_text": {"type": "string"},
                            "old_str": {"type": "string"},
                            "new_str": {"type": "string"},
                            "view_range": {"type": "array", "items": {"type": "number"}}
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
                            "command": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                logger.info(f"Executing tool: {name} with arguments: {arguments}")
                
                if name == "computer_20250124":
                    result = await self._computer_action(**arguments)
                elif name == "text_editor_20250429":
                    result = await self._text_editor_action(**arguments)
                elif name == "bash_20250124":
                    result = await self._bash_action(**arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                
            except Exception as e:
                error_msg = f"Error executing tool {name}: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "success": False
                }, indent=2))]
    
    async def _computer_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """Handle computer control actions"""
        try:
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
                    pyautogui.rightClick(coordinate[0], coordinate[1])
                    return {"output": f"Right click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.rightClick()
                    x, y = pyautogui.position()
                    return {"output": f"Right click at current position {x}, {y}"}
            
            elif action == "double_click":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    pyautogui.doubleClick(coordinate[0], coordinate[1])
                    return {"output": f"Double click at {coordinate[0]}, {coordinate[1]}"}
                else:
                    pyautogui.doubleClick()
                    x, y = pyautogui.position()
                    return {"output": f"Double click at current position {x}, {y}"}
            
            elif action == "type":
                text = kwargs.get("text")
                if not text:
                    return {"output": "ERROR: No text specified"}
                pyautogui.typewrite(text)
                return {"output": f"Typed text: '{text}'"}
            
            elif action == "key":
                key_to_press = kwargs.get("key")
                if not key_to_press:
                    return {"output": "ERROR: No key specified"}
                pyautogui.press(key_to_press)
                return {"output": f"Pressed key: {key_to_press}"}
            
            elif action == "scroll":
                direction = kwargs.get("direction", "down")
                clicks = kwargs.get("clicks", 1)
                if direction == "down":
                    pyautogui.scroll(-clicks)
                    return {"output": f"Scrolled down {clicks} clicks"}
                elif direction == "up":
                    pyautogui.scroll(clicks)
                    return {"output": f"Scrolled up {clicks} clicks"}
                else:
                    return {"output": f"ERROR: Invalid scroll direction: {direction}"}
            
            elif action == "wait":
                duration = kwargs.get("duration", 1.0)
                await asyncio.sleep(duration)
                return {"output": f"Waited for {duration} seconds"}
            
            else:
                return {"output": f"ERROR: Unknown action: {action}"}
                
        except Exception as e:
            return {"output": f"ERROR: Action '{action}' failed: {str(e)}"}
    
    async def _text_editor_action(self, command: str, **kwargs) -> Dict[str, Any]:
        """Handle text editor actions"""
        try:
            if command == "view":
                path = kwargs.get("path")
                if not path:
                    return {"output": "ERROR: No file path specified"}
                
                file_path = Path(path)
                if not file_path.exists():
                    return {"output": f"ERROR: File not found: {path}"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                view_range = kwargs.get("view_range")
                if view_range and len(view_range) == 2:
                    start, end = view_range
                    lines = content.split('\n')
                    if 0 <= start <= end < len(lines):
                        limited_content = '\n'.join(lines[start:end+1])
                        return {
                            "output": f"Viewing file {path} (lines {start}-{end})",
                            "file_text": limited_content
                        }
                
                return {"output": f"Viewing file {path}", "file_text": content}
            
            elif command == "create":
                path = kwargs.get("path")
                file_text = kwargs.get("file_text", "")
                
                if not path:
                    return {"output": "ERROR: No file path specified"}
                
                file_path = Path(path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_text)
                
                return {"output": f"Created file: {path}"}
            
            elif command == "str_replace":
                path = kwargs.get("path")
                old_str = kwargs.get("old_str")
                new_str = kwargs.get("new_str")
                
                if not path or old_str is None or new_str is None:
                    return {"output": "ERROR: Missing required parameters"}
                
                file_path = Path(path)
                if not file_path.exists():
                    return {"output": f"ERROR: File not found: {path}"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content.replace(old_str, new_str)
                count = content.count(old_str)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return {"output": f"Replaced {count} occurrence(s) in {path}"}
            
            else:
                return {"output": f"ERROR: Unknown command: {command}"}
        
        except Exception as e:
            return {"output": f"ERROR: Text editor command '{command}' failed: {str(e)}"}
    
    async def _bash_action(self, command: str) -> Dict[str, Any]:
        """Handle bash commands via WSL"""
        try:
            process = subprocess.Popen(
                ['wsl', 'bash', '-c', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=30)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                return {"output": "ERROR: Command timed out after 30 seconds"}
            
            if exit_code == 0:
                return {"output": stdout.strip()}
            else:
                error_msg = stderr.strip() if stderr else f"Command failed with exit code {exit_code}"
                return {"output": f"ERROR: {error_msg}\n{stdout.strip()}"}
                
        except Exception as e:
            return {"output": f"ERROR: Failed to execute bash command: {str(e)}"}
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot and return base64 encoded image"""
        try:
            screenshot = ImageGrab.grab()
            img_buffer = BytesIO()
            screenshot.save(img_buffer, format="PNG")
            img_buffer.seek(0)
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
    """Main entry point"""
    logger.info("Starting Windows Computer Use MCP Server")
    
    server = WindowsComputerUseServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
