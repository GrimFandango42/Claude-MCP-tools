import os
from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    # API settings
    APP_NAME: str = "Claude Desktop Agent"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Anthropic API settings
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_API_URL: str = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # Security settings
    API_KEY: Optional[str] = os.getenv("API_KEY")
    API_KEY_NAME: str = "x-api-key"
    
    # Storage settings
    SCREENSHOTS_DIR: str = os.path.join(os.getcwd(), "screenshots")
    LOGS_DIR: str = os.path.join(os.getcwd(), "logs")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        settings.SCREENSHOTS_DIR,
        settings.LOGS_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Call this function when importing this module
ensure_directories()
