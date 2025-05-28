import base64
import io
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel # type: ignore
# PIL Image is imported but not directly used by ScreenshotTool after pyautogui.
# Pyautogui handles image object creation. It's used by AnalyzeScreenshotTool if it were to load from file.
# from PIL import Image # Commenting out as it's not directly used by ScreenshotTool logic if pyautogui is available
from app.utils.logger import setup_logger

# Import SystemModule from ClaudeDesktopBridge
# This assumes ClaudeDesktopBridge is in the PYTHONPATH or installed
try:
    from ClaudeDesktopBridge.app.modules.system import SystemModule
except ImportError:
    # Fallback for local development if paths are set up differently,
    # or provide a mock/stub if bridge is not available during agent testing.
    # For this task, we assume it will be available.
    # logger.error("Failed to import SystemModule from ClaudeDesktopBridge. Ensure it's in PYTHONPATH.")
    print("WARNING: Failed to import SystemModule from ClaudeDesktopBridge. Ensure it's in PYTHONPATH.")
    # As a stub for the tool to be structurally sound, define a dummy SystemModule
    class SystemModule:
        def execute_command(self, command: str, timeout: Optional[int] = None, shell: bool = True) -> Dict[str, Any]:
            return {"success": False, "stderr": "SystemModule (stub) not available", "stdout": "", "return_code": -1}

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
                    "maxItems": 4,
                    "default": None # Making explicit that region is optional
                }
            },
            "required": [] # region is not required if full_screen is true
        }
        self.returns_schema = {
            "type": "object",
            "properties": {
                "image_data": {"type": "string", "description": "Base64-encoded image data"},
                "width": {"type": "integer", "description": "Image width in pixels"},
                "height": {"type": "integer", "description": "Image height in pixels"},
                "timestamp": {"type": "string", "description": "ISO timestamp when the screenshot was taken"},
                "file_path": {"type": "string", "description": "Server-side path where the screenshot was saved"}
            }
        }
        
        self.pyautogui_available = True
        try:
            import pyautogui
            # Specific configurations for pyautogui can be done here if needed for this tool
            # e.g., pyautogui.FAILSAFE = False if default is too sensitive for server
            self.pyautogui_module = pyautogui # Store the module if needed elsewhere
        except (ImportError, ModuleNotFoundError, OSError) as e:
            self.pyautogui_available = False
            self.pyautogui_module = None
            # Using print as logger might not be configured at module load time or init
            print(f"WARNING: PyAutoGUI import failed for ScreenshotTool: {e}. Screenshot tool will be unavailable.")
            logger.warning(f"PyAutoGUI import failed for ScreenshotTool: {e}. Screenshot tool will be unavailable.")


        # Create screenshots directory if it doesn't exist
        # Using relative path from this file's location to a 'screenshots' dir at project root
        # Assuming tools.py is in app/mcp/, so ../../.. goes to ClaudeDesktopAgent/
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "screenshots")
        if not os.path.exists(self.screenshots_dir):
            try:
                os.makedirs(self.screenshots_dir)
                logger.info(f"Created screenshots directory at {self.screenshots_dir}")
            except Exception as e:
                logger.error(f"Failed to create screenshots directory at {self.screenshots_dir}: {e}")
                # If dir creation fails, tool might still work by returning base64 without saving.
                # However, current implementation saves then returns base64.
    
    async def execute(self, full_screen: bool = True, region: Optional[List[int]] = None) -> Dict[str, Any]:
        """Capture a screenshot of the desktop or a specific region"""
        if not self.pyautogui_available:
            logger.error("ScreenshotTool: PyAutoGUI is not available.")
            raise RuntimeError("Screenshot tool is unavailable because PyAutoGUI failed to load.")
        
        try:
            # Capture screenshot
            if full_screen:
                screenshot = self.pyautogui_module.screenshot()
            else:
                if region is None:
                    # This case should ideally be caught by schema validation if region is required when full_screen=false
                    # For robustness, handle it here too.
                    raise ValueError("Region must be specified when full_screen is False")
                if len(region) != 4:
                    raise ValueError("Region must be a list of 4 integers [left, top, width, height]")
                screenshot = self.pyautogui_module.screenshot(region=tuple(region))
            
            width, height = screenshot.size
            timestamp = datetime.now().isoformat()
            
            filepath = "unavailable" # Default if saving fails
            try:
                if os.path.exists(self.screenshots_dir) and os.path.isdir(self.screenshots_dir):
                    filename = f"screenshot_{timestamp.replace(':', '-')}.png"
                    filepath = os.path.join(self.screenshots_dir, filename)
                    screenshot.save(filepath)
                    logger.info(f"Saved screenshot to {filepath}")
                else:
                    logger.warning(f"Screenshots directory {self.screenshots_dir} does not exist or is not a directory. Screenshot will not be saved to file.")
            except Exception as e:
                logger.error(f"Failed to save screenshot to file: {e}")


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
            # Re-raise to be caught by the MCP server's error handling
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
                "confidence": {"type": "number", "description": "Confidence score of the analysis (placeholder)"}
            }
        }
        
        self.anthropic_api_key = anthropic_api_key
        self.anthropic_api_url = anthropic_api_url
        # This tool does not directly use pyautogui, so no availability check here.
    
    async def execute(self, image_data: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a screenshot using Claude Vision API"""
        import requests # Moved import here as it's only used by this tool
        
        if not self.anthropic_api_key:
            # This should ideally be checked at tool initialization and prevent tool registration
            # if critical dependencies/configs are missing.
            logger.error("ANTHROPIC_API_KEY not found for AnalyzeScreenshotTool.")
            raise ValueError("ANTHROPIC_API_KEY not configured for this tool.")
        
        try:
            if prompt is None:
                prompt = self.parameters_schema["properties"]["prompt"]["default"]
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": "claude-3-opus-20240229", # Consider making model configurable
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png", # Assuming PNG, could be made dynamic
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
            
            response = requests.post(self.anthropic_api_url, json=payload, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            result = response.json()
            
            description = result.get("content", [{}])[0].get("text", "No description found.")
            confidence = 0.95 # Placeholder
            
            return {
                "description": description,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
            raise

class ExecuteShellCommandTool(BaseTool):
    """Tool for executing shell commands"""
    def __init__(self):
        self.name = "execute_shell_command"
        self.description = "Executes a shell command and returns its output. For security, only pre-approved commands can be run."
        self.parameters_schema = {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute."},
                "timeout": {"type": "integer", "description": "Optional timeout in seconds.", "default": 60}
            },
            "required": ["command"]
        }
        self.returns_schema = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "description": "True if the command executed successfully (return code 0), False otherwise."},
                "stdout": {"type": "string", "description": "Standard output from the command."},
                "stderr": {"type": "string", "description": "Standard error from the command."},
                "return_code": {"type": "integer", "description": "The return code of the command."}
            }
        }
        # This tool relies on SystemModule, which handles its own command execution logic.
        # No direct pyautogui dependency here.
        self.system_module = SystemModule()

    async def execute(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Executes a shell command using SystemModule"""
        logger.info(f"Executing shell command via tool: {command} with timeout: {timeout}")
        try:
            result = self.system_module.execute_command(command=command, timeout=timeout)
            return result
        except Exception as e:
            logger.error(f"Error executing shell command tool: {str(e)}", exc_info=True)
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1 
            }
