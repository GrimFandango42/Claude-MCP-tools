from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Tuple, Literal
import base64
from app.modules.computer import ComputerModule
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Initialize computer module
computer_module = ComputerModule()

# Request and response models
class ScreenshotRequest(BaseModel):
    full_screen: bool = True
    region: Optional[Tuple[int, int, int, int]] = None  # (left, top, width, height)

class ScreenshotResponse(BaseModel):
    image_data: str
    width: int
    height: int
    timestamp: str

class ClickRequest(BaseModel):
    x: int
    y: int
    button: Literal["left", "right", "middle"] = "left"
    clicks: int = 1

class TypeRequest(BaseModel):
    text: str
    interval: Optional[float] = None  # Time between keystrokes

class KeyPressRequest(BaseModel):
    key: str
    press_duration: Optional[float] = None  # Time to hold the key

class MouseMoveRequest(BaseModel):
    x: int
    y: int
    duration: Optional[float] = None  # Time to complete movement

class ScrollRequest(BaseModel):
    amount: int  # Positive for scroll down, negative for scroll up
    x: Optional[int] = None  # X coordinate to scroll at
    y: Optional[int] = None  # Y coordinate to scroll at

class DragRequest(BaseModel):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    button: Literal["left", "right", "middle"] = "left"
    duration: Optional[float] = None  # Time to complete drag

class AnalysisResponse(BaseModel):
    description: str
    image_data: str
    confidence: float = Field(default=0.95)

# Endpoints
@router.post("/screenshot", response_model=ScreenshotResponse)
async def capture_screenshot(request: ScreenshotRequest = ScreenshotRequest()):
    """Capture a screenshot of the desktop or a specific region"""
    try:
        logger.info(f"Capturing screenshot: {request}")
        result = computer_module.capture_screenshot(
            full_screen=request.full_screen,
            region=request.region
        )
        return result
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {str(e)}")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_screenshot(request: ScreenshotRequest = ScreenshotRequest(), background_tasks: BackgroundTasks = None):
    """Capture and analyze a screenshot using Claude Vision API"""
    try:
        logger.info(f"Capturing and analyzing screenshot: {request}")
        # Capture screenshot first
        screenshot_data = computer_module.capture_screenshot(
            full_screen=request.full_screen,
            region=request.region
        )
        
        # Then analyze it
        analysis_result = await computer_module.analyze_screenshot(
            screenshot_data["image_data"],
            background_tasks
        )
        
        return analysis_result
    except Exception as e:
        logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze screenshot: {str(e)}")

@router.post("/click")
async def click(request: ClickRequest):
    """Perform a mouse click at the specified coordinates"""
    try:
        logger.info(f"Clicking at ({request.x}, {request.y}) with {request.button} button, {request.clicks} clicks")
        computer_module.click(request.x, request.y, request.button, request.clicks)
        return {"success": True, "message": f"Clicked at ({request.x}, {request.y})"}
    except Exception as e:
        logger.error(f"Error clicking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to click: {str(e)}")

@router.post("/type")
async def type_text(request: TypeRequest):
    """Type text at the current cursor position"""
    try:
        logger.info(f"Typing text: {request.text[:20]}..." if len(request.text) > 20 else f"Typing text: {request.text}")
        computer_module.type_text(request.text, request.interval)
        return {"success": True, "message": f"Typed text: {request.text[:20]}..." if len(request.text) > 20 else f"Typed text: {request.text}"}
    except Exception as e:
        logger.error(f"Error typing text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to type text: {str(e)}")

@router.post("/key_press")
async def key_press(request: KeyPressRequest):
    """Press a specific key"""
    try:
        logger.info(f"Pressing key: {request.key}")
        computer_module.key_press(request.key, request.press_duration)
        return {"success": True, "message": f"Pressed key: {request.key}"}
    except Exception as e:
        logger.error(f"Error pressing key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to press key: {str(e)}")

@router.post("/mouse_move")
async def mouse_move(request: MouseMoveRequest):
    """Move the mouse to the specified coordinates"""
    try:
        logger.info(f"Moving mouse to ({request.x}, {request.y})")
        computer_module.mouse_move(request.x, request.y, request.duration)
        return {"success": True, "message": f"Moved mouse to ({request.x}, {request.y})"}
    except Exception as e:
        logger.error(f"Error moving mouse: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to move mouse: {str(e)}")

@router.post("/scroll")
async def scroll(request: ScrollRequest):
    """Scroll the mouse wheel"""
    try:
        logger.info(f"Scrolling {request.amount} clicks")
        computer_module.scroll(request.amount, request.x, request.y)
        return {"success": True, "message": f"Scrolled {request.amount} clicks"}
    except Exception as e:
        logger.error(f"Error scrolling: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scroll: {str(e)}")

@router.post("/drag")
async def drag(request: DragRequest):
    """Perform a drag operation from one point to another"""
    try:
        logger.info(f"Dragging from ({request.start_x}, {request.start_y}) to ({request.end_x}, {request.end_y})")
        computer_module.drag(request.start_x, request.start_y, request.end_x, request.end_y, request.button, request.duration)
        return {"success": True, "message": f"Dragged from ({request.start_x}, {request.start_y}) to ({request.end_x}, {request.end_y})"}
    except Exception as e:
        logger.error(f"Error dragging: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to drag: {str(e)}")
