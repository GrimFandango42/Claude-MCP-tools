from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import json
import base64
from app.modules.bridge import BridgeModule
from app.utils.security import get_api_key
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter(dependencies=[Depends(get_api_key)])

# Initialize bridge module
bridge_module = BridgeModule()

# Models
class ToolUseRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    message_id: str

class ToolResultResponse(BaseModel):
    success: bool
    message_id: str
    tool_name: str
    result: Dict[str, Any]
    error: Optional[str] = None

class MessageRequest(BaseModel):
    messages: List[Dict[str, Any]]
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    system: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    content: List[Dict[str, Any]]
    model: str
    role: str
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Dict[str, int]

# Endpoints
@router.post("/tool_use", response_model=ToolResultResponse)
async def handle_tool_use(request: ToolUseRequest, background_tasks: BackgroundTasks = None):
    """Handle a tool use request from Claude"""
    try:
        logger.info(f"Handling tool use request: {request.tool_name}")
        result = await bridge_module.handle_tool_use(
            tool_name=request.tool_name,
            parameters=request.parameters,
            message_id=request.message_id,
            background_tasks=background_tasks
        )
        return ToolResultResponse(
            success=True,
            message_id=request.message_id,
            tool_name=request.tool_name,
            result=result
        )
    except Exception as e:
        logger.error(f"Error handling tool use: {str(e)}", exc_info=True)
        return ToolResultResponse(
            success=False,
            message_id=request.message_id,
            tool_name=request.tool_name,
            result={},
            error=str(e)
        )

@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send a message to Claude API with tools enabled"""
    try:
        logger.info(f"Sending message to Claude API")
        response = await bridge_module.send_message(
            messages=request.messages,
            model=request.model,
            max_tokens=request.max_tokens,
            system=request.system
        )
        return response
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.post("/webhook")
async def claude_webhook(request: Request):
    """Webhook endpoint for Claude for Desktop to send events"""
    try:
        payload = await request.json()
        logger.info(f"Received webhook from Claude for Desktop")
        
        # Process the webhook payload
        result = await bridge_module.process_webhook(payload)
        
        return JSONResponse(content={"success": True, "message": "Webhook processed successfully"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Failed to process webhook: {str(e)}"}
        )

@router.get("/status")
async def bridge_status():
    """Get the status of the bridge"""
    try:
        status = bridge_module.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting bridge status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get bridge status: {str(e)}")
