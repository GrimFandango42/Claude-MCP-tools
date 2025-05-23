#!/usr/bin/env python3
"""
Simple test for Windows Computer Use core functionality
"""

import sys
import base64
from PIL import ImageGrab
import pyautogui

def test_screenshot():
    """Test screenshot capture"""
    print("📸 Testing screenshot...")
    try:
        # Take screenshot
        screenshot = ImageGrab.grab()
        print(f"   ✅ Screenshot size: {screenshot.size}")
        
        # Convert to bytes
        import io
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        screenshot_bytes = img_buffer.getvalue()
        print(f"   ✅ Screenshot bytes: {len(screenshot_bytes):,}")
        
        # Encode as base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        print(f"   ✅ Base64 length: {len(screenshot_b64):,}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_mouse_info():
    """Test mouse position detection"""
    print("\n🖱️  Testing mouse info...")
    try:
        # Get screen size
        screen_size = pyautogui.size()
        print(f"   ✅ Screen size: {screen_size}")
        
        # Get mouse position  
        mouse_pos = pyautogui.position()
        print(f"   ✅ Mouse position: {mouse_pos}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_wsl():
    """Test WSL availability"""
    print("\n🐧 Testing WSL...")
    try:
        import subprocess
        
        # Test if WSL is available
        result = subprocess.run(
            ["wsl", "--", "echo", "WSL Test"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"   ✅ WSL available: {result.stdout.strip()}")
        else:
            print(f"   ⚠️  WSL not available: {result.stderr}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Simple Windows Computer Use Test")
    print("=" * 40)
    
    tests = [
        ("Screenshot", test_screenshot),
        ("Mouse Info", test_mouse_info), 
        ("WSL", test_wsl)
    ]
    
    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))
    
    print("\n" + "=" * 40)
    print("📊 Results:")
    passed = 0
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    main()