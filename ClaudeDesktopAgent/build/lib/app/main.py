import uvicorn
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.api.router import api_router
from app.utils.logger import setup_logger

# Import the mcp_app from app.mcp.server to mount it
from app.mcp.server import mcp_app as mcp_websocket_app # Renaming to avoid confusion with main app

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI app (main application)
app = FastAPI(
    title="Claude Desktop Agent",
    description="A framework for extending Claude's capabilities on desktop",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router (for HTTP endpoints)
app.include_router(api_router)

# Mount the MCP WebSocket application
# All routes from mcp_websocket_app (including its @mcp_app.websocket("/"))
# will be available under the main app. If mounted at root, paths don't change.
# If mounted with a prefix, e.g., app.mount("/mcp_ws", mcp_websocket_app),
# then client URI would be ws://localhost:8000/mcp_ws/
# The original mcp_app had its WebSocket at "/", so mounting mcp_websocket_app at "/"
# effectively merges its routes into the main app at the root.
app.mount("/", mcp_websocket_app) # This should make @mcp_app.websocket("/") available at ws://localhost:8000/


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

# Health check endpoint (already on main app)
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Main entry point for running this app directly (e.g. for dev)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Claude Desktop Agent on port {port}")
    # Uvicorn should run this app instance (app.main:app)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
