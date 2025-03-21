from fastapi import APIRouter, Request, Response, HTTPException, Depends
from typing import Dict, Any, List, Optional
import json
import logging

# Import MCP server
from app.mcp.server import handle_mcp_request, get_tools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_route")

# Create router
router = APIRouter()

@router.post("/")
async def mcp_endpoint(request: Request) -> Response:
    """Forward requests to the MCP server"""
    try:
        # Forward the request to the MCP handler
        return await handle_mcp_request(request)
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """List all available MCP tools"""
    try:
        # Get tools from the MCP server
        return await get_tools()
    except Exception as e:
        logger.error(f"Error listing MCP tools: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
