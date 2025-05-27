#!/usr/bin/env python3
"""
Test Claude Code CLI availability and integration
"""
import os
import subprocess
import sys

def test_claude_availability():
    """Test if Claude Code is available with proper PATH"""
    # Set the PATH to include the node binary location
    env = os.environ.copy()
    env['PATH'] = '/home/nithin/.nvm/versions/node/v24.1.0/bin:' + env.get('PATH', '')
    
    try:
        result = subprocess.run(
            ['claude', '--version'], 
            capture_output=True, 
            text=True, 
            timeout=10,
            env=env
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout.strip()}")
        
        if result.stderr:
            print(f"Error: {result.stderr.strip()}")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("Claude binary not found")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_claude_help():
    """Test Claude help command"""
    env = os.environ.copy()
    env['PATH'] = '/home/nithin/.nvm/versions/node/v24.1.0/bin:' + env.get('PATH', '')
    
    try:
        result = subprocess.run(
            ['claude', '--help'], 
            capture_output=True, 
            text=True, 
            timeout=10,
            env=env
        )
        
        print("\n--- Claude Help Output ---")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Help command failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Claude Code CLI availability...")
    
    available = test_claude_availability()
    if available:
        print("✅ Claude Code is available!")
        test_claude_help()
    else:
        print("❌ Claude Code is not available!")
        print("Current PATH:", os.environ.get('PATH', 'Not set'))
    
    sys.exit(0 if available else 1)
