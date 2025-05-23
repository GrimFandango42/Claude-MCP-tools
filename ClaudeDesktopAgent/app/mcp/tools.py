import base64
import io
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel
import pyautogui
from PIL import Image
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

class BaseTool:
    """Base class for all MCP tools"""
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    returns_schema: Dict[str, Any]
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool schema for MCP"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "returns": self.returns_schema
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with the given parameters"""
        raise NotImplementedError("Subclasses must implement execute()")

class ScreenshotTool(BaseTool):
    """Tool for capturing screenshots"""
    def __init__(self):
        self.name = "screenshot"
        self.description = "Capture a screenshot of the desktop or a specific region"
        self.parameters_schema = {
            "type": "object",
            "properties": {
                "full_screen": {
                    "type": "boolean",
                    "description": "Whether to capture the full screen or a region",
                    "default": True
                },
                "region": {
                    "type": "array",
                    "description": "Region to capture [left, top, width, height]",
                    "items": {"type": "integer"},
                    "minItems": 4,
                    "maxItems": 4
                }
            },
            "required": []
        }
        self.returns_schema = {
            "type": "object",
            "properties": {
                "image_data": {"type": "string", "description": "Base64-encoded image data"},
                "width": {"type": "integer", "description": "Image width in pixels"},
                "height": {"type": "integer", "description": "Image height in pixels"},
                "timestamp": {"type": "string", "description": "ISO timestamp when the screenshot was taken"}
            }
        }
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            logger.info(f"Created screenshots directory at {self.screenshots_dir}")
    
    async def execute(self, full_screen: bool = True, region: Optional[List[int]] = None) -> Dict[str, Any]:
        """Capture a screenshot of the desktop or a specific region"""
        try:
            # Capture screenshot
            if full_screen:
                screenshot = pyautogui.screenshot()
            else:
                if region is None:
                    raise ValueError("Region must be specified when full_screen is False")
                if len(region) != 4:
                    raise ValueError("Region must be a list of 4 integers [left, top, width, height]")
                screenshot = pyautogui.screenshot(region=tuple(region))
            
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
                "file_path": filepath
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
            raise

class AnalyzeScreenshotTool(BaseTool):
    """Tool for analyzing screenshots using Claude Vision"""
    def __init__(self, anthropic_api_key: str, anthropic_api_url: str):
        self.name = "analyze_screenshot"
        self.description = "Analyze a screenshot using Claude Vision API"
        self.parameters_schema = {
            "type": "object",
            "properties": {
                "image_data": {
                    "type": "string",
                    "description": "Base64-encoded image data"
                },
                "prompt": {
                    "type": "string",
                    "description": "Custom prompt for analysis",
                    "default": "Describe what you see in this screenshot of my desktop. Focus on the visible applications, windows, content, and any notable UI elements."
                }
            },
            "required": ["image_data"]
        }
        self.returns_schema = {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Description of the screenshot content"},
                "confidence": {"type": "number", "description": "Confidence score of the analysis"}
            }
        }
        
        self.anthropic_api_key = anthropic_api_key
        self.anthropic_api_url = anthropic_api_url
    
    async def execute(self, image_data: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a screenshot using Claude Vision API"""
        import requests
        
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        try:
            # Use default prompt if none provided
            if prompt is None:
                prompt = "Describe what you see in this screenshot of my desktop. Focus on the visible applications, windows, content, and any notable UI elements."
            
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
                                "text": prompt
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
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
            raise
