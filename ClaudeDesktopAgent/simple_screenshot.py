import json
import logging
import os
import sys
import base64
import io
from datetime import datetime
from typing import Dict, Any, List, Optional

import pyautogui
from PIL import Image

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("screenshot_server.log")
    ]
)
logger = logging.getLogger("simple_screenshot")

# Create screenshots directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
    logger.info(f"Created screenshots directory at {screenshots_dir}")

# Capture screenshot
def capture_screenshot(full_screen=True, region=None):
    try:
        # Capture screenshot
        if full_screen:
            screenshot = pyautogui.screenshot()
        else:
            if region is None:
                region = [0, 0, 800, 600]  # Default region
            screenshot = pyautogui.screenshot(region=tuple(region))
        
        # Get image dimensions
        width, height = screenshot.size
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Save screenshot to file
        filename = f"screenshot_{timestamp.replace(':', '-').replace('.', '-')}.png"
        filepath = os.path.join(screenshots_dir, filename)
        screenshot.save(filepath)
        logger.info(f"Saved screenshot to {filepath}")
        
        return {
            "file_path": filepath,
            "width": width,
            "height": height,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
        return {"error": str(e)}

# Main function
def main():
    logger.info("Starting simple screenshot tool")
    
    # Print ready message for Claude Desktop
    print("MCP SERVER READY", file=sys.stderr)
    sys.stderr.flush()
    
    # Process arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--capture":
            result = capture_screenshot()
            print(json.dumps({
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "image",
                            "url": f"file://{result['file_path']}",
                            "mime_type": "image/png"
                        },
                        {
                            "type": "text",
                            "text": f"Screenshot captured at {result['timestamp']}. Dimensions: {result['width']}x{result['height']}"
                        }
                    ]
                }
            }))
    else:
        # Just indicate we're ready
        logger.info("Screenshot tool ready")

if __name__ == "__main__":
    main()
