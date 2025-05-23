from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.utils.config import settings
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# API key header
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key"""
    if settings.API_KEY and settings.API_KEY != "":
        if api_key is None or api_key != settings.API_KEY:
            logger.warning(f"Invalid API key: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    return api_key
