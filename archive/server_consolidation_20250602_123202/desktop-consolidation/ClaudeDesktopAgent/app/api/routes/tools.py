from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Models
class ToolDescription(BaseModel):
    name: str
    description: str
    version: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]

class ToolRegistrationRequest(BaseModel):
    name: str
    description: str
    version: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    endpoint: str

class ToolRegistrationResponse(BaseModel):
    success: bool
    message: str
    tool_id: Optional[str] = None

# In-memory tool registry (would be replaced with a database in production)
tool_registry = {
    "screenshot": {
        "name": "screenshot",
        "description": "Capture and analyze desktop screenshots",
        "version": "0.1.0",
        "parameters": {},
        "returns": {"image_data": "string", "description": "string"},
        "endpoint": "/api/screenshot"
    }
}

@router.get("/list", response_model=Dict[str, ToolDescription])
async def list_tools():
    """List all available tools"""
    return tool_registry

@router.get("/{tool_id}", response_model=ToolDescription)
async def get_tool(tool_id: str):
    """Get details for a specific tool"""
    if tool_id not in tool_registry:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    return tool_registry[tool_id]

@router.post("/register", response_model=ToolRegistrationResponse)
async def register_tool(tool: ToolRegistrationRequest):
    """Register a new tool"""
    tool_id = tool.name.lower()
    
    if tool_id in tool_registry:
        return ToolRegistrationResponse(
            success=False,
            message=f"Tool '{tool_id}' already exists",
            tool_id=tool_id
        )
    
    # Add to registry
    tool_registry[tool_id] = tool.dict()
    logger.info(f"Registered new tool: {tool_id}")
    
    return ToolRegistrationResponse(
        success=True,
        message=f"Tool '{tool_id}' registered successfully",
        tool_id=tool_id
    )

@router.delete("/{tool_id}", response_model=ToolRegistrationResponse)
async def unregister_tool(tool_id: str):
    """Unregister a tool"""
    if tool_id not in tool_registry:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    
    # Remove from registry
    del tool_registry[tool_id]
    logger.info(f"Unregistered tool: {tool_id}")
    
    return ToolRegistrationResponse(
        success=True,
        message=f"Tool '{tool_id}' unregistered successfully",
        tool_id=tool_id
    )
