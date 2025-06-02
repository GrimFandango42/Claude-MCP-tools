import uvicorn
from app.utils.config import settings
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting Claude Desktop Agent on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
