#!/usr/bin/env python3
"""
Windows Computer Use MCP Server

Provides Claude Computer Use capabilities adapted for Windows environments with WSL integration.
This server implements Windows-native automation tools that bridge to WSL for development tasks.
"""

import asyncio
import json
import sys
import signal
import traceback
import base64
import io
from typing import Any, Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Windows-specific imports
import win32gui
import win32con
import win32api
import win32clipboard
from PIL import Image, ImageGrab
import pyautogui
import subprocess

# MCP Framework
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool

# Configure logging to stderr with JSON format
import json_logging

# Initialize JSON logging
json_logging.init_non_web(enable_json=True)
logger = logging.getLogger("windows-computer-use")
logger.setLevel(logging.INFO)

# Configure stderr handler
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.INFO)
logger.addHandler(stderr_handler)

# Initialize FastMCP server
mcp = FastMCP("windows-computer-use")

# Global state for screenshots and automation
current_screenshot: Optional[bytes] = None
display_info = {
    "width": 0,
    "height": 0,
    "scale_factor": 1.0
}

def initialize_display_info():
    """Initialize display information for Windows environment."""
    global display_info
    try:
        # Get primary display dimensions
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # Get DPI scaling factor
        hdc = win32gui.GetDC(0)
        dpi_x = win32gui.GetDeviceCaps(hdc, win32con.LOGPIXELSX)
        win32gui.ReleaseDC(0, hdc)
        scale_factor = dpi_x / 96.0  # 96 DPI is baseline
        
        display_info = {
            "width": screen_width,
            "height": screen_height,
            "scale_factor": scale_factor
        }
        
        logger.info(f"Display initialized: {screen_width}x{screen_height}, scale: {scale_factor}")
        
    except Exception as e:
        logger.error(f"Failed to initialize display info: {e}")
        # Fallback values
        display_info = {
            "width": 1920,
            "height": 1080,
            "scale_factor": 1.0
        }

def capture_screenshot() -> bytes:
    """Capture screenshot of the Windows desktop."""
    global current_screenshot
    
    try:
        # Capture screenshot using PIL
        screenshot = ImageGrab.grab()
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        screenshot_bytes = img_buffer.getvalue()
        
        # Store for reference
        current_screenshot = screenshot_bytes
        
        logger.info(f"Screenshot captured: {len(screenshot_bytes)} bytes")
        return screenshot_bytes
        
    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        raise

