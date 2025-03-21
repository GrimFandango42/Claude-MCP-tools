import asyncio
import json
import logging
import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "simple_memory_server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("simple_memory_server")

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup - use absolute path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple_memories.db")
logger.info(f"Using database at absolute path: {DB_PATH}")

def init_db():
    """Initialize the SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create memories table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB_PATH}")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        return False

# Memory operations
async def create_memory(title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
    """Create a new memory with optional tags"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Convert tags list to JSON string
        tags_json = json.dumps(tags) if tags else None
        
        # Insert memory
        cursor.execute(
            "INSERT INTO memories (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags_json)
        )
        memory_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created memory: {title} with ID {memory_id}")
        return {
            "success": True,
            "memory_id": memory_id,
            "title": title,
            "tags": tags or []
        }
    except Exception as e:
        logger.error(f"Error creating memory: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

async def get_memory(memory_id: int) -> Dict[str, Any]:
    """Retrieve a memory by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
        cursor = conn.cursor()
        
        # Get memory
        cursor.execute("""
        SELECT id, title, content, tags, created_at
        FROM memories
        WHERE id = ?
        """, (memory_id,))
        
        memory = cursor.fetchone()
        
        if not memory:
            conn.close()
            return {
                "success": False,
                "error": f"Memory with ID {memory_id} not found"
            }
        
        # Parse tags from JSON
        tags = json.loads(memory["tags"]) if memory["tags"] else []
        
        conn.close()
        
        return {
            "success": True,
            "memory": {
                "id": memory["id"],
                "title": memory["title"],
                "content": memory["content"],
                "created_at": memory["created_at"],
                "tags": tags
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving memory: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

async def search_memories(query: str = None, tags: List[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Search memories by text query and/or tags"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql_query = "SELECT id, title, content, tags, created_at FROM memories"
        params = []
        where_clauses = []
        
        # Add text search if query provided
        if query:
            where_clauses.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        # Add WHERE clause if we have conditions
        if where_clauses:
            sql_query += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add limit
        sql_query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        
        # Format results
        memories = []
        for row in results:
            # Parse tags
            memory_tags = json.loads(row["tags"]) if row["tags"] else []
            
            # Filter by tags if provided
            if tags and not any(tag in memory_tags for tag in tags):
                continue
            
            memories.append({
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "created_at": row["created_at"],
                "tags": memory_tags
            })
        
        conn.close()
        
        return {
            "success": True,
            "memories": memories,
            "count": len(memories)
        }
    except Exception as e:
        logger.error(f"Error searching memories: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

# JSON-RPC over HTTP endpoint for MCP
@app.post("/")
async def jsonrpc_endpoint(request: Request):
    try:
        # Get the request body
        data = await request.json()
        logger.info(f"Received JSON-RPC request: {json.dumps(data, indent=2)}")
        
        # Extract message details
        method = data.get("method")
        message_id = data.get("id")
        
        # Handle initialize method
        if method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "serverInfo": {
                        "name": "Simple Memory MCP Server",
                        "version": "1.0.0"
                    }
                }
            })
        
        # Handle tools/list method
        elif method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "tools": [
                        {
                            "name": "memory_create",
                            "description": "Create a new memory with optional tags",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "Title of the memory"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Content of the memory"
                                    },
                                    "tags": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "Tags to associate with the memory"
                                    }
                                },
                                "required": ["title", "content"]
                            }
                        },
                        {
                            "name": "memory_get",
                            "description": "Retrieve a memory by ID",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "memory_id": {
                                        "type": "integer",
                                        "description": "ID of the memory to retrieve"
                                    }
                                },
                                "required": ["memory_id"]
                            }
                        },
                        {
                            "name": "memory_search",
                            "description": "Search memories by text query and/or tags",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Text to search for in memory titles and content"
                                    },
                                    "tags": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "Tags to filter memories by"
                                    },
                                    "limit": {
                                        "type": "integer",
                                        "description": "Maximum number of results to return"
                                    }
                                }
                            }
                        }
                    ]
                }
            })
        
        # Handle tools/call method
        elif method == "tools/call":
            params = data.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"Tool call: {tool_name} with arguments: {arguments}")
            
            result = None
            error = None
            
            try:
                if tool_name == "memory_create":
                    title = arguments.get("title")
                    content = arguments.get("content")
                    tags = arguments.get("tags", [])
                    result = await create_memory(title, content, tags)
                
                elif tool_name == "memory_get":
                    memory_id = arguments.get("memory_id")
                    result = await get_memory(memory_id)
                
                elif tool_name == "memory_search":
                    query = arguments.get("query")
                    tags = arguments.get("tags")
                    limit = arguments.get("limit", 10)
                    result = await search_memories(query, tags, limit)
                
                else:
                    error = f"Unknown tool: {tool_name}"
                    logger.warning(error)
            except Exception as e:
                error = str(e)
                logger.error(f"Error executing {tool_name}: {error}", exc_info=True)
            
            if error:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32000,
                        "message": error
                    }
                })
            else:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                })
        
        # Handle unknown methods
        else:
            logger.warning(f"Unknown method: {method}")
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received: {str(e)}", exc_info=True)
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": "Internal error"
            }
        })

# WebSocket endpoint for MCP (alternative transport)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        while True:
            # Receive message from client
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                logger.info(f"Received WebSocket message: {json.dumps(message, indent=2)}")
                
                # Extract message details
                method = message.get("method")
                message_id = message.get("id")
                
                # Handle initialize method
                if method == "initialize":
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": {
                            "protocolVersion": "0.1.0",
                            "capabilities": {},
                            "serverInfo": {
                                "name": "Simple Memory MCP Server",
                                "version": "1.0.0"
                            }
                        }
                    }))
                    logger.info("Sent initialize response via WebSocket")
                
                # Handle tools/list method
                elif method == "tools/list":
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "memory_create",
                                    "description": "Create a new memory with optional tags",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "Title of the memory"
                                            },
                                            "content": {
                                                "type": "string",
                                                "description": "Content of the memory"
                                            },
                                            "tags": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                },
                                                "description": "Tags to associate with the memory"
                                            }
                                        },
                                        "required": ["title", "content"]
                                    }
                                },
                                {
                                    "name": "memory_get",
                                    "description": "Retrieve a memory by ID",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "memory_id": {
                                                "type": "integer",
                                                "description": "ID of the memory to retrieve"
                                            }
                                        },
                                        "required": ["memory_id"]
                                    }
                                },
                                {
                                    "name": "memory_search",
                                    "description": "Search memories by text query and/or tags",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {
                                                "type": "string",
                                                "description": "Text to search for in memory titles and content"
                                            },
                                            "tags": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                },
                                                "description": "Tags to filter memories by"
                                            },
                                            "limit": {
                                                "type": "integer",
                                                "description": "Maximum number of results to return"
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }))
                    logger.info("Sent tools/list response via WebSocket")
                
                # Handle tools/call method
                elif method == "tools/call":
                    params = message.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    logger.info(f"WebSocket tool call: {tool_name} with arguments: {arguments}")
                    
                    result = None
                    error = None
                    
                    try:
                        if tool_name == "memory_create":
                            title = arguments.get("title")
                            content = arguments.get("content")
                            tags = arguments.get("tags", [])
                            result = await create_memory(title, content, tags)
                        
                        elif tool_name == "memory_get":
                            memory_id = arguments.get("memory_id")
                            result = await get_memory(memory_id)
                        
                        elif tool_name == "memory_search":
                            query = arguments.get("query")
                            tags = arguments.get("tags")
                            limit = arguments.get("limit", 10)
                            result = await search_memories(query, tags, limit)
                        
                        else:
                            error = f"Unknown tool: {tool_name}"
                            logger.warning(error)
                    except Exception as e:
                        error = str(e)
                        logger.error(f"Error executing {tool_name} via WebSocket: {error}", exc_info=True)
                    
                    if error:
                        await websocket.send_text(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "error": {
                                "code": -32000,
                                "message": error
                            }
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result)
                                    }
                                ]
                            }
                        }))
                        logger.info(f"Sent {tool_name} response via WebSocket")
                
                # Handle unknown methods
                else:
                    logger.warning(f"Unknown WebSocket method: {method}")
                    await websocket.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received via WebSocket: {str(e)}", exc_info=True)
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }))
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}", exc_info=True)
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)

# HTTP endpoint for health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": os.path.exists(DB_PATH)}

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    if not init_db():
        logger.critical("Failed to initialize database. Exiting.")
        sys.exit(1)

# Run the server
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5006  # Changed port to avoid conflicts
    logger.info(f"Starting Simple Memory MCP server on {host}:{port}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Environment variables: {json.dumps({k: v for k, v in os.environ.items() if not k.startswith('_')}, indent=2)}")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
