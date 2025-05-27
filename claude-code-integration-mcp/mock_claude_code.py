#!/usr/bin/env python3
"""
Mock Claude Code CLI for testing the Enhanced Claude Code Integration MCP Server
This script simulates Claude Code CLI behavior for development and testing
"""

import json
import sys
import time
import argparse
from pathlib import Path

def mock_claude_code_response(query, output_format="text", project_path=None):
    """Generate a mock response that simulates Claude Code CLI behavior"""
    
    if output_format == "json":
        response = {
            "conversation_id": "mock-conversation-12345",
            "messages": [
                {
                    "role": "system",
                    "content": "Mock Claude Code response",
                    "timestamp": "2025-05-26T12:00:00Z"
                },
                {
                    "role": "user", 
                    "content": query
                },
                {
                    "role": "assistant",
                    "content": f"Mock response to: {query}\n\nI understand you want me to help with: {query}\n\nProject context: {project_path or 'No project specified'}\n\nThis is a simulated response for testing the MCP integration.",
                    "timestamp": "2025-05-26T12:00:01Z"
                }
            ],
            "result": {
                "success": True,
                "total_tokens": 150,
                "model": "claude-sonnet-4-20250514"
            }
        }
        return json.dumps(response, indent=2)
    else:
        return f"""Mock Claude Code Response:

Query: {query}
Project: {project_path or 'No project specified'}

I understand you want help with: {query}

This is a simulated response for testing the Enhanced Claude Code Integration MCP Server. In a real scenario, I would analyze your project and provide specific coding assistance.

Task completed successfully in mock mode."""

def main():
    parser = argparse.ArgumentParser(description="Mock Claude Code CLI for testing")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--print", "-p", type=str, help="Non-interactive query")
    parser.add_argument("--output-format", default="text", choices=["text", "json", "stream-json"])
    parser.add_argument("--project", type=str, help="Project path")
    parser.add_argument("--max-turns", type=int, default=1, help="Maximum turns")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.version:
        print("claude-code v1.0.0-mock (Mock Version for MCP Testing)")
        return 0
    
    if args.print:
        # Simulate some processing time
        if args.verbose:
            print("Processing query...", file=sys.stderr)
        time.sleep(1)
        
        response = mock_claude_code_response(
            args.print,
            args.output_format,
            args.project
        )
        print(response)
        return 0
    
    print("Mock Claude Code CLI - Use --print for non-interactive mode", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
