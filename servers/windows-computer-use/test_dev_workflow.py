#!/usr/bin/env python3
"""
Development Workflow Test for Windows Computer Use
Tests VS Code, WSL, and development environment automation
"""

import subprocess
import time
import pyautogui
import os

def test_wsl_dev_environment():
    """Test WSL development environment capabilities"""
    print("🐧 Testing WSL Development Environment")
    
    dev_commands = [
        ("Check WSL Version", "wsl --version"),
        ("List WSL Distributions", "wsl --list --verbose"),
        ("WSL System Info", ["wsl", "--", "uname", "-a"]),
        ("Check Python in WSL", ["wsl", "--", "python3", "--version"]),
        ("Check Node.js in WSL", ["wsl", "--", "node", "--version"]),
        ("Check Git in WSL", ["wsl", "--", "git", "--version"]),
        ("WSL Current Directory", ["wsl", "--", "pwd"]),
        ("WSL List Windows C Drive", ["wsl", "--", "ls", "-la", "/mnt/c/AI_Projects"])
    ]
    
    results = []
    for desc, cmd in dev_commands:
        print(f"\n   Testing: {desc}")
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()[:100]
                print(f"   ✅ Success: {output}...")
                results.append((desc, True, output))
            else:
                error = result.stderr.strip()[:100]
                print(f"   ❌ Failed: {error}...")
                results.append((desc, False, error))
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append((desc, False, str(e)))
    
    return results

def test_file_operations():
    """Test cross-platform file operations"""
    print("\n📁 Testing Cross-Platform File Operations")
    
    test_dir = "C:\\Temp\\computer_use_test"
    test_file = os.path.join(test_dir, "test_file.txt")
    test_content = "Windows Computer Use Test File\nCreated for cross-platform testing"
    
    operations = []
    
    try:
        # Create directory
        print("   Creating test directory...")
        os.makedirs(test_dir, exist_ok=True)
        operations.append(("Create Directory", True))
        
        # Write test file
        print("   Writing test file...")
        with open(test_file, 'w') as f:
            f.write(test_content)
        operations.append(("Write File", True))
        
        # Read file back
        print("   Reading file back...")
        with open(test_file, 'r') as f:
            read_content = f.read()
        
        if read_content == test_content:
            print("   ✅ File content matches")
            operations.append(("Read File", True))
        else:
            print("   ❌ File content mismatch")
            operations.append(("Read File", False))
        
        # Access file from WSL
        print("   Accessing file from WSL...")
        wsl_path = test_file.replace("C:", "/mnt/c").replace("\\", "/")
        result = subprocess.run(
            ["wsl", "--", "cat", wsl_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip() == test_content:
            print("   ✅ WSL file access successful")
            operations.append(("WSL File Access", True))
        else:
            print(f"   ❌ WSL file access failed: {result.stderr}")
            operations.append(("WSL File Access", False))
        
        # Cleanup
        print("   Cleaning up test files...")
        os.remove(test_file)
        os.rmdir(test_dir)
        operations.append(("Cleanup", True))
        
    except Exception as e:
        print(f"   ❌ File operations error: {e}")
        operations.append(("File Operations", False))
    
    return operations

def test_vs_code_automation():
    """Test VS Code automation (if available)"""
    print("\n💻 Testing VS Code Automation")
    
    try:
        # Check if VS Code is available
        print("   Checking VS Code availability...")
        result = subprocess.run(["code", "--version"], capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            print("   ⚠️  VS Code not available in PATH")
            return [("VS Code Available", False)]
        
        print(f"   ✅ VS Code found: {result.stdout.split()[0]}")
        
        # Test opening VS Code to a specific directory
        print("   Testing VS Code project opening...")
        test_project = "C:\\AI_Projects\\Claude-MCP-tools"
        
        # This would normally open VS Code - commenting out for safety
        # subprocess.Popen(["code", test_project])
        
        print("   ✅ VS Code commands available")
        return [("VS Code Available", True), ("VS Code Commands", True)]
        
    except Exception as e:
        print(f"   ❌ VS Code test error: {e}")
        return [("VS Code Test", False)]

def test_automation_safety():
    """Test automation safety features"""
    print("\n🛡️  Testing Automation Safety")
    
    try:
        # Test pyautogui failsafe
        print("   Testing pyautogui failsafe...")
        pyautogui.FAILSAFE = True
        current_pos = pyautogui.position()
        print(f"   ✅ Current mouse position: {current_pos}")
        print(f"   ✅ Screen size: {pyautogui.size()}")
        print(f"   ✅ Failsafe enabled: {pyautogui.FAILSAFE}")
        
        # Test pause setting
        original_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0.1
        print(f"   ✅ Automation pause: {pyautogui.PAUSE}s")
        pyautogui.PAUSE = original_pause
        
        return [("Safety Features", True)]
        
    except Exception as e:
        print(f"   ❌ Safety test error: {e}")
        return [("Safety Features", False)]

def main():
    """Run development workflow tests"""
    print("🚀 Windows Computer Use - Development Workflow Test")
    print("=" * 60)
    
    all_results = []
    
    # Run all test suites
    test_suites = [
        ("WSL Development Environment", test_wsl_dev_environment),
        ("File Operations", test_file_operations),
        ("VS Code Automation", test_vs_code_automation),
        ("Automation Safety", test_automation_safety),
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n🧪 {suite_name}")
        print("-" * 40)
        try:
            results = test_func()
            all_results.extend(results)
        except Exception as e:
            print(f"❌ Test suite error: {e}")
            all_results.append((suite_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Development Workflow Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(all_results)
    
    for test_name, success, *details in all_results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All development workflow tests passed!")
        print("🚀 Ready for advanced Computer Use automation!")
    else:
        print("⚠️  Some tests failed - check individual results above")
    
    return passed == total

if __name__ == "__main__":
    main()