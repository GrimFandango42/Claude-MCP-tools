#!/usr/bin/env python3
"""
Windows Computer Use MCP Server - Diagnostic Tool
Quick diagnostic and repair tool for the Windows Computer Use MCP server.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
import importlib.util

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_status(message, success=True):
    """Print a status message with color coding."""
    symbol = "✅" if success else "❌"
    print(f"{symbol} {message}")

def check_virtual_environment():
    """Check if we're in the correct virtual environment."""
    print_header("Virtual Environment Check")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        print_status("Virtual environment directory found")
        
        python_exe = venv_path / "Scripts" / "python.exe"
        if python_exe.exists():
            print_status("Python executable found in venv")
            return True
        else:
            print_status("Python executable missing in venv", False)
            return False
    else:
        print_status("Virtual environment directory not found", False)
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print_header("Dependencies Check")
    
    required_packages = {
        'mcp': 'MCP Framework',
        'pyautogui': 'GUI Automation',
        'PIL': 'Python Imaging Library',
        'win32api': 'Windows API (pywin32)'
    }
    
    all_good = True
    for package, description in required_packages.items():
        try:
            if package == 'PIL':
                import PIL
            elif package == 'win32api':
                import win32api
            else:
                __import__(package)
            print_status(f"{description} ({package}) available")
        except ImportError:
            print_status(f"{description} ({package}) missing", False)
            all_good = False
    
    return all_good

def check_server_file():
    """Check if server.py exists and can be imported."""
    print_header("Server File Check")
    
    server_file = Path("server.py")
    if server_file.exists():
        print_status("server.py file exists")
        
        # Try to import the server
        try:
            spec = importlib.util.spec_from_file_location("server", server_file)
            server_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server_module)
            print_status("server.py can be imported")
            
            # Check if it has the right class
            if hasattr(server_module, 'WindowsComputerUseMCP'):
                print_status("WindowsComputerUseMCP class found")
                return True
            else:
                print_status("WindowsComputerUseMCP class missing", False)
                return False
                
        except Exception as e:
            print_status(f"server.py import failed: {e}", False)
            return False
    else:
        print_status("server.py file missing", False)
        return False

def check_claude_config():
    """Check Claude Desktop configuration."""
    print_header("Claude Desktop Configuration Check")
    
    config_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    
    if config_path.exists():
        print_status("Claude Desktop config file found")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if 'mcpServers' in config and 'windows-computer-use' in config['mcpServers']:
                print_status("windows-computer-use server configured")
                
                server_config = config['mcpServers']['windows-computer-use']
                batch_file = server_config.get('args', [])
                if batch_file and len(batch_file) > 1:
                    batch_path = Path(batch_file[1])
                    if batch_path.exists():
                        print_status("Batch launcher file exists")
                        return True
                    else:
                        print_status("Batch launcher file missing", False)
                        return False
                else:
                    print_status("Invalid server configuration", False)
                    return False
            else:
                print_status("windows-computer-use server not configured", False)
                return False
                
        except Exception as e:
            print_status(f"Config file read error: {e}", False)
            return False
    else:
        print_status("Claude Desktop config file not found", False)
        return False

def run_diagnostic():
    """Run complete diagnostic."""
    print_header("Windows Computer Use MCP Server - Diagnostic")
    
    print("Running comprehensive diagnostic...")
    
    checks = [
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Server File", check_server_file),
        ("Claude Configuration", check_claude_config)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"{check_name} check failed: {e}", False)
            results.append((check_name, False))
    
    # Summary
    print_header("Diagnostic Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        print_status(f"{check_name}: {'PASS' if result else 'FAIL'}", result)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("All checks passed! Server should be working correctly.")
        print("\nNext steps:")
        print("1. Restart Claude Desktop")
        print("2. Test the computer use tools")
        print("3. Check server logs if issues persist")
    else:
        print_status("Some checks failed. Issues need to be resolved.", False)
        print("\nRecommended actions:")
        print("1. Run setup script to fix environment issues")
        print("2. Reinstall dependencies if needed")
        print("3. Check file permissions")
        print("4. Verify Claude Desktop configuration")
    
    return passed == total

def main():
    """Main diagnostic function."""
    # Change to server directory
    server_dir = Path(__file__).parent
    os.chdir(server_dir)
    
    success = run_diagnostic()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 DIAGNOSTIC PASSED - Server should be operational!")
    else:
        print("⚠️  DIAGNOSTIC FAILED - Issues detected that need resolution")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
