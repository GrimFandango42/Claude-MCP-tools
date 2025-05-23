from fastapi import APIRouter
from app.api.routes import screenshot, tools, mcp

# Create main API router
api_router = APIRouter(prefix="/api")

# Include module-specific routers
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(screenshot.router, prefix="/screenshot", tags=["screenshot"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# Add more module routers as they are developed
# api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
# api_router.include_router(apps.router, prefix="/apps", tags=["apps"])
