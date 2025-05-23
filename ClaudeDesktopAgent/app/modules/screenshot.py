import pyautogui
import base64
import io
from PIL import Image
from datetime import datetime
import os
import requests
from typing import Dict, Any
from fastapi import BackgroundTasks
from app.utils.logger import setup_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger(__name__)

class ScreenshotModule:
    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_api_url = "https://api.anthropic.com/v1/messages"
        self.screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            logger.info(f"Created screenshots directory at {self.screenshots_dir}")
    
    def capture_screenshot(self) -> Dict[str, Any]:
        """Capture a screenshot of the desktop and return it as base64 encoded string"""
        try:
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
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
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
            raise
    
    async def analyze_screenshot(self, image_data: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Analyze a screenshot using Claude Vision API"""
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
            
            # Make API request in background to avoid blocking
            def make_api_request():
                response = requests.post(self.anthropic_api_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            
            # Execute request
            response = make_api_request()
            
            # Extract description from response
            description = response["content"][0]["text"]
            
            # For now, we'll use a placeholder confidence value
            confidence = 0.95
            
            return {
                "description": description,
                "image_data": image_data,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
            raise
