from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from app.utils.config import settings
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# API key header
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    # If no API key is configured, allow all requests (for development)
    if not settings.API_KEY:
        return True
    
    # If API key is configured, validate it
    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True
