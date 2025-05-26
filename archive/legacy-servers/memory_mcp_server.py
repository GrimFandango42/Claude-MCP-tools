import asyncio
import json
import logging
import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("memory_mcp_server.log")
    ]
)
logger = logging.getLogger("memory_mcp_server")

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

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude_memories.db")

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create memories table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create tags table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    
    # Create memory_tags junction table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory_tags (
        memory_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (memory_id, tag_id),
        FOREIGN KEY (memory_id) REFERENCES memories (id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

# Memory operations
async def create_memory(title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
    """Create a new memory with optional tags"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert memory
        cursor.execute(
            "INSERT INTO memories (title, content) VALUES (?, ?)",
            (title, content)
        )
        memory_id = cursor.lastrowid
        
        # Process tags if provided
        if tags and len(tags) > 0:
            for tag in tags:
                # Insert tag if it doesn't exist
                cursor.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag,)
                )
                
                # Get tag ID
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                tag_id = cursor.fetchone()[0]
                
                # Link memory to tag
                cursor.execute(
                    "INSERT INTO memory_tags (memory_id, tag_id) VALUES (?, ?)",
                    (memory_id, tag_id)
                )
        
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
        SELECT m.id, m.title, m.content, m.created_at, m.updated_at
        FROM memories m
        WHERE m.id = ?
        """, (memory_id,))
        
        memory = cursor.fetchone()
        
        if not memory:
            conn.close()
            return {
                "success": False,
                "error": f"Memory with ID {memory_id} not found"
            }
        
        # Get tags for this memory
        cursor.execute("""
        SELECT t.name
        FROM tags t
        JOIN memory_tags mt ON t.id = mt.tag_id
        WHERE mt.memory_id = ?
        """, (memory_id,))
        
        tags = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "memory": {
                "id": memory["id"],
                "title": memory["title"],
                "content": memory["content"],
                "created_at": memory["created_at"],
                "updated_at": memory["updated_at"],
                "tags": tags
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving memory: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

async def update_memory(memory_id: int, title: str = None, content: str = None, tags: List[str] = None) -> Dict[str, Any]:
    """Update an existing memory"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if memory exists
        cursor.execute("SELECT id FROM memories WHERE id = ?", (memory_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "error": f"Memory with ID {memory_id} not found"
            }
        
        # Update fields if provided
        update_parts = []
        params = []
        
        if title is not None:
            update_parts.append("title = ?")
            params.append(title)
        
        if content is not None:
            update_parts.append("content = ?")
            params.append(content)
        
        if update_parts:
            update_parts.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE memories SET {', '.join(update_parts)} WHERE id = ?"
            params.append(memory_id)
            cursor.execute(query, params)
        
        # Update tags if provided
        if tags is not None:
            # Remove existing tags
            cursor.execute("DELETE FROM memory_tags WHERE memory_id = ?", (memory_id,))
            
            # Add new tags
            for tag in tags:
                # Insert tag if it doesn't exist
                cursor.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag,)
                )
                
                # Get tag ID
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                tag_id = cursor.fetchone()[0]
                
                # Link memory to tag
                cursor.execute(
                    "INSERT INTO memory_tags (memory_id, tag_id) VALUES (?, ?)",
                    (memory_id, tag_id)
                )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated memory with ID {memory_id}")
        return {
            "success": True,
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error updating memory: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

async def delete_memory(memory_id: int) -> Dict[str, Any]:
    """Delete a memory by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if memory exists
        cursor.execute("SELECT id FROM memories WHERE id = ?", (memory_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "error": f"Memory with ID {memory_id} not found"
            }
        
        # Delete memory (will cascade to memory_tags)
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        
        # Clean up orphaned tags
        cursor.execute("""
        DELETE FROM tags
        WHERE id NOT IN (SELECT DISTINCT tag_id FROM memory_tags)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted memory with ID {memory_id}")
        return {
            "success": True,
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error deleting memory: {str(e)}", exc_info=True)
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
        
        # Build query based on parameters
        sql_query = """
        SELECT DISTINCT m.id, m.title, m.content, m.created_at, m.updated_at
        FROM memories m
        """
        
        params = []
        where_clauses = []
        
        # Add tag filtering if tags provided
        if tags and len(tags) > 0:
            sql_query += """
            JOIN memory_tags mt ON m.id = mt.memory_id
            JOIN tags t ON mt.tag_id = t.id
            """
            placeholders = ", ".join(["?" for _ in tags])
            where_clauses.append(f"t.name IN ({placeholders})")
            params.extend(tags)
        
        # Add text search if query provided
        if query:
            where_clauses.append("(m.title LIKE ? OR m.content LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        # Add WHERE clause if we have conditions
        if where_clauses:
            sql_query += f"WHERE {' AND '.join(where_clauses)}"
        
        # Add limit
        sql_query += "\nORDER BY m.updated_at DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        
        # Format results
        memories = []
        for row in results:
            # Get tags for this memory
            cursor.execute("""
            SELECT t.name
            FROM tags t
            JOIN memory_tags mt ON t.id = mt.tag_id
            WHERE mt.memory_id = ?
            """, (row["id"],))
            
            memory_tags = [tag[0] for tag in cursor.fetchall()]
            
            memories.append({
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
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

# WebSocket endpoint for MCP
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("WebSocket connection attempt received")
    try:
        await websocket.accept()
        logger.info("WebSocket connection established successfully")
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {str(e)}", exc_info=True)
        return
    
    try:
        while True:
            # Receive message from client
            logger.info("Waiting for message from client...")
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received message: {message}")
            
            # Extract message details
            method = message.get("method")
            message_id = message.get("id")
            
            # Handle initialize method
            if method == "initialize":
                logger.debug("Handling initialize request")
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "experimental": {}
                        },
                        "serverInfo": {
                            "name": "Memory MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }))
                logger.info("Sent initialize response")
            
            # Handle tools/list method
            elif method == "tools/list":
                logger.debug("Handling tools/list request")
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
                                "name": "memory_update",
                                "description": "Update an existing memory",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "memory_id": {
                                            "type": "integer",
                                            "description": "ID of the memory to update"
                                        },
                                        "title": {
                                            "type": "string",
                                            "description": "New title for the memory"
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "New content for the memory"
                                        },
                                        "tags": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "New tags for the memory"
                                        }
                                    },
                                    "required": ["memory_id"]
                                }
                            },
                            {
                                "name": "memory_delete",
                                "description": "Delete a memory by ID",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "memory_id": {
                                            "type": "integer",
                                            "description": "ID of the memory to delete"
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
                logger.info("Sent tools/list response")
            
            # Handle tools/call method
            elif method == "tools/call":
                logger.debug("Handling tools/call request")
                params = message.get("params", {})
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
                    
                    elif tool_name == "memory_update":
                        memory_id = arguments.get("memory_id")
                        title = arguments.get("title")
                        content = arguments.get("content")
                        tags = arguments.get("tags")
                        result = await update_memory(memory_id, title, content, tags)
                    
                    elif tool_name == "memory_delete":
                        memory_id = arguments.get("memory_id")
                        result = await delete_memory(memory_id)
                    
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
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        }
                    }))
                    logger.info(f"Sent {tool_name} response")
            
            # Handle unknown methods
            else:
                logger.warning(f"Unknown method: {method}")
                await websocket.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)

# HTTP endpoint for health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Run the server
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5004  # Changed from 8093 to match default MCP port expectations
    logger.info(f"Starting Memory MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
