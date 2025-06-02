# Knowledge Memory MCP Server

A Model Context Protocol server that provides persistent knowledge management with hybrid Zettelkasten and vector search capabilities. This server allows you to create, retrieve, and organize knowledge in a local-first, privacy-preserving manner.

## Features

- Note creation, updating, and deletion
- Tag-based organization
- Automatic link extraction between notes
- Vector-based similarity search (using embeddings)
- Local SQLite database storage
- Privacy-focused, local-first architecture

## Installation

1. Create and activate a Python virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -e .
```

## Usage

1. Start the server:

```bash
python src/server.py
```

2. The server will communicate via standard I/O following the MCP protocol.

## Configuration

The server stores data in `~/.knowledge-memory-mcp/knowledge.db` by default. You can customize the location by setting the `KNOWLEDGE_MEMORY_DATA_DIR` environment variable.

## MCP Tools

The server provides the following MCP tools:

- `create_note`: Create a new note with title, content, and optional tags
- `get_note`: Retrieve a note by ID
- `update_note`: Update an existing note
- `delete_note`: Delete a note by ID
- `search_notes`: Search notes by title and content
- `get_tags`: Get all tags in the knowledge base
- `search_by_tag`: Search notes by tag
- `get_similar_notes`: Find notes similar to a specified note using vector similarity
- `get_note_backlinks`: Get notes that link to a specified note
- `extract_and_link_references`: Extract and create links for references within a note
- `get_statistics`: Get statistics about the knowledge base

## Development

The server is built using FastMCP, a Python framework for creating MCP servers. It uses SQLite for storage and implements structured JSON logging for easier debugging.

## Troubleshooting

Logs are written to stderr in JSON format. When running via Claude Desktop, these logs will be available in the Claude Desktop logs directory.