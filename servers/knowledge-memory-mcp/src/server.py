#!/usr/bin/env python3
"""
Knowledge & Memory MCP Server (FastMCP-based)

A Model Context Protocol server that provides persistent knowledge management
with hybrid Zettelkasten and vector search capabilities.

This server adheres to the MCP specification and provides tools for creating,
retrieving, and organizing knowledge in a local-first, privacy-preserving manner.

JSONRPC communication happens over stdin/stdout, with logs going to stderr.
"""

import logging
import sys
import os
from pythonjsonlogger import jsonlogger
from mcp.server.fastmcp import FastMCP

# --- Structured Logging Setup ---
logHandler = logging.StreamHandler(stream=sys.stderr)
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger('knowledge-memory-mcp')
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
logger.propagate = False

# --- Import business logic modules ---
from src.storage.database import Database
from src.knowledge.zettelkasten import ZettelkastenManager
from src.vector.vector_store import VectorStore

# --- Determine data directory and database path ---
def get_data_dir():
    # Use environment variable or default to user home directory
    return os.environ.get(
        "KNOWLEDGE_MEMORY_DATA_DIR",
        os.path.join(os.path.expanduser("~"), ".knowledge-memory-mcp")
    )

def get_db_path():
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "knowledge.db")

# --- Initialize FastMCP and persistent components ---
mcp = FastMCP("knowledge-memory-mcp")
db = Database(get_db_path())
zettelkasten = ZettelkastenManager(db)
vector_store = VectorStore(db)

# --- Register tools ---
@mcp.tool()
def create_note(title: str, content: str, tags: list = None) -> dict:
    """Create a new note in the knowledge base."""
    note_id = zettelkasten.create_note(title, content, tags or [])
    return {"note_id": note_id}

@mcp.tool()
def search_notes(query: str, limit: int = 10) -> list:
    """Search notes by text query."""
    return zettelkasten.search_notes(query, limit)

@mcp.tool()
def semantic_search(query: str, limit: int = 10) -> list:
    """Search notes by semantic similarity."""
    return vector_store.semantic_search(query, limit)

@mcp.tool()
def get_note(note_id: str) -> dict:
    """Retrieve a specific note by ID."""
    return zettelkasten.get_note(note_id)

@mcp.tool()
def update_note(note_id: str, title: str = None, content: str = None, tags: list = None) -> bool:
    """Update an existing note."""
    return zettelkasten.update_note(note_id, title, content, tags)

@mcp.tool()
def delete_note(note_id: str) -> bool:
    """Delete a note from the knowledge base."""
    return zettelkasten.delete_note(note_id)

@mcp.tool()
def get_tags() -> list:
    """Get all tags used in the knowledge base."""
    return zettelkasten.get_all_tags()

@mcp.tool()
def search_by_tag(tag: str, limit: int = 10) -> list:
    """Search notes by tag."""
    return zettelkasten.search_notes_by_tag(tag, limit)

@mcp.tool()
def get_similar_notes(note_id: str, limit: int = 5) -> list:
    """Find notes similar to the specified note using vector similarity."""
    return vector_store.get_similar_notes(note_id, limit)

@mcp.tool()
def get_note_backlinks(note_id: str) -> list:
    """Get all notes that link to the specified note."""
    return zettelkasten.get_backlinks(note_id)

@mcp.tool()
def extract_and_link_references(note_id: str) -> dict:
    """Extract and create links for references within a note."""
    return zettelkasten.extract_and_link_references(note_id)

@mcp.tool()
def get_statistics() -> dict:
    """Get statistics about the knowledge base."""
    return {
        "note_count": zettelkasten.get_note_count(),
        "tag_count": len(zettelkasten.get_all_tags()),
        "link_count": zettelkasten.get_link_count(),
        "indexed_vectors": vector_store.get_embedding_count()
    }

@mcp.tool()
def debug_database_schema() -> dict:
    """Debug database schema and connection."""
    try:
        # Check table schema
        cursor = db.execute("PRAGMA table_info(notes)")
        schema = cursor.fetchall()
        schema_info = [dict(row) for row in schema]
        
        # Check if we can do a simple select
        cursor = db.execute("SELECT COUNT(*) as count FROM notes")
        count_result = cursor.fetchone()
        
        # Test insert without timestamps
        test_id = db.generate_id()
        simple_insert_error = None
        try:
            db.execute(
                "INSERT INTO notes (id, title, content) VALUES (?, ?, ?)",
                (test_id, "Test Title", "Test Content")
            )
            db.conn.rollback()  # Rollback the test insert
            simple_insert_success = True
        except Exception as e:
            simple_insert_success = False
            simple_insert_error = str(e)
        
        return {
            "schema": schema_info,
            "note_count": dict(count_result)["count"] if count_result else 0,
            "simple_insert_success": simple_insert_success,
            "simple_insert_error": simple_insert_error if not simple_insert_success else None,
            "database_path": db.db_path
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

# Register signal handlers for graceful shutdown
import signal

def handle_signal(sig, frame):
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    # Close database connections
    db.close()
    logger.info("Database connections closed")
    # Exit with success status
    sys.exit(0)

# Register handlers for common signals
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

if __name__ == "__main__":
    logger.info("Starting Knowledge Memory MCP Server (FastMCP-based)...")
    mcp.run(transport="stdio")
