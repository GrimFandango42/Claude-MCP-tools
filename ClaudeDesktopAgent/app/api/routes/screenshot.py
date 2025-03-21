from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import base64
from app.modules.screenshot import ScreenshotModule
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Initialize screenshot module
screenshot_module = ScreenshotModule()

# Response models
class ScreenshotResponse(BaseModel):
    image_data: str
    width: int
    height: int
    timestamp: str

class AnalysisResponse(BaseModel):
    description: str
    image_data: str
    confidence: float

# Endpoints
@router.post("/capture", response_model=ScreenshotResponse)
async def capture_screenshot():
    """Capture a screenshot of the desktop"""
    try:
        logger.info("Capturing screenshot")
        result = screenshot_module.capture_screenshot()
        return result
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {str(e)}")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_screenshot(background_tasks: BackgroundTasks):
    """Capture and analyze a screenshot using Claude Vision API"""
    try:
        logger.info("Capturing and analyzing screenshot")
        # Capture screenshot first
        screenshot_data = screenshot_module.capture_screenshot()
        
        # Then analyze it
        analysis_result = await screenshot_module.analyze_screenshot(
            screenshot_data["image_data"],
            background_tasks
        )
        
        return analysis_result
    except Exception as e:
        logger.error(f"Error analyzing screenshot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze screenshot: {str(e)}")
