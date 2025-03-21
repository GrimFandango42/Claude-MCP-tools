from mcp.server import Server, stdio_server
from mcp.server.tools import Tool
import logging
import os
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculator_official_sdk.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("calculator_official_sdk")

# Create the server
app = Server("Calculator MCP Server")

# Define calculator tools
@app.tool()
async def mcp2_calculator_add(a: float, b: float) -> str:
    """Add two numbers together"""
    result = a + b
    logger.info(f"Performed addition: {a} + {b} = {result}")
    return f"Performed addition: {a} + {b} = {result}"

@app.tool()
async def mcp2_calculator_subtract(a: float, b: float) -> str:
    """Subtract second number from first number"""
    result = a - b
    logger.info(f"Performed subtraction: {a} - {b} = {result}")
    return f"Performed subtraction: {a} - {b} = {result}"

@app.tool()
async def mcp2_calculator_multiply(a: float, b: float) -> str:
    """Multiply two numbers"""
    result = a * b
    logger.info(f"Performed multiplication: {a} × {b} = {result}")
    return f"Performed multiplication: {a} × {b} = {result}"

@app.tool()
async def mcp2_calculator_divide(a: float, b: float) -> str:
    """Divide first number by second number"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    result = a / b
    logger.info(f"Performed division: {a} ÷ {b} = {result}")
    return f"Performed division: {a} ÷ {b} = {result}"

# Main function to run the server
async def main():
    logger.info("Starting calculator MCP server with official SDK")
    try:
        async with stdio_server() as streams:
            await app.run(
                streams[0],  # stdin
                streams[1],  # stdout
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Error running server: {str(e)}", exc_info=True)

# Run the server
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
