import base64
import io
import os
import sys # Added for sys.exit override AND sys.path printing
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel # type: ignore
from app.utils.logger import setup_logger

# Setup logger for this module
logger = setup_logger(__name__)

# --- Robust PyAutoGUI Import for tools.py ---
_original_sys_exit_tools_module = sys.exit
TOOLS_PYAUTOGUI_MODULE = None
TOOLS_PYAUTOGUI_AVAILABLE = False

try:
    def _graceful_exit_tools_py_import(code=0):
        print(f"INFO: pyautogui attempted to sys.exit({code}) during import in tools.py. Intercepting.")
        logger.warning(f"pyautogui attempted to sys.exit({code}) during import in tools.py. Intercepting.")
        raise InterruptedError(f"pyautogui attempted to sys.exit({code}) in tools.py")

    sys.exit = _graceful_exit_tools_py_import
    
    import pyautogui
    
    TOOLS_PYAUTOGUI_MODULE = pyautogui
    TOOLS_PYAUTOGUI_AVAILABLE = True
    print("INFO: PyAutoGUI imported successfully in tools.py and is available.")
    logger.info("PyAutoGUI imported successfully in tools.py and is available.")

except (ImportError, ModuleNotFoundError, OSError, InterruptedError) as e:
    print(f"WARNING: PyAutoGUI import failed or was interrupted in tools.py: {e}. ScreenshotTool will be affected.")
    logger.warning(f"PyAutoGUI import failed or was interrupted in tools.py: {e}. ScreenshotTool will be affected.")
    TOOLS_PYAUTOGUI_AVAILABLE = False
finally:
    sys.exit = _original_sys_exit_tools_module
# --- End Robust PyAutoGUI Import ---

# Print sys.path for diagnostics before attempting to import SystemModule
print(f"DEBUG: sys.path in ClaudeDesktopAgent/app/mcp/tools.py: {sys.path}")
logger.info(f"DEBUG: sys.path in ClaudeDesktopAgent/app/mcp/tools.py: {sys.path}")

try:
    from ClaudeDesktopBridge.app.modules.system import SystemModule
    logger.info("Successfully imported SystemModule from ClaudeDesktopBridge.")
except ImportError as e:
    logger.warning(f"Failed to import SystemModule from ClaudeDesktopBridge (Error: {e}). Ensure it's in PYTHONPATH. Using stub for ExecuteShellCommandTool.")
    print(f"WARNING: Failed to import SystemModule from ClaudeDesktopBridge (Error: {e}). Using stub.")
    class SystemModule: # Stub
        def execute_command(self, command: str, timeout: Optional[int] = None, shell: bool = True) -> Dict[str, Any]:
            logger.warning(f"ExecuteShellCommandTool: Called stub SystemModule.execute_command for: {command}")
            return {"success": False, "stderr": "SystemModule (stub) not available due to import error", "stdout": "", "return_code": -1}
        # Add other methods of SystemModule as stubs if ExecuteShellCommandTool might call them.
        # For now, only execute_command is directly called by the tool.


class BaseTool:
    """Base class for all MCP tools"""
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    returns_schema: Dict[str, Any]
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "returns": self.returns_schema
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement execute()")

class ScreenshotTool(BaseTool):
    """Tool for capturing screenshots"""
    def __init__(self):
        self.name = "screenshot"
        self.description = "Capture a screenshot of the desktop or a specific region. Availability depends on GUI environment."
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
                    "default": None
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
                "timestamp": {"type": "string", "description": "ISO timestamp when the screenshot was taken"},
                "file_path": {"type": "string", "description": "Server-side path where the screenshot was saved (or 'unavailable')"},
                "status": {"type": "string", "description": "Status of the screenshot operation ('success' or 'unavailable: reason')"}
            }
        }
        
        self.pyautogui_module = TOOLS_PYAUTOGUI_MODULE
        self.pyautogui_available = TOOLS_PYAUTOGUI_AVAILABLE

        if not self.pyautogui_available:
            logger.warning("ScreenshotTool initialized, but PyAutoGUI is not available. Screenshots will fail.")
        else:
            logger.info("ScreenshotTool initialized, PyAutoGUI is available.")

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.screenshots_dir = os.path.join(project_root, "screenshots")
        if not os.path.exists(self.screenshots_dir):
            try:
                os.makedirs(self.screenshots_dir)
                logger.info(f"Created screenshots directory at {self.screenshots_dir}")
            except Exception as e:
                logger.error(f"Failed to create screenshots directory {self.screenshots_dir}: {e}")
    
    async def execute(self, full_screen: bool = True, region: Optional[List[int]] = None) -> Dict[str, Any]:
        if not self.pyautogui_available:
            logger.error("ScreenshotTool.execute called but PyAutoGUI is not available.")
            return {
                "image_data": "", "width": 0, "height": 0, 
                "timestamp": datetime.now().isoformat(), "file_path": "unavailable",
                "status": "unavailable: PyAutoGUI failed to load or is not functional."
            }
        
        try:
            if full_screen:
                screenshot = self.pyautogui_module.screenshot()
            else:
                if region is None:
                    raise ValueError("Region must be specified when full_screen is False")
                if len(region) != 4:
                    raise ValueError("Region must be a list of 4 integers [left, top, width, height]")
                screenshot = self.pyautogui_module.screenshot(region=tuple(region))
            
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
                "image_data": img_str, "width": width, "height": height,
                "timestamp": timestamp, "file_path": filepath,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
            return { 
                "image_data": "", "width": 0, "height": 0,
                "timestamp": datetime.now().isoformat(), "file_path": "error",
                "status": f"error: {str(e)}"
            }

class AnalyzeScreenshotTool(BaseTool):
    """Tool for analyzing screenshots using Claude Vision"""
    def __init__(self, anthropic_api_key: str, anthropic_api_url: str):
        self.name = "analyze_screenshot"
        self.description = "Analyze a screenshot using Claude Vision API"
        self.parameters_schema = {
            "type": "object",
            "properties": {
                "image_data": {"type": "string", "description": "Base64-encoded image data"},
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
    
    async def execute(self, image_data: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        import requests
        if not self.anthropic_api_key:
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
                "model": "claude-3-opus-20240229",
                "max_tokens": 1024,
                "messages": [{"role": "user","content": [{"type": "image","source": {"type": "base64","media_type": "image/png","data": image_data}},{"type": "text","text": prompt}]}]
            }
            response = requests.post(self.anthropic_api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            description = result.get("content", [{}])[0].get("text", "No description found.")
            return {"description": description, "confidence": 0.95} 
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
        self.system_module = SystemModule() # This will use the stub if import failed

    async def execute(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        logger.info(f"ExecuteShellCommandTool: Calling SystemModule.execute_command for: {command}")
        try:
            result = self.system_module.execute_command(command=command, timeout=timeout)
            return result
        except Exception as e:
            logger.error(f"Error executing shell command tool: {str(e)}", exc_info=True)
            return {"success": False, "stdout": "", "stderr": str(e), "return_code": -1}
