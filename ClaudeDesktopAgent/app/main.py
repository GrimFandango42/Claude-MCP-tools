import uvicorn
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.api.router import api_router
from app.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI app
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

# Include API router
app.include_router(api_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Claude Desktop Agent on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
