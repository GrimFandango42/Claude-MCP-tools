import os
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import api_router
from app.utils.logger import setup_logger
from app.utils.config import settings

# Setup logger
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Claude Desktop Bridge",
    description="Bridge between Claude for Desktop and computer control capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Create required directories
os.makedirs(settings.SCREENSHOTS_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Claude Desktop Bridge API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
