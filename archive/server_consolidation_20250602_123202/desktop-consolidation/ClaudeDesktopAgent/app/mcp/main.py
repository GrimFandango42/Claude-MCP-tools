import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# MCP server settings
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8090"))
MCP_DEBUG = os.getenv("MCP_DEBUG", "False").lower() in ("true", "1", "t")

def main():
    """Run the MCP server"""
    logger.info(f"Starting MCP server on {MCP_HOST}:{MCP_PORT}")
    
    # Ensure screenshots directory exists
    screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        logger.info(f"Created screenshots directory at {screenshots_dir}")
    
    # Run the server
    uvicorn.run(
        "app.mcp.server:mcp_app",
        host=MCP_HOST,
        port=MCP_PORT,
        reload=MCP_DEBUG
    )

if __name__ == "__main__":
    main()
