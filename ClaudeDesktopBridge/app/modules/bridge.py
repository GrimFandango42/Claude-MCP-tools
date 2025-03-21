import os
import json
import base64
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from fastapi import BackgroundTasks
from app.utils.logger import setup_logger
from app.utils.config import settings
from app.modules.computer import ComputerModule

# Setup logger
logger = setup_logger(__name__)

class BridgeModule:
    def __init__(self):
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.anthropic_api_url = settings.ANTHROPIC_API_URL
        self.computer_module = ComputerModule()
        self.tool_handlers = {
            "computer": self._handle_computer_tool,
            "browser": self._handle_browser_tool,
            "system": self._handle_system_tool
        }
        self.status = {
            "connected": False,
            "last_connection": None,
            "active_sessions": 0,
            "tool_calls": 0,
            "errors": 0
        }
    
    async def handle_tool_use(self, tool_name: str, parameters: Dict[str, Any], 
                            message_id: str, background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Handle a tool use request from Claude"""
        try:
            # Update status
            self.status["tool_calls"] += 1
            
            # Check if tool handler exists
            if tool_name not in self.tool_handlers:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Call the appropriate tool handler
            result = await self.tool_handlers[tool_name](parameters, background_tasks)
            
            return result
        except Exception as e:
            # Update error count
            self.status["errors"] += 1
            logger.error(f"Error handling tool use: {str(e)}", exc_info=True)
            raise
    
    async def _handle_computer_tool(self, parameters: Dict[str, Any], 
                                 background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Handle computer tool requests"""
        action = parameters.get("action")
        
        if action == "screenshot":
            full_screen = parameters.get("full_screen", True)
            region = parameters.get("region")
            result = self.computer_module.capture_screenshot(full_screen, region)
            return result
        
        elif action == "click":
            x = parameters.get("x")
            y = parameters.get("y")
            button = parameters.get("button", "left")
            clicks = parameters.get("clicks", 1)
            self.computer_module.click(x, y, button, clicks)
            return {"success": True, "message": f"Clicked at ({x}, {y})"}
        
        elif action == "type":
            text = parameters.get("text")
            interval = parameters.get("interval")
            self.computer_module.type_text(text, interval)
            return {"success": True, "message": f"Typed text"}
        
        elif action == "key_press":
            key = parameters.get("key")
            press_duration = parameters.get("press_duration")
            self.computer_module.key_press(key, press_duration)
            return {"success": True, "message": f"Pressed key: {key}"}
        
        elif action == "mouse_move":
            x = parameters.get("x")
            y = parameters.get("y")
            duration = parameters.get("duration")
            self.computer_module.mouse_move(x, y, duration)
            return {"success": True, "message": f"Moved mouse to ({x}, {y})"}
        
        elif action == "scroll":
            amount = parameters.get("amount")
            x = parameters.get("x")
            y = parameters.get("y")
            self.computer_module.scroll(amount, x, y)
            return {"success": True, "message": f"Scrolled {amount} clicks"}
        
        elif action == "drag":
            start_x = parameters.get("start_x")
            start_y = parameters.get("start_y")
            end_x = parameters.get("end_x")
            end_y = parameters.get("end_y")
            button = parameters.get("button", "left")
            duration = parameters.get("duration")
            self.computer_module.drag(start_x, start_y, end_x, end_y, button, duration)
            return {"success": True, "message": f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"}
        
        else:
            raise ValueError(f"Unknown computer action: {action}")
    
    async def _handle_browser_tool(self, parameters: Dict[str, Any], 
                               background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Handle browser tool requests"""
        # This is a placeholder for browser tool handling
        # Will be implemented when browser module is ready
        return {"success": False, "message": "Browser tools not yet implemented"}
    
    async def _handle_system_tool(self, parameters: Dict[str, Any], 
                              background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Handle system tool requests"""
        # This is a placeholder for system tool handling
        # Will be implemented when system module is ready
        return {"success": False, "message": "System tools not yet implemented"}
    
    async def send_message(self, messages: List[Dict[str, Any]], model: str, 
                        max_tokens: int, system: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to Claude API with tools enabled"""
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
            
            # Prepare tools
            tools = [
                {
                    "name": "computer",
                    "description": "Control the computer with keyboard and mouse actions, and capture screenshots",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["screenshot", "click", "type", "key_press", "mouse_move", "scroll", "drag"]
                            },
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "text": {"type": "string"},
                            "key": {"type": "string"}
                        },
                        "required": ["action"]
                    }
                }
            ]
            
            # Prepare payload
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
                "tools": tools
            }
            
            # Add system prompt if provided
            if system:
                payload["system"] = system
            
            # Make API request
            response = requests.post(self.anthropic_api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Update status
            self.status["connected"] = True
            self.status["last_connection"] = datetime.now().isoformat()
            self.status["active_sessions"] += 1
            
            return result
        except Exception as e:
            # Update error count
            self.status["errors"] += 1
            logger.error(f"Error sending message: {str(e)}", exc_info=True)
            raise
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process a webhook from Claude for Desktop"""
        # This is a placeholder for webhook processing
        # Will be implemented when webhook integration is ready
        logger.info(f"Processing webhook: {json.dumps(payload)[:100]}...")
        return {"success": True, "message": "Webhook processed"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the bridge"""
        return self.status
