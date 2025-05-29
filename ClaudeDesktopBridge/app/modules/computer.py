import base64
import io
# from PIL import Image # PIL.Image is not directly used by this module's pyautogui functions
from datetime import datetime
import os
import requests
import sys # Added for sys.exit override
import time
from typing import Dict, Any, Optional, Tuple, Literal
from fastapi import BackgroundTasks
from app.utils.logger import setup_logger
from app.utils.config import settings

# Setup logger
logger = setup_logger(__name__)

# --- Robust PyAutoGUI Import ---
_original_sys_exit_computer_module = sys.exit
PYAUTOGUI_MODULE = None
PYAUTOGUI_AVAILABLE = False

try:
    def _graceful_exit_computer_module(code=0):
        logger.warning(f"pyautogui attempted to sys.exit({code}) during import in computer.py. Intercepting.")
        # print(f"INFO: pyautogui attempted to sys.exit({code}) during import in computer.py. Intercepting.")
        raise InterruptedError(f"pyautogui attempted to sys.exit({code}) in computer.py")

    sys.exit = _graceful_exit_computer_module
    
    import pyautogui
    
    PYAUTOGUI_MODULE = pyautogui
    PYAUTOGUI_AVAILABLE = True
    logger.info("PyAutoGUI imported successfully in computer.py and is available.")
    # print("INFO: PyAutoGUI imported successfully in computer.py and is available.")
    
    # Configure PyAutoGUI defaults if successfully imported and available
    PYAUTOGUI_MODULE.FAILSAFE = True
    PYAUTOGUI_MODULE.PAUSE = 0.1

except (ImportError, ModuleNotFoundError, OSError, InterruptedError) as e:
    logger.warning(f"PyAutoGUI import failed or was interrupted in computer.py: {e}. GUI automation will be unavailable.")
    # print(f"WARNING: PyAutoGUI import failed or was interrupted in computer.py: {e}. GUI automation will be unavailable.")
    PYAUTOGUI_AVAILABLE = False
finally:
    sys.exit = _original_sys_exit_computer_module # Always restore original sys.exit
# --- End Robust PyAutoGUI Import ---


class ComputerModule:
    def __init__(self):
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.anthropic_api_url = settings.ANTHROPIC_API_URL
        self.screenshots_dir = settings.SCREENSHOTS_DIR
        
        if not os.path.exists(self.screenshots_dir):
            try:
                os.makedirs(self.screenshots_dir)
                logger.info(f"Created screenshots directory at {self.screenshots_dir}")
            except Exception as e:
                 logger.error(f"Failed to create screenshots directory {self.screenshots_dir}: {e}")
    
    def capture_screenshot(self, full_screen: bool = True, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Capture a screenshot of the desktop or a specific region"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("capture_screenshot called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            if full_screen:
                screenshot = PYAUTOGUI_MODULE.screenshot()
            else:
                if region is None:
                    raise ValueError("Region must be specified when full_screen is False")
                screenshot = PYAUTOGUI_MODULE.screenshot(region=region)
            
            width, height = screenshot.size
            timestamp = datetime.now().isoformat()
            
            filepath = "unavailable"
            if os.path.exists(self.screenshots_dir) and os.path.isdir(self.screenshots_dir):
                filename = f"screenshot_{timestamp.replace(':', '-')}.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                try:
                    screenshot.save(filepath)
                    logger.info(f"Saved screenshot to {filepath}")
                except Exception as e:
                    logger.error(f"Failed to save screenshot to {filepath}: {e}")
                    filepath = f"failed_to_save: {e}"
            else:
                logger.warning(f"Screenshots directory {self.screenshots_dir} not found or not a directory. Screenshot not saved.")

            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image_data": img_str,
                "width": width,
                "height": height,
                "timestamp": timestamp,
                "file_path": filepath
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
            raise
    
    async def analyze_screenshot(self, image_data: str, background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Analyze a screenshot using Claude Vision API"""
        if not self.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        try:
            headers = {
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-opus-20240229",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": "Describe what you see in this screenshot of my desktop. Focus on the visible applications, windows, content, and any notable UI elements."
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(self.anthropic_api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            description = result.get("content", [{}])[0].get("text", "No description found.")
            confidence = 0.95
            
            return {
                "description": description,
                "image_data": image_data,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
            raise
    
    def click(self, x: int, y: int, button: Literal["left", "right", "middle"] = "left", clicks: int = 1) -> None:
        """Perform a mouse click at the specified coordinates"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("click called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            PYAUTOGUI_MODULE.moveTo(x, y)
            if button == "left":
                PYAUTOGUI_MODULE.click(clicks=clicks)
            elif button == "right":
                PYAUTOGUI_MODULE.rightClick()
            elif button == "middle":
                PYAUTOGUI_MODULE.middleClick()
            logger.info(f"Clicked at ({x}, {y}) with {button} button, {clicks} clicks")
        except Exception as e:
            logger.error(f"Error clicking at ({x}, {y}): {str(e)}", exc_info=True)
            raise
    
    def type_text(self, text: str, interval: Optional[float] = 0.0) -> None:
        """Type text at the current cursor position"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("type_text called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            PYAUTOGUI_MODULE.typewrite(text, interval=interval)
            logger.info(f"Typed text: {text[:20]}..." if len(text) > 20 else f"Typed text: {text}")
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}", exc_info=True)
            raise
    
    def key_press(self, key: str, press_duration: Optional[float] = None) -> None:
        """Press a specific key"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("key_press called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            if press_duration is not None and press_duration > 0:
                PYAUTOGUI_MODULE.keyDown(key)
                time.sleep(press_duration)
                PYAUTOGUI_MODULE.keyUp(key)
            else:
                PYAUTOGUI_MODULE.press(key)
            logger.info(f"Pressed key: {key}")
        except Exception as e:
            logger.error(f"Error pressing key: {str(e)}", exc_info=True)
            raise
    
    def mouse_move(self, x: int, y: int, duration: Optional[float] = 0.0) -> None:
        """Move the mouse to the specified coordinates"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("mouse_move called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            PYAUTOGUI_MODULE.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
        except Exception as e:
            logger.error(f"Error moving mouse to ({x}, {y}): {str(e)}", exc_info=True)
            raise
    
    def scroll(self, amount: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll the mouse wheel"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("scroll called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            if x is not None and y is not None:
                PYAUTOGUI_MODULE.moveTo(x, y)
            PYAUTOGUI_MODULE.scroll(amount)
            logger.info(f"Scrolled {amount} clicks")
        except Exception as e:
            logger.error(f"Error scrolling: {str(e)}", exc_info=True)
            raise
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             button: Literal["left", "right", "middle"] = "left", 
             duration: Optional[float] = 0.0) -> None:
        """Perform a drag operation from one point to another"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("drag called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            PYAUTOGUI_MODULE.moveTo(start_x, start_y)
            PYAUTOGUI_MODULE.dragTo(end_x, end_y, duration=duration, button=button)
            logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) using {button} button")
        except Exception as e:
            logger.error(f"Error dragging: {str(e)}", exc_info=True)
            raise
