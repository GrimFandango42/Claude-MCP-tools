from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Literal
import base64
from app.modules.browser import BrowserModule
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Initialize browser module
browser_module = BrowserModule()

# Request and response models
class NavigateRequest(BaseModel):
    url: str
    wait_until: Optional[Literal["load", "domcontentloaded", "networkidle"]] = "networkidle"
    timeout: Optional[int] = 30000  # milliseconds

class ClickRequest(BaseModel):
    selector: str
    timeout: Optional[int] = 5000  # milliseconds
    button: Optional[Literal["left", "right", "middle"]] = "left"

class TypeRequest(BaseModel):
    selector: str
    text: str
    delay: Optional[int] = 50  # milliseconds between keystrokes

class ExtractRequest(BaseModel):
    selector: Optional[str] = None
    xpath: Optional[str] = None
    attribute: Optional[str] = None
    include_html: Optional[bool] = False

class SearchRequest(BaseModel):
    query: str
    engine: Optional[Literal["google", "bing", "duckduckgo"]] = "google"

class ScreenshotRequest(BaseModel):
    selector: Optional[str] = None
    full_page: Optional[bool] = False

class ScreenshotResponse(BaseModel):
    image_data: str
    width: int
    height: int

class ExtractResponse(BaseModel):
    text: List[str]
    html: Optional[List[str]] = None
    attributes: Optional[List[Dict[str, str]]] = None

# Endpoints
@router.post("/navigate")
async def navigate(request: NavigateRequest):
    """Navigate to a URL"""
    try:
        logger.info(f"Navigating to: {request.url}")
        result = await browser_module.navigate(
            url=request.url,
            wait_until=request.wait_until,
            timeout=request.timeout
        )
        return {"success": True, "message": f"Navigated to {request.url}", "title": result["title"]}
    except Exception as e:
        logger.error(f"Error navigating to {request.url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to navigate: {str(e)}")

@router.post("/click")
async def click(request: ClickRequest):
    """Click on an element"""
    try:
        logger.info(f"Clicking on selector: {request.selector}")
        await browser_module.click(
            selector=request.selector,
            timeout=request.timeout,
            button=request.button
        )
        return {"success": True, "message": f"Clicked on {request.selector}"}
    except Exception as e:
        logger.error(f"Error clicking on {request.selector}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to click: {str(e)}")

@router.post("/type")
async def type_text(request: TypeRequest):
    """Type text into an element"""
    try:
        logger.info(f"Typing into selector: {request.selector}")
        await browser_module.type(
            selector=request.selector,
            text=request.text,
            delay=request.delay
        )
        return {"success": True, "message": f"Typed text into {request.selector}"}
    except Exception as e:
        logger.error(f"Error typing into {request.selector}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to type: {str(e)}")

@router.post("/extract", response_model=ExtractResponse)
async def extract(request: ExtractRequest):
    """Extract content from the page"""
    try:
        logger.info(f"Extracting content from page")
        result = await browser_module.extract(
            selector=request.selector,
            xpath=request.xpath,
            attribute=request.attribute,
            include_html=request.include_html
        )
        return result
    except Exception as e:
        logger.error(f"Error extracting content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to extract content: {str(e)}")

@router.post("/search")
async def search(request: SearchRequest):
    """Perform a web search"""
    try:
        logger.info(f"Searching for: {request.query} using {request.engine}")
        results = await browser_module.search(
            query=request.query,
            engine=request.engine
        )
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Error searching for {request.query}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search: {str(e)}")

@router.post("/screenshot", response_model=ScreenshotResponse)
async def screenshot(request: ScreenshotRequest):
    """Take a screenshot of the page or an element"""
    try:
        logger.info(f"Taking screenshot")
        result = await browser_module.screenshot(
            selector=request.selector,
            full_page=request.full_page
        )
        return result
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to take screenshot: {str(e)}")
