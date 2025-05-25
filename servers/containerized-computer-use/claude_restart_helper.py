#!/usr/bin/env python3
"""
Claude Desktop Automation Helper
Uses Windows Computer Use MCP to restart Claude Desktop if available.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def check_claude_running():
    """Check if Claude Desktop is running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Claude.exe"],
            capture_output=True,
            text=True
        )
        return "Claude.exe" in result.stdout
    except:
        return False

def kill_claude():
    """Kill Claude Desktop process."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "Claude.exe"], capture_output=True)
        time.sleep(2)
        return True
    except:
        return False

def start_claude():
    """Start Claude Desktop."""
    try:
        # Common paths for Claude Desktop
        possible_paths = [
            r"C:\Users\Nithin\AppData\Local\Programs\claude-desktop\Claude.exe",
            r"C:\Program Files\Claude\Claude.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\claude-desktop\Claude.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                print(f"Started Claude Desktop from: {path}")
                return True
        
        # Try using start command as fallback
        subprocess.Popen(["start", "claude://"], shell=True)
        return True
    except Exception as e:
        print(f"Failed to start Claude: {e}")
        return False

def restart_claude_desktop():
    """Restart Claude Desktop."""
    print("Checking Claude Desktop status...")
    
    if check_claude_running():
        print("Claude Desktop is running. Stopping it...")
        if kill_claude():
            print("Claude Desktop stopped successfully.")
        else:
            print("Failed to stop Claude Desktop.")
            return False
    else:
        print("Claude Desktop is not running.")
    
    print("Starting Claude Desktop...")
    if start_claude():
        print("Claude Desktop started successfully.")
        print("Please wait 10-15 seconds for it to fully initialize.")
        return True
    else:
        print("Failed to start Claude Desktop.")
        print("Please start it manually.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restart":
        restart_claude_desktop()
    else:
        if check_claude_running():
            print("Claude Desktop is running.")
        else:
            print("Claude Desktop is not running.")
