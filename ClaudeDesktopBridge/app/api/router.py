from fastapi import APIRouter, Depends
from app.utils.security import get_api_key
from app.api.routes import computer, browser, system, tools, bridge

# Create main API router
api_router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])

# Include all route handlers
api_router.include_router(computer.router, prefix="/computer", tags=["computer"])
api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(bridge.router, prefix="/bridge", tags=["bridge"])
