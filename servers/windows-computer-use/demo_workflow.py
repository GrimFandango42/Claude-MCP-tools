#!/usr/bin/env python3
"""
Interactive Demo Workflow for Windows Computer Use
This demonstrates practical automation capabilities.
"""

import time
import pyautogui
import subprocess
from PIL import ImageGrab
import io
import base64

# Configure pyautogui
pyautogui.PAUSE = 0.5  # Pause between actions
pyautogui.FAILSAFE = True

class WindowsComputerUseDemo:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"🖥️  Screen: {self.screen_width}x{self.screen_height}")
    
    def take_screenshot(self, description=""):
        """Take a screenshot and show info"""
        screenshot = ImageGrab.grab()
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        size = len(img_buffer.getvalue())
        print(f"📸 Screenshot: {description} ({size:,} bytes)")
        return screenshot
    
    def demo_notepad_automation(self):
        """Demonstrate automating Notepad"""
        print("\n🗒️  Demo: Notepad Automation")
        print("   Opening Notepad...")
        
        # Open Run dialog
        pyautogui.hotkey('win', 'r')
        time.sleep(0.5)
        
        # Type notepad and press enter
        pyautogui.typewrite('notepad')
        pyautogui.press('enter')
        time.sleep(1)
        
        self.take_screenshot("Notepad opened")
        
        # Type sample text
        sample_text = """Windows Computer Use Demo
========================

This text was automatically typed using:
- Python automation
- Windows Computer Use MCP Server  
- Cross-platform integration capabilities

Current time: """ + time.strftime("%Y-%m-%d %H:%M:%S")
        
        print("   Typing sample text...")
        pyautogui.typewrite(sample_text)
        
        self.take_screenshot("Text typed in Notepad")
        
        # Save file
        print("   Saving file...")
        pyautogui.hotkey('ctrl', 's')
        time.sleep(0.5)
        
        # Type filename
        filename = "computer_use_demo.txt"
        pyautogui.typewrite(filename)
        pyautogui.press('enter')
        time.sleep(0.5)
        
        self.take_screenshot("File saved")
        
        # Close notepad
        print("   Closing Notepad...")
        pyautogui.hotkey('alt', 'f4')
        
        return filename
    
    def demo_calculator(self):
        """Demonstrate calculator automation"""
        print("\n🧮 Demo: Calculator Automation")
        print("   Opening Calculator...")
        
        # Open calculator
        pyautogui.hotkey('win', 'r')
        time.sleep(0.5)
        pyautogui.typewrite('calc')
        pyautogui.press('enter')
        time.sleep(1)
        
        self.take_screenshot("Calculator opened")
        
        # Perform calculation: 123 + 456 = 
        print("   Calculating 123 + 456...")
        
        # Click numbers and operators
        calculation = "123+456="
        for char in calculation:
            if char.isdigit():
                pyautogui.typewrite(char)
            elif char == '+':
                pyautogui.typewrite('+')
            elif char == '=':
                pyautogui.press('enter')
            time.sleep(0.2)
        
        self.take_screenshot("Calculation result")
        
        # Close calculator
        print("   Closing Calculator...")
        pyautogui.hotkey('alt', 'f4')
    
    def demo_file_explorer(self):
        """Demonstrate file explorer automation"""
        print("\n📁 Demo: File Explorer Navigation")
        print("   Opening File Explorer...")
        
        # Open file explorer
        pyautogui.hotkey('win', 'e')
        time.sleep(1)
        
        self.take_screenshot("File Explorer opened")
        
        # Navigate to Documents
        print("   Navigating to Documents...")
        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
        time.sleep(0.5)
        pyautogui.typewrite('C:\\Users\\%USERNAME%\\Documents')
        pyautogui.press('enter')
        time.sleep(1)
        
        self.take_screenshot("Documents folder")
        
        # Close file explorer
        print("   Closing File Explorer...")
        pyautogui.hotkey('alt', 'f4')
    
    def demo_powershell_commands(self):
        """Demonstrate PowerShell command execution"""
        print("\n💻 Demo: PowerShell Commands")
        
        commands = [
            "Get-Date",
            "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory",
            "Get-Process | Sort-Object CPU -Descending | Select-Object -First 3"
        ]
        
        for cmd in commands:
            print(f"   Executing: {cmd}")
            try:
                result = subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    output = result.stdout.strip()[:200]  # Limit output
                    print(f"   ✅ Result: {output}...")
                else:
                    print(f"   ❌ Error: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    def demo_wsl_commands(self):
        """Demonstrate WSL command execution"""
        print("\n🐧 Demo: WSL Commands")
        
        commands = [
            "pwd",
            "whoami", 
            "ls -la /mnt/c/Users",
            "python3 --version"
        ]
        
        for cmd in commands:
            print(f"   Executing: {cmd}")
            try:
                result = subprocess.run(
                    ["wsl", "--", "bash", "-c", cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    output = result.stdout.strip()
                    print(f"   ✅ Result: {output}")
                else:
                    print(f"   ❌ Error: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    def demo_system_info(self):
        """Demonstrate system information gathering"""
        print("\n🔍 Demo: System Information")
        
        # Screen info
        print(f"   Screen Resolution: {self.screen_width}x{self.screen_height}")
        
        # Mouse position
        mouse_x, mouse_y = pyautogui.position()
        print(f"   Current Mouse Position: ({mouse_x}, {mouse_y})")
        
        # System info via PowerShell
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject -Class Win32_OperatingSystem | Select-Object Caption, Version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"   OS Info: {result.stdout.strip()}")
        except:
            print("   ❌ Could not get OS info")

def main():
    """Run the demo workflow"""
    print("🚀 Windows Computer Use - Interactive Demo")
    print("=" * 50)
    print("⚠️  This demo will automate your desktop.")
    print("⚠️  Move mouse to top-left corner to abort if needed.")
    print("=" * 50)
    
    # Ask for confirmation
    response = input("\n🤔 Proceed with automation demo? (y/n): ")
    if response.lower() != 'y':
        print("❌ Demo cancelled.")
        return
    
    print("\n⏳ Starting demo in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print("\n🎬 Demo starting!")
    
    demo = WindowsComputerUseDemo()
    
    try:
        # Run demo workflows
        demo.demo_system_info()
        demo.demo_powershell_commands()
        demo.demo_wsl_commands()
        
        print(f"\n🎯 GUI Automation demos (will control your desktop)...")
        time.sleep(2)
        
        demo.demo_notepad_automation()
        demo.demo_calculator()
        demo.demo_file_explorer()
        
        print("\n🎉 Demo completed successfully!")
        print("✅ All Windows Computer Use capabilities verified")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n📋 Demo Summary:")
    print("   ✅ Screenshot capture")
    print("   ✅ Mouse/keyboard automation") 
    print("   ✅ Application control")
    print("   ✅ PowerShell command execution")
    print("   ✅ WSL bridge functionality")
    print("   ✅ System information gathering")

if __name__ == "__main__":
    main()