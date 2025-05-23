#!/usr/bin/env python3
"""
Financial Datasets MCP Server - Robust Implementation
Follows the critical MCP server development rules:
1. Stdout sanctity - ONLY JSON-RPC messages on stdout
2. Proper error handling
3. Signal handling for graceful shutdown
4. Structured JSON logging to stderr
"""

import json
import os
import sys
import signal
import logging
import traceback
import httpx
from pythonjsonlogger import jsonlogger

# Configure structured JSON logging to stderr only
logger = logging.getLogger("financial-datasets-mcp")
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stderr)
format_str = "%(asctime)s %(name)s %(levelname)s %(message)s"
logHandler.setFormatter(jsonlogger.JsonFormatter(format_str))
logger.addHandler(logHandler)

# Prevent any inherited handlers from causing stdout pollution
logger.propagate = False

# Silence other loggers that might write to stdout
logging.getLogger().setLevel(logging.WARNING)
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
        logging.getLogger().removeHandler(handler)

try:
    # Import FastMCP with the correct pattern for current version
    from mcp.server.fastmcp import FastMCP
    logger.info("Imported FastMCP from mcp.server.fastmcp")
except ImportError:
    logger.error("Failed to import FastMCP. Please install with: uv sync")
    sys.exit(1)

# Constants
FINANCIAL_DATASETS_API_BASE = "https://api.financialdatasets.ai"
API_KEY = os.environ.get("FINANCIAL_DATASETS_API_KEY", "")

if not API_KEY:
    logger.warning("No FINANCIAL_DATASETS_API_KEY found in environment variables")

# Initialize FastMCP server
mcp = FastMCP("financial-datasets")
logger.info("Using FastMCP for MCP implementation")

# Helper function to make API requests with enhanced error handling
def make_request(url: str, endpoint_type: str):
    """
    Make a request to the Financial Datasets API with proper error handling.
    
    Args:
        url: The full URL to make the request to
        endpoint_type: The type of endpoint being called (for better error messages)
    """
    if not API_KEY:
        logger.error(f"API key not set - cannot make request to {endpoint_type}")
        return {
            "error": "API key not configured. Set FINANCIAL_DATASETS_API_KEY in environment variables.",
            "endpoint": endpoint_type,
            "status": "error"
        }
    
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Making request to {endpoint_type} endpoint: {url}")
        response = httpx.get(url, headers=headers, timeout=10.0)
        
        if response.status_code == 200:
            logger.info(f"Request to {endpoint_type} successful")
            return response.json()
        elif response.status_code == 401 or response.status_code == 403:
            logger.error(f"Authentication error ({response.status_code}) for {endpoint_type}")
            return {
                "error": "Authentication failed. Please check your API key.",
                "status_code": response.status_code,
                "endpoint": endpoint_type
            }
        elif response.status_code == 404:
            logger.error(f"Resource not found (404) for {endpoint_type}: {url}")
            return {
                "error": f"Resource not found. The {endpoint_type} endpoint may be incorrect.",
                "status_code": response.status_code,
                "endpoint": endpoint_type
            }
        else:
            logger.error(f"Request failed with status {response.status_code} for {endpoint_type}")
            return {
                "error": f"Request failed with status code: {response.status_code}",
                "status_code": response.status_code,
                "endpoint": endpoint_type
            }
    except httpx.RequestError as e:
        logger.error(f"Request error to {endpoint_type}: {str(e)}")
        return {
            "error": f"Request failed: {str(e)}",
            "endpoint": endpoint_type,
            "status": "error"
        }
    except Exception as e:
        logger.error(f"Unexpected error during {endpoint_type} request: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Unexpected error: {str(e)}",
            "endpoint": endpoint_type,
            "status": "error"
        }


# ==================== COMPANY DATA ENDPOINTS ====================

@mcp.tool()
def get_company_facts(ticker: str):
    """
    Get company general information like name, industry, sector, market cap, etc.
    Cost: $0.00 per request (Free)
    
    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
    """
    url = f"{FINANCIAL_DATASETS_API_BASE}/company/facts?ticker={ticker}"
    return make_request(url, "company_facts")


@mcp.tool()
def get_stock_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "day",
    interval_multiplier: int = 1,
    limit: int = 100
):
    """
    Get historical stock price data.
    Cost: $0.01 per request
    
    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (day, week, month, year)
        interval_multiplier: Multiplier of the interval (default: 1)
        limit: Maximum number of data points to return (default: 100, max: 5000)
    """
    url = (
        f"{FINANCIAL_DATASETS_API_BASE}/stock/prices"
        f"?ticker={ticker}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        f"&interval={interval}"
        f"&interval_multiplier={interval_multiplier}"
        f"&limit={limit}"
    )
    return make_request(url, "stock_prices")


@mcp.tool()
def get_income_statements(
    ticker: str,
    period: str = "annual",
    limit: int = 4
):
    """
    Get income statements for a company.
    Cost: $0.02 per request
    
    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        period: Period of statements (annual, quarterly, ttm)
        limit: Number of statements to return (default: 4)
    """
    url = (
        f"{FINANCIAL_DATASETS_API_BASE}/company/financials/income-statements"
        f"?ticker={ticker}"
        f"&period={period}"
        f"&limit={limit}"
    )
    return make_request(url, "income_statements")


# Signal handling for graceful shutdown
def handle_exit(signum, frame):
    """Handle termination signals for graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    # Don't exit - let MCP handle shutdown properly


# Main entry point with robust error handling
if __name__ == "__main__":
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        
        # Log startup information
        logger.info("Financial Datasets MCP Server starting up")
        logger.info(f"API base URL: {FINANCIAL_DATASETS_API_BASE}")
        logger.info(f"API key configured: {bool(API_KEY)}")
        
        # Run the MCP server
        mcp.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        # Don't use sys.exit() - emit error and let process terminate normally
        print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None}))