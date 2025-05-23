import os
from pydantic import BaseSettings
from typing import List, Dict, Any, Optional

class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True
    
    # Security Settings
    API_KEY: str = os.getenv("API_KEY", "")
    API_KEY_NAME: str = "X-API-Key"
    
    # Anthropic API Settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_API_URL: str = "https://api.anthropic.com/v1/messages"
    
    # File Storage Settings
    SCREENSHOTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'screenshots')
    
    # Security Allowlists
    ALLOWED_COMMANDS: List[str] = [
        "dir", "ls", "echo", "type", "cat", "find", "grep", "ping", 
        "ipconfig", "ifconfig", "systeminfo", "tasklist", "ps", "whoami",
        "python", "pip", "npm", "node", "powershell"
    ]
    
    ALLOWED_APPS: List[str] = [
        "notepad", "calc", "chrome", "firefox", "edge", "explorer",
        "code", "cmd", "powershell", "terminal", "python"
    ]
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()
