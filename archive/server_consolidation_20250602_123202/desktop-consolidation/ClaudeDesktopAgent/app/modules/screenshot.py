import base64
import io
# from PIL import Image # Not directly used if pyautogui handles image objects
from datetime import datetime
import os
import sys # Added for sys.exit override
import requests # Used by analyze_screenshot
from typing import Dict, Any
from fastapi import BackgroundTasks # Used by analyze_screenshot
from app.utils.logger import setup_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logger for this module
logger = setup_logger(__name__)

# --- Robust PyAutoGUI Import for screenshot.py ---
_original_sys_exit_screenshot_module = sys.exit
SCREENSHOT_PYAUTOGUI_MODULE = None
SCREENSHOT_PYAUTOGUI_AVAILABLE = False

try:
    def _graceful_exit_screenshot_py_import(code=0):
        # Using print for critical import phase, logger might not be fully ready
        print(f"INFO: pyautogui attempted to sys.exit({code}) during import in screenshot.py. Intercepting.")
        logger.warning(f"pyautogui attempted to sys.exit({code}) during import in screenshot.py. Intercepting.")
        raise InterruptedError(f"pyautogui attempted to sys.exit({code}) in screenshot.py")

    sys.exit = _graceful_exit_screenshot_py_import
    
    import pyautogui # pyautogui and its mouseinfo submodule will use the replaced sys.exit
    
    SCREENSHOT_PYAUTOGUI_MODULE = pyautogui
    SCREENSHOT_PYAUTOGUI_AVAILABLE = True
    print("INFO: PyAutoGUI imported successfully in screenshot.py and is available.")
    logger.info("PyAutoGUI imported successfully in screenshot.py and is available.")

except (ImportError, ModuleNotFoundError, OSError, InterruptedError) as e:
    print(f"WARNING: PyAutoGUI import failed or was interrupted in screenshot.py: {e}. Screenshot features will be unavailable.")
    logger.warning(f"PyAutoGUI import failed or was interrupted in screenshot.py: {e}. Screenshot features will be unavailable.")
    SCREENSHOT_PYAUTOGUI_AVAILABLE = False
finally:
    sys.exit = _original_sys_exit_screenshot_module # Always restore original sys.exit
# --- End Robust PyAutoGUI Import ---


class ScreenshotModule:
    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_api_url = "https://api.anthropic.com/v1/messages"
        
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.screenshots_dir = os.path.join(project_root, "screenshots")
        
        if not os.path.exists(self.screenshots_dir):
            try:
                os.makedirs(self.screenshots_dir)
                logger.info(f"Created screenshots directory at {self.screenshots_dir}")
            except Exception as e:
                logger.error(f"Failed to create screenshots directory at {self.screenshots_dir}: {e}")
        
        if not SCREENSHOT_PYAUTOGUI_AVAILABLE:
            logger.warning("ScreenshotModule initialized, but PyAutoGUI (and thus screenshot capability) is unavailable.")
        else:
            logger.info("ScreenshotModule initialized, PyAutoGUI is available.")

    def capture_screenshot(self) -> Dict[str, Any]:
        """Capture a screenshot of the desktop and return it as base64 encoded string"""
        if not SCREENSHOT_PYAUTOGUI_AVAILABLE:
            logger.error("capture_screenshot called but PyAutoGUI is not available.")
            raise RuntimeError("PyAutoGUI is not available, cannot capture screenshot.")
        
        try:
            screenshot = SCREENSHOT_PYAUTOGUI_MODULE.screenshot()
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
                logger.warning(f"Screenshots directory {self.screenshots_dir} not found. Screenshot not saved to disk.")

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
    
    async def analyze_screenshot(self, image_data: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
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
            confidence = 0.95 # Placeholder
            
            return {
                "description": description,
                "image_data": image_data,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
            raise
