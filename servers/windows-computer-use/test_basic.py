#!/usr/bin/env python3
"""
Basic functionality test for Windows Computer Use MCP Server
This script tests the core functions without MCP protocol overhead.
"""

import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our server functions
from server import (
    capture_screenshot,
    execute_wsl_command,
    initialize_display_info,
    display_info
)

def test_display_initialization():
    """Test display information gathering."""
    print("🖥️  Testing Display Initialization...")
    try:
        initialize_display_info()
        print(f"   ✅ Display: {display_info['width']}x{display_info['height']}")
        print(f"   ✅ Scale Factor: {display_info['scale_factor']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_screenshot_capture():
    """Test screenshot functionality."""
    print("\n📸 Testing Screenshot Capture...")
    try:
        screenshot_bytes = capture_screenshot()
        print(f"   ✅ Screenshot captured: {len(screenshot_bytes):,} bytes")
        
        # Verify it's valid image data
        if screenshot_bytes.startswith(b'\x89PNG'):
            print("   ✅ Valid PNG format detected")
        else:
            print("   ⚠️  Unknown image format")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_wsl_bridge():
    """Test WSL command execution."""
    print("\n🐧 Testing WSL Bridge...")
    try:
        # Test basic WSL command
        result = execute_wsl_command("echo 'Hello from WSL'")
        
        if result['success']:
            print(f"   ✅ WSL command executed successfully")
            print(f"   ✅ Output: {result['stdout'].strip()}")
        else:
            print(f"   ❌ WSL command failed: {result['stderr']}")
            
        return result['success']
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_powershell_command():
    """Test PowerShell command execution."""
    print("\n💻 Testing PowerShell Execution...")
    try:
        import subprocess
        
        # Test basic PowerShell command
        ps_cmd = ["powershell", "-Command", "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory"]
        result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ PowerShell command executed successfully")
            print(f"   ✅ Output preview: {result.stdout[:100]}...")
        else:
            print(f"   ❌ PowerShell command failed: {result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_automation_libraries():
    """Test automation library imports and basic functionality."""
    print("\n🤖 Testing Automation Libraries...")
    
    try:
        import pyautogui
        import win32gui
        import win32api
        
        print("   ✅ pyautogui imported successfully")
        print("   ✅ win32gui imported successfully") 
        print("   ✅ win32api imported successfully")
        
        # Test basic pyautogui functionality
        screen_size = pyautogui.size()
        print(f"   ✅ Screen size detected: {screen_size}")
        
        # Test mouse position (without moving)
        mouse_pos = pyautogui.position()
        print(f"   ✅ Mouse position: {mouse_pos}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🚀 Windows Computer Use - Basic Functionality Test")
    print("=" * 60)
    
    tests = [
        ("Display Initialization", test_display_initialization),
        ("Automation Libraries", test_automation_libraries),
        ("Screenshot Capture", test_screenshot_capture),
        ("PowerShell Execution", test_powershell_command),
        ("WSL Bridge", test_wsl_bridge),
    ]
    
    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Windows Computer Use is ready for automation.")
    else:
        print("⚠️  Some tests failed. Check the errors above for troubleshooting.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)