def execute_wsl_command(command: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
    """Execute a command in WSL environment."""
    try:
        # Construct WSL command
        wsl_cmd = ["wsl"]
        
        if working_dir:
            # Convert Windows path to WSL path if needed
            if working_dir.startswith("C:"):
                wsl_path = working_dir.replace("C:", "/mnt/c").replace("\\", "/")
                wsl_cmd.extend(["--cd", wsl_path])
        
        wsl_cmd.extend(["--", "bash", "-c", command])
        
        logger.info(f"Executing WSL command: {' '.join(wsl_cmd)}")
        
        # Execute command
        result = subprocess.run(
            wsl_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"WSL command timeout: {command}")
        return {
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "returncode": -1,
            "success": False
        }
    except Exception as e:
        logger.error(f"WSL command execution failed: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "success": False
        }

@mcp.tool()
def windows_computer_screenshot() -> str:
    """
    Take a screenshot of the Windows desktop.
    
    Returns:
        Base64-encoded PNG image of the current desktop.
    """
    try:
        screenshot_bytes = capture_screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return json.dumps({
            "type": "screenshot",
            "format": "png",
            "data": screenshot_b64,
            "width": display_info["width"],
            "height": display_info["height"],
            "scale_factor": display_info["scale_factor"]
        })
        
    except Exception as e:
        logger.error(f"Screenshot tool error: {e}")
        return json.dumps({
            "type": "error",
            "message": f"Screenshot failed: {str(e)}"
        })

@mcp.tool()
def windows_computer_click(x: int, y: int, button: str = "left", click_count: int = 1) -> str:
    """
    Click at specified coordinates on the Windows desktop.
    
    Args:
        x: X coordinate to click
        y: Y coordinate to click  
        button: Mouse button ("left", "right", "middle")
        click_count: Number of clicks (1 for single, 2 for double)
    
    Returns:
        JSON result of the click operation.
    """
    try:
        # Validate coordinates
        if not (0 <= x <= display_info["width"]) or not (0 <= y <= display_info["height"]):
            raise ValueError(f"Coordinates ({x}, {y}) out of screen bounds")
        
        # Map button names
        button_map = {
            "left": "left",
            "right": "right", 
            "middle": "middle"
        }
        
        if button not in button_map:
            raise ValueError(f"Invalid button: {button}")
        
        # Perform click using pyautogui
        if click_count == 1:
            pyautogui.click(x, y, button=button_map[button])
        elif click_count == 2:
            pyautogui.doubleClick(x, y, button=button_map[button])
        else:
            for _ in range(click_count):
                pyautogui.click(x, y, button=button_map[button])
        
        logger.info(f"Clicked at ({x}, {y}) with {button} button, {click_count} times")
        
        return json.dumps({
            "type": "click",
            "x": x,
            "y": y,
            "button": button,
            "click_count": click_count,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Click operation failed: {e}")
        return json.dumps({
            "type": "error",
            "message": f"Click failed: {str(e)}"
        })

@mcp.tool()
def windows_computer_type(text: str) -> str:
    """
    Type text at the current cursor position.
    
    Args:
        text: Text to type
    
    Returns:
        JSON result of the type operation.
    """
    try:
        # Use pyautogui to type text
        pyautogui.typewrite(text)
        
        logger.info(f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        return json.dumps({
            "type": "type",
            "text": text,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Type operation failed: {e}")
        return json.dumps({
            "type": "error", 
            "message": f"Type failed: {str(e)}"
        })

@mcp.tool()
def windows_computer_key(key: str, modifiers: List[str] = None) -> str:
    """
    Press a key or key combination.
    
    Args:
        key: Key to press (e.g., "enter", "tab", "escape", "a", "1")
        modifiers: List of modifier keys (e.g., ["ctrl"], ["ctrl", "shift"])
    
    Returns:
        JSON result of the key operation.
    """
    try:
        if modifiers:
            # Build key combination
            key_combo = modifiers + [key]
            pyautogui.hotkey(*key_combo)
            logger.info(f"Pressed key combination: {'+'.join(key_combo)}")
        else:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
        
        return json.dumps({
            "type": "key",
            "key": key,
            "modifiers": modifiers or [],
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Key operation failed: {e}")
        return json.dumps({
            "type": "error",
            "message": f"Key press failed: {str(e)}"
        })

@mcp.tool()
def windows_powershell_execute(command: str, working_directory: str = None) -> str:
    """
    Execute a PowerShell command on Windows.
    
    Args:
        command: PowerShell command to execute
        working_directory: Optional working directory for the command
    
    Returns:
        JSON result with command output.
    """
    try:
        # Build PowerShell command
        ps_cmd = ["powershell", "-Command"]
        
        if working_directory:
            # Change directory first, then execute command
            full_command = f"cd '{working_directory}'; {command}"
        else:
            full_command = command
        
        ps_cmd.append(full_command)
        
        logger.info(f"Executing PowerShell: {command}")
        
        # Execute command
        result = subprocess.run(
            ps_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return json.dumps({
            "type": "powershell",
            "command": command,
            "working_directory": working_directory,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        })
        
    except subprocess.TimeoutExpired:
        logger.error(f"PowerShell command timeout: {command}")
        return json.dumps({
            "type": "error",
            "message": "Command timed out after 30 seconds"
        })
    except Exception as e:
        logger.error(f"PowerShell execution failed: {e}")
        return json.dumps({
            "type": "error",
            "message": f"PowerShell failed: {str(e)}"
        })

@mcp.tool()
def wsl_bridge_execute(command: str, working_directory: str = None) -> str:
    """
    Execute a command in WSL environment.
    
    Args:
        command: Linux command to execute in WSL
        working_directory: Optional working directory (Windows or WSL path)
    
    Returns:
        JSON result with command output.
    """
    try:
        result = execute_wsl_command(command, working_directory)
        
        return json.dumps({
            "type": "wsl",
            "command": command,
            "working_directory": working_directory,
            **result
        })
        
    except Exception as e:
        logger.error(f"WSL bridge execution failed: {e}")
        return json.dumps({
            "type": "error",
            "message": f"WSL execution failed: {str(e)}"
        })

@mcp.tool()
def windows_file_operations(operation: str, path: str, content: str = None) -> str:
    """
    Perform file operations on Windows filesystem.
    
    Args:
        operation: Operation to perform ("read", "write", "delete", "exists")
        path: File path (Windows format)
        content: Content for write operations
    
    Returns:
        JSON result of the file operation.
    """
    try:
        file_path = Path(path)
        
        if operation == "read":
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            content = file_path.read_text(encoding='utf-8')
            return json.dumps({
                "type": "file_read",
                "path": path,
                "content": content,
                "success": True
            })
            
        elif operation == "write":
            if content is None:
                raise ValueError("Content required for write operation")
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            
            return json.dumps({
                "type": "file_write",
                "path": path,
                "bytes_written": len(content.encode('utf-8')),
                "success": True
            })
            
        elif operation == "delete":
            if file_path.exists():
                file_path.unlink()
                deleted = True
            else:
                deleted = False
            
            return json.dumps({
                "type": "file_delete",
                "path": path,
                "deleted": deleted,
                "success": True
            })
            
        elif operation == "exists":
            exists = file_path.exists()
            return json.dumps({
                "type": "file_exists",
                "path": path,
                "exists": exists,
                "success": True
            })
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
    except Exception as e:
        logger.error(f"File operation failed: {e}")
        return json.dumps({
            "type": "error",
            "message": f"File operation failed: {str(e)}"
        })

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point for the Windows Computer Use MCP server."""
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize display information
        initialize_display_info()
        
        # Configure pyautogui settings
        pyautogui.PAUSE = 0.1  # Small pause between actions
        pyautogui.FAILSAFE = True  # Enable failsafe (move mouse to corner to abort)
        
        logger.info("Windows Computer Use MCP Server starting...")
        logger.info(f"Display: {display_info['width']}x{display_info['height']}")
        
        # Run the FastMCP server
        mcp.run()
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()