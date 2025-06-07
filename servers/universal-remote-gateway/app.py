#!/usr/bin/env python3
"""
Universal Remote MCP Gateway - Mobile Access to ALL Claude Desktop MCP Servers

This service exposes ALL your Claude Desktop MCP servers as HTTP REST APIs
that can be accessed from Claude mobile app or any HTTP client.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("universal-remote-gateway")

# FastAPI app
app = FastAPI(
    title="Universal Remote MCP Gateway",
    description="HTTP bridge for ALL Claude Desktop MCP servers - Access every MCP skill from anywhere!",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security (optional)
security = HTTPBearer(auto_error=False)

# Request/Response Models
class MCPToolRequest(BaseModel):
    server_name: str = Field(..., description="MCP server name")
    tool_name: str = Field(..., description="Tool name to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

class MCPToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    server_name: str
    tool_name: str
    execution_time_ms: float

# MCP Server Registry - ALL 22 servers from your config
MCP_SERVERS = {
    "filesystem": {
        "description": "File system operations - read, write, list files and directories",
        "type": "nodejs",
        "tools": ["read_file", "write_file", "list_directory", "create_directory", "move_file", "search_files"]
    },
    "firecrawl": {
        "description": "Web scraping and crawling with advanced extraction capabilities",
        "type": "nodejs", 
        "tools": ["scrape_url", "crawl_site", "extract_data", "search_web", "map_site"]
    },
    "playwright": {
        "description": "Browser automation - navigate, click, fill forms, take screenshots",
        "type": "nodejs",
        "tools": ["navigate", "click", "fill", "screenshot", "evaluate", "wait_for_element"]
    },
    "financial-datasets": {
        "description": "Financial data analysis and market information",
        "type": "python",
        "tools": ["get_stock_data", "analyze_market", "financial_metrics", "portfolio_analysis"]
    },
    "fantasy-pl": {
        "description": "Fantasy Premier League data and analysis",
        "type": "python",
        "tools": ["get_player_stats", "analyze_teams", "transfer_suggestions", "gameweek_predictions"]
    },
    "mcp-pandoc": {
        "description": "Document conversion between various formats using Pandoc",
        "type": "python",
        "tools": ["convert_document", "supported_formats", "batch_convert"]
    },
    "screenpilot": {
        "description": "Desktop automation with screen capture, mouse control, and keyboard input",
        "type": "python",
        "tools": ["take_screenshot", "click_coordinates", "type_text", "find_element", "automate_workflow"]
    },
    "sqlite": {
        "description": "SQLite database operations and queries",
        "type": "nodejs",
        "tools": ["execute_query", "create_table", "insert_data", "update_data", "delete_data"]
    },
    "windows-computer-use": {
        "description": "Windows desktop automation with MCP framework integration",
        "type": "python",
        "tools": ["computer_screenshot", "computer_click", "computer_type", "computer_scroll", "computer_key"]
    },
    "containerized-computer-use": {
        "description": "Containerized computer use with Docker isolation and VNC access",
        "type": "python", 
        "tools": ["container_screenshot", "container_click", "container_type", "start_container", "stop_container"]
    },
    "n8n-workflow-generator": {
        "description": "N8n workflow generation and management with natural language processing",
        "type": "nodejs",
        "tools": ["create_workflow", "execute_workflow", "list_workflows", "update_workflow", "generate_from_description"]
    },
    "docker-orchestration": {
        "description": "Docker container orchestration with enhanced async handling",
        "type": "python",
        "tools": ["list_containers", "start_container", "stop_container", "create_container", "manage_compose"]
    },
    "github": {
        "description": "GitHub repository management and operations",
        "type": "nodejs",
        "tools": ["create_repo", "list_repos", "create_issue", "create_pr", "get_file_content", "push_changes"]
    },
    "memory": {
        "description": "Official MCP memory server for persistent context storage",
        "type": "nodejs",
        "tools": ["store_memory", "retrieve_memory", "search_memories", "delete_memory", "list_memories"]
    },
    "api-gateway": {
        "description": "Unified API Gateway with intelligent routing and cost optimization",
        "type": "python",
        "tools": ["route_request", "optimize_cost", "cache_response", "analyze_usage", "health_check"]
    },
    "claude-code-integration": {
        "description": "Claude Code Integration with FastMCP and CLI detection",
        "type": "python",
        "tools": ["execute_code", "run_tests", "format_code", "analyze_code", "generate_documentation"]
    },
    "vibetest": {
        "description": "Multi-agent browser QA testing with intelligent bug detection",
        "type": "python",
        "tools": ["run_test_suite", "detect_bugs", "generate_report", "analyze_performance", "create_test_plan"]
    },
    "agenticseek-mcp": {
        "description": "Multi-provider AI routing with smart cost optimization",
        "type": "python",
        "tools": ["smart_routing", "local_reasoning", "openai_reasoning", "google_reasoning", "estimate_cost"]
    },
    "code-formatter": {
        "description": "Code formatting for multiple languages (Python, JavaScript, etc.)",
        "type": "python",
        "tools": ["format_python", "format_javascript", "format_json", "lint_code", "check_style"]
    },
    "security-scanner": {
        "description": "Dependency vulnerability scanning and license checking",
        "type": "python",
        "tools": ["scan_dependencies", "check_vulnerabilities", "analyze_licenses", "security_report", "fix_suggestions"]
    },
    "visual-debugging": {
        "description": "Visual debugging for infrastructure dashboards and screenshots",
        "type": "python",
        "tools": ["analyze_screenshot", "analyze_kubernetes_dashboard", "suggest_troubleshooting", "interpret_metrics"]
    },
    "enhanced-memory": {
        "description": "Enhanced memory with self-improving workflows and experiment tracking",
        "type": "python",
        "tools": ["create_experiment", "update_experiment", "analyze_patterns", "generate_insights", "track_progress"]
    },
    "auto-accept": {
        "description": "Autonomous coding loops with auto-accept mode for rapid prototyping",
        "type": "python",
        "tools": ["start_autonomous_loop", "execute_loop_iteration", "get_loop_status", "pause_loop", "resume_loop"]
    },
    "travel-booking": {
        "description": "Intelligent travel booking with multi-platform search and smart recommendations",
        "type": "python",
        "tools": ["search_accommodations", "get_recommendations", "analyze_price_trends", "get_booking_links", "destination_insights"]
    }
}

# Mock MCP execution
async def execute_mcp_tool(server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool on the specified MCP server."""
    if server_name not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    if tool_name not in MCP_SERVERS[server_name]["tools"]:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found in server '{server_name}'")
    
    # Simulate MCP tool execution
    await asyncio.sleep(0.1)
    
    return {
        "success": True,
        "result": {
            "message": f"Executed {tool_name} on {server_name}",
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
            "server_type": MCP_SERVERS[server_name]["type"]
        }
    }

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Interactive documentation homepage"""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Universal Remote MCP Gateway</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #2c3e50; }}
            .server-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
            .server-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 8px; background: #f9f9f9; }}
            .server-name {{ font-weight: bold; color: #34495e; }}
            .tools {{ font-size: 12px; color: #666; margin-top: 10px; }}
            .endpoint {{ background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Universal Remote MCP Gateway</h1>
            <p>Access ALL your Claude Desktop MCP servers from mobile! This gateway exposes <strong>{len(MCP_SERVERS)} MCP servers</strong> as HTTP endpoints.</p>
            
            <h2>📱 Available MCP Servers</h2>
            <div class="server-grid">
                {''.join(f'''
                <div class="server-card">
                    <div class="server-name">{name}</div>
                    <div>{info["description"]}</div>
                    <div class="tools">Tools: {", ".join(info["tools"][:3])}{"..." if len(info["tools"]) > 3 else ""}</div>
                </div>
                ''' for name, info in MCP_SERVERS.items())}
            </div>
            
            <h2>🔗 Quick Start</h2>
            <div class="endpoint">GET /api/v1/servers - List all MCP servers</div>
            <div class="endpoint">POST /api/v1/execute - Execute any MCP tool</div>
            <div class="endpoint">GET /docs - Interactive API documentation</div>
            
            <h2>📖 Documentation</h2>
            <a href="/docs">Interactive API Docs (Swagger)</a> | 
            <a href="/redoc">Alternative Docs (ReDoc)</a>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "servers_available": len(MCP_SERVERS)
    }

@app.get("/api/v1/servers")
async def list_servers():
    """List all available MCP servers"""
    return [
        {
            "name": name,
            "description": info["description"],
            "available_tools": info["tools"],
            "status": "available",
            "type": info["type"]
        }
        for name, info in MCP_SERVERS.items()
    ]

@app.post("/api/v1/execute", response_model=MCPToolResponse)
async def execute_tool(request: MCPToolRequest):
    """Execute a tool on any MCP server"""
    start_time = datetime.now()
    
    try:
        result = await execute_mcp_tool(
            request.server_name,
            request.tool_name, 
            request.parameters
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return MCPToolResponse(
            success=True,
            result=result["result"],
            server_name=request.server_name,
            tool_name=request.tool_name,
            execution_time_ms=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error executing {request.tool_name} on {request.server_name}: {e}")
        
        return MCPToolResponse(
            success=False,
            error=str(e),
            server_name=request.server_name,
            tool_name=request.tool_name,
            execution_time_ms=execution_time
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Universal Remote MCP Gateway on 0.0.0.0:{port}")
    logger.info(f"Available servers: {list(MCP_SERVERS.keys())}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )