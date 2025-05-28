#!/usr/bin/env python3
"""
Claude Code Wrapper - Handles asyncio event loop conflicts
Solves the "Cannot run the event loop while another loop is running" error
"""

import subprocess
import sys
import os
import json
import glob

class ClaudeCodeWrapper:
    def __init__(self):
        self.claude_code_path = self._find_claude_code()
    
    def _find_claude_code(self):
        """Find Claude Code executable in various locations"""
        possible_paths = [
            # Windows paths accessible from WSL
            "/mnt/c/Users/*/AppData/Local/Programs/claude-code/bin/claude-code.exe",
            "/mnt/c/Program Files/claude-code/claude-code.exe", 
            "/mnt/c/Program Files (x86)/claude-code/claude-code.exe",
            # Direct path if available
            "claude-code"
        ]
        
        for path_pattern in possible_paths:
            if "*" in path_pattern:
                # Handle wildcard paths
                matches = glob.glob(path_pattern)
                if matches:
                    return matches[0]
            else:
                # Check if executable exists
                try:
                    result = subprocess.run([path_pattern, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return path_pattern
                except:
                    continue
        return None
    
    def execute_task(self, task_description, project_path=None):
        """Execute Claude Code task without event loop conflicts"""
        if not self.claude_code_path:
            return {
                "success": False,
                "message": "Claude Code executable not found. Please install Claude Code CLI."
            }
        
        try:
            # Use subprocess instead of asyncio to avoid event loop conflicts
            cmd = [self.claude_code_path, task_description]
            
            if project_path:
                cmd.extend(["--project", str(project_path)])
            
            # Run in subprocess to avoid asyncio conflicts
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=project_path or os.getcwd()
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Claude Code task timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing Claude Code: {str(e)}"
            }

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python claude_code_wrapper.py 'task description' [project_path]")
        sys.exit(1)
    
    wrapper = ClaudeCodeWrapper()
    task_description = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = wrapper.execute_task(task_description, project_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
