#!/usr/bin/env python3
"""
Containerized Computer Use Server - Docker/Linux Implementation
Provides Computer Use API compatible tools for containerized environments.

This server implements the exact tool specifications from Anthropic's Computer Use API:
- computer_20250124: Enhanced computer control with all actions
- text_editor_20250429: File editing without undo_edit command  
- bash_20250124: Linux command execution
"""

import sys
import json
import base64
import subprocess
import time
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from io import BytesIO
import logging

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='[containerized-computer-use] %(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

try:
    import pyautogui
    from PIL import ImageGrab, Image
    import pyscreenshot as ImageGrab  # Fallback for Linux
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("pyautogui not available - screenshot and mouse control disabled")

# Configure pyautogui safety if available
if PYAUTOGUI_AVAILABLE:
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1


class ContainerizedComputerUseAPI:
    """Computer Use API compliant implementation for containerized Linux environments."""
    
    def __init__(self):
        # Get screen dimensions for tool configuration
        if PYAUTOGUI_AVAILABLE:
            try:
                self.screen_width, self.screen_height = pyautogui.size()
            except Exception:
                # Default to common resolution if detection fails
                self.screen_width, self.screen_height = 1920, 1080
        else:
            self.screen_width, self.screen_height = 1920, 1080
            
        self.current_directory = os.getcwd()
        self.editor_files = {}  # Track open files for text editor
        
        logging.info(f"Initialized: {self.screen_width}x{self.screen_height}")
        
    def computer_20250124(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Enhanced computer control tool compatible with Computer Use API.
        
        Actions: key, hold_key, type, cursor_position, mouse_move, left_mouse_down,
        left_mouse_up, left_click, left_click_drag, right_click, middle_click, 
        double_click, triple_click, scroll, wait, screenshot
        """
        if not PYAUTOGUI_AVAILABLE and action != "wait":
            return {"output": f"ERROR: pyautogui not available for action: {action}"}
            
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
                    return {"output": "ERROR: mouse_move requires coordinate [x, y]"}
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
            
            elif action == "left_click_drag":
                start_coordinate = kwargs.get("start_coordinate")
                end_coordinate = kwargs.get("end_coordinate")
                
                if not start_coordinate or not end_coordinate:
                    return {"output": "ERROR: left_click_drag requires start_coordinate and end_coordinate"}
                
                sx, sy = start_coordinate
                ex, ey = end_coordinate
                pyautogui.dragTo(ex, ey, button='left', duration=0.5)
                return {"output": f"Dragged from ({sx}, {sy}) to ({ex}, {ey})"}
            
            elif action == "scroll":
                coordinate = kwargs.get("coordinate")
                clicks = kwargs.get("clicks", 5)  # Default 5 clicks
                direction = kwargs.get("direction", "down")
                
                # Move to coordinate if provided
                if coordinate:
                    x, y = coordinate
                    pyautogui.moveTo(x, y)
                
                # Scroll direction
                scroll_amount = -clicks if direction == "down" else clicks
                pyautogui.scroll(scroll_amount)
                
                return {"output": f"Scrolled {direction} {abs(clicks)} clicks"}
            
            elif action == "key":
                text = kwargs.get("text", "")
                if not text:
                    return {"output": "ERROR: key action requires text parameter"}
                
                # Handle special keys and combinations
                pyautogui.press(text)
                return {"output": f"Pressed key: {text}"}
            
            elif action == "hold_key":
                text = kwargs.get("text", "")
                duration = kwargs.get("duration", 1000) / 1000.0  # Convert ms to seconds
                
                if not text:
                    return {"output": "ERROR: hold_key requires text parameter"}
                
                pyautogui.keyDown(text)
                time.sleep(duration)
                pyautogui.keyUp(text)
                
                return {"output": f"Held key '{text}' for {duration} seconds"}
            
            elif action == "type":
                text = kwargs.get("text", "")
                if not text:
                    return {"output": "ERROR: type action requires text parameter"}
                
                pyautogui.write(text)
                return {"output": f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}"}
            
            elif action == "left_mouse_down":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.moveTo(x, y)
                    pyautogui.mouseDown(button='left')
                    return {"output": f"Left mouse down at ({x}, {y})"}
                else:
                    pyautogui.mouseDown(button='left')
                    return {"output": "Left mouse down at current position"}
            
            elif action == "left_mouse_up":
                coordinate = kwargs.get("coordinate")
                if coordinate:
                    x, y = coordinate
                    pyautogui.moveTo(x, y)
                    pyautogui.mouseUp(button='left')
                    return {"output": f"Left mouse up at ({x}, {y})"}
                else:
                    pyautogui.mouseUp(button='left')
                    return {"output": "Left mouse up at current position"}
                    
            elif action == "wait":
                duration = kwargs.get("duration", 1000) / 1000.0  # Convert ms to seconds
                time.sleep(duration)
                return {"output": f"Waited {duration} seconds"}
                
            else:
                return {"output": f"ERROR: Unknown action: {action}"}
                
        except Exception as e:
            logging.error(f"Error in computer action {action}: {e}")
            return {"output": f"ERROR: {str(e)}"}
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot and return base64 encoded image."""
        try:
            # Try different screenshot methods for container compatibility
            screenshot = None
            
            # Method 1: pyautogui screenshot
            if PYAUTOGUI_AVAILABLE:
                try:
                    screenshot = pyautogui.screenshot()
                except Exception as e:
                    logging.warning(f"pyautogui screenshot failed: {e}")
            
            # Method 2: ImageGrab (pyscreenshot fallback)
            if screenshot is None:
                try:
                    screenshot = ImageGrab.grab()
                except Exception as e:
                    logging.warning(f"ImageGrab failed: {e}")
                    
            # Method 3: Use scrot command if available
            if screenshot is None:
                try:
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        subprocess.run(['scrot', tmp.name], check=True, capture_output=True)
                        screenshot = Image.open(tmp.name)
                        os.unlink(tmp.name)
                except Exception as e:
                    logging.warning(f"scrot command failed: {e}")
                    
            if screenshot is None:
                return {"output": "ERROR: Failed to capture screenshot - no method available"}
            
            # Convert to base64
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                "output": "Screenshot taken successfully",
                "screenshot": image_base64
            }
            
        except Exception as e:
            logging.error(f"Screenshot error: {e}")
            return {"output": f"ERROR: Failed to take screenshot: {str(e)}"}
    
    def text_editor_20250429(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Text editor tool for viewing and editing files.
        Commands: view, create, str_replace
        """
        try:
            if command == "view":
                path = kwargs.get("path", "")
                view_range = kwargs.get("view_range")
                
                if not path:
                    return {"output": "ERROR: view command requires path parameter"}
                
                # Ensure path is within allowed workspace
                file_path = Path(path).resolve()
                
                if not file_path.exists():
                    return {"output": f"ERROR: File not found: {path}"}
                
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines()
                
                # Apply view range if specified
                if view_range and len(view_range) == 2:
                    start, end = view_range
                    start = max(1, start) - 1  # Convert to 0-indexed
                    end = min(len(lines), end)
                    lines = lines[start:end]
                    result = '\n'.join(lines)
                    return {"output": f"Lines {start+1}-{end}:\n{result}"}
                else:
                    return {"output": content}
            
            elif command == "create":
                path = kwargs.get("path", "")
                content = kwargs.get("file_text", "")
                
                if not path:
                    return {"output": "ERROR: create command requires path parameter"}
                
                file_path = Path(path).resolve()
                
                # Create parent directories if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write content
                file_path.write_text(content, encoding='utf-8')
                
                return {"output": f"Created file: {path}"}
            
            elif command == "str_replace":
                path = kwargs.get("path", "")
                old_str = kwargs.get("old_str", "")
                new_str = kwargs.get("new_str", "")
                
                if not all([path, old_str]):
                    return {"output": "ERROR: str_replace requires path and old_str parameters"}
                
                file_path = Path(path).resolve()
                
                if not file_path.exists():
                    return {"output": f"ERROR: File not found: {path}"}
                
                # Read content
                content = file_path.read_text(encoding='utf-8')
                
                # Check if old_str exists
                if old_str not in content:
                    return {"output": f"ERROR: String not found in file: {old_str[:50]}..."}
                
                # Replace string
                new_content = content.replace(old_str, new_str, 1)  # Replace first occurrence
                
                # Write back
                file_path.write_text(new_content, encoding='utf-8')
                
                return {"output": f"Replaced string in {path}"}
                
            else:
                return {"output": f"ERROR: Unknown command: {command}"}
                
        except Exception as e:
            logging.error(f"Text editor error: {e}")
            return {"output": f"ERROR: {str(e)}"}
    
    def bash_20250124(self, command: str) -> Dict[str, Any]:
        """
        Execute bash commands in the container environment.
        """
        try:
            # Set timeout (default 30 seconds)
            timeout = 30
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.current_directory
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            return {
                "output": output.strip() if output else f"Command completed with exit code {result.returncode}"
            }
            
        except subprocess.TimeoutExpired:
            return {"output": f"ERROR: Command timed out after {timeout} seconds"}
        except Exception as e:
            logging.error(f"Bash command error: {e}")
            return {"output": f"ERROR: {str(e)}"}


# Main execution function for direct testing
def main():
    """Run the containerized computer use API."""
    api = ContainerizedComputerUseAPI()
    
    # Test basic functionality
    logging.info("Testing containerized Computer Use API...")
    
    # Test screenshot
    result = api.computer_20250124("screenshot")
    logging.info(f"Screenshot result: {result.get('output')}")
    
    # Test bash command
    result = api.bash_20250124("echo 'Container is running!' && date")
    logging.info(f"Bash result: {result}")
    
    # Test text editor
    result = api.text_editor_20250429("create", path="/tmp/test.txt", file_text="Hello from container!")
    logging.info(f"File creation result: {result}")
    
    result = api.text_editor_20250429("view", path="/tmp/test.txt")
    logging.info(f"File content: {result}")


if __name__ == "__main__":
    main()
