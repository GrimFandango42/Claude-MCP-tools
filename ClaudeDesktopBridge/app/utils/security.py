from fastapi import Depends, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from app.utils.config import settings
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# API key header
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    if not settings.API_KEY:  # Covers None or empty string
        if settings.DEBUG:
            logger.warning("API key is not configured. Allowing request in DEBUG mode.")
            return True  # Or a dummy key value if needed by other parts, but True is simpler.
        else:
            logger.error("API key is not configured. Denying request in non-DEBUG mode.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is required for this application."
            )
    else:
        # API key is configured, validate it
        if api_key is None or api_key != settings.API_KEY:
            logger.warning(f"Invalid API key received: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        return True # Or return api_key if the validated key is used elsewhere
