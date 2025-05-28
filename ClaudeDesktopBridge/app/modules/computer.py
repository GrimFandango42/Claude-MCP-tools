import base64
import io
from PIL import Image
from datetime import datetime
import os
import requests
import time
from typing import Dict, Any, Optional, Tuple, Literal
from fastapi import BackgroundTasks
from app.utils.logger import setup_logger
from app.utils.config import settings

# Setup logger
logger = setup_logger(__name__)

# PyAutoGUI availability flag and import
PYAUTOGUI_AVAILABLE = True
try:
    import pyautogui
    # Configure PyAutoGUI defaults if successfully imported
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1 
except (ImportError, ModuleNotFoundError, OSError) as e:
    PYAUTOGUI_AVAILABLE = False
    # Assuming logger might not be fully set up if this is a top-level import issue during startup
    print(f"WARNING: PyAutoGUI import failed: {e}. GUI automation will be unavailable.")

class ComputerModule:
    def __init__(self):
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.anthropic_api_url = settings.ANTHROPIC_API_URL
        self.screenshots_dir = settings.SCREENSHOTS_DIR
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            logger.info(f"Created screenshots directory at {self.screenshots_dir}")
    
    def capture_screenshot(self, full_screen: bool = True, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Capture a screenshot of the desktop or a specific region"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Capture screenshot
            if full_screen:
                screenshot = pyautogui.screenshot()
            else:
                if region is None:
                    raise ValueError("Region must be specified when full_screen is False")
                screenshot = pyautogui.screenshot(region=region)
            
            # Get image dimensions
            width, height = screenshot.size
            
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # Save screenshot to file
            filename = f"screenshot_{timestamp.replace(':', '-')}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            screenshot.save(filepath)
            logger.info(f"Saved screenshot to {filepath}")
            
            # Convert to base64
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image_data": img_str,
                "width": width,
                "height": height,
                "timestamp": timestamp,
                "file_path": filepath # Added file_path to return as it's useful
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
            raise
    
    async def analyze_screenshot(self, image_data: str, background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Analyze a screenshot using Claude Vision API"""
        # This method does not directly use pyautogui, so no PYAUTOGUI_AVAILABLE check needed here.
        if not self.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        try:
            # Prepare headers
            headers = {
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            # Prepare payload
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
            
            # Make API request
            response = requests.post(self.anthropic_api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Extract description from response
            description = result["content"][0]["text"]
            
            # For now, we'll use a placeholder confidence value
            confidence = 0.95
            
            return {
                "description": description,
                "image_data": image_data, # Returning input image_data for context if needed
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
            raise
    
    def click(self, x: int, y: int, button: Literal["left", "right", "middle"] = "left", clicks: int = 1) -> None:
        """Perform a mouse click at the specified coordinates"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Move mouse to position
            pyautogui.moveTo(x, y)
            
            # Perform click
            if button == "left":
                pyautogui.click(clicks=clicks)
            elif button == "right":
                pyautogui.rightClick()
            elif button == "middle":
                pyautogui.middleClick()
            
            logger.info(f"Clicked at ({x}, {y}) with {button} button, {clicks} clicks")
        except Exception as e:
            logger.error(f"Error clicking at ({x}, {y}): {str(e)}", exc_info=True)
            raise
    
    def type_text(self, text: str, interval: Optional[float] = 0.0) -> None: # Default interval to 0.0 as per pyautogui docs
        """Type text at the current cursor position"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Type text
            pyautogui.typewrite(text, interval=interval) # interval was Optional[float] = None, pyautogui default is 0.0
            
            logger.info(f"Typed text: {text[:20]}..." if len(text) > 20 else f"Typed text: {text}")
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}", exc_info=True)
            raise
    
    def key_press(self, key: str, press_duration: Optional[float] = None) -> None:
        """Press a specific key"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Press key
            if press_duration is not None and press_duration > 0: # Ensure duration is positive if provided
                pyautogui.keyDown(key)
                time.sleep(press_duration)
                pyautogui.keyUp(key)
            else:
                pyautogui.press(key)
            
            logger.info(f"Pressed key: {key}")
        except Exception as e:
            logger.error(f"Error pressing key: {str(e)}", exc_info=True)
            raise
    
    def mouse_move(self, x: int, y: int, duration: Optional[float] = 0.0) -> None: # Default duration to 0.0 as per pyautogui docs
        """Move the mouse to the specified coordinates"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Move mouse
            pyautogui.moveTo(x, y, duration=duration) # duration was Optional[float] = None, pyautogui default is 0.0
            
            logger.info(f"Moved mouse to ({x}, {y})")
        except Exception as e:
            logger.error(f"Error moving mouse to ({x}, {y}): {str(e)}", exc_info=True)
            raise
    
    def scroll(self, amount: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll the mouse wheel"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Move mouse to position if specified
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
            
            # Scroll
            pyautogui.scroll(amount)
            
            logger.info(f"Scrolled {amount} clicks")
        except Exception as e:
            logger.error(f"Error scrolling: {str(e)}", exc_info=True)
            raise
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             button: Literal["left", "right", "middle"] = "left", 
             duration: Optional[float] = 0.0) -> None: # Default duration to 0.0 as per pyautogui docs
        """Perform a drag operation from one point to another"""
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is not available due to import errors.")
        try:
            # Move to start position
            pyautogui.moveTo(start_x, start_y)
            
            # Perform drag
            # pyautogui.dragTo uses button parameter directly
            pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
            
            logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) using {button} button")
        except Exception as e:
            logger.error(f"Error dragging: {str(e)}", exc_info=True)
            raise
