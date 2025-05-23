#!/usr/bin/env python3
"""
Interactive demo for containerized Computer Use MCP Server
Demonstrates various capabilities with visual feedback
"""

import json
import subprocess
import time
import base64
import sys
from typing import Dict, Any
from datetime import datetime


class ContainerDemo:
    """Interactive demonstration of containerized Computer Use capabilities."""
    
    def __init__(self):
        self.container_name = "windows-computer-use"
        
    def run_mcp_command(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an MCP command in the container."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        # Execute command in container
        cmd = [
            "docker", "exec", "-i", self.container_name,
            "python3", "-c",
            f"import sys, json; from container_mcp_wrapper import ContainerMCPServer; "
            f"import asyncio; server = ContainerMCPServer(); "
            f"result = asyncio.run(server.handle_request({json.dumps(request)})); "
            f"print(json.dumps(result))"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": f"Command failed: {result.stderr}"}
        except Exception as e:
            return {"error": f"Execution error: {str(e)}"}
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}\n")
    
    def save_screenshot(self, name: str):
        """Take and save a screenshot."""
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {"action": "screenshot"}
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            for item in content:
                if item.get("type") == "image":
                    screenshot_data = item.get("data", "")
                    if screenshot_data:
                        # Save to file
                        filename = f"screenshot_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        with open(filename, "wb") as f:
                            f.write(base64.b64decode(screenshot_data))
                        print(f"✓ Screenshot saved: {filename}")
                        return True
        
        print("✗ Failed to capture screenshot")
        return False
    
    def demo_system_info(self):
        """Demonstrate system information gathering."""
        self.print_header("System Information Demo")
        
        print("Gathering container system information...")
        
        # Get system info
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "uname -a && echo && lsb_release -a 2>/dev/null && echo && df -h / && echo && free -h"}
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                print(content[0].get("text", ""))
        
        # Check installed packages
        print("\nChecking key installed packages...")
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "python3 --version && echo && pip list | grep -E 'pyautogui|pillow|fastmcp'"}
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                print(content[0].get("text", ""))
    
    def demo_file_operations(self):
        """Demonstrate file operations."""
        self.print_header("File Operations Demo")
        
        # Create a demo file
        demo_content = """# Container Demo File
This file was created inside the containerized Computer Use server.

Current time: {}
Container environment: Ubuntu with X11 display

## Features Demonstrated:
- File creation
- Content editing
- File reading
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        file_path = "/workspace/demo_file.md"
        
        print(f"Creating file: {file_path}")
        response = self.run_mcp_command("tools/call", {
            "name": "text_editor_20250429",
            "arguments": {
                "command": "create",
                "path": file_path,
                "file_text": demo_content
            }
        })
        
        if "result" in response:
            print("✓ File created successfully")
        
        # Read the file back
        print(f"\nReading file: {file_path}")
        response = self.run_mcp_command("tools/call", {
            "name": "text_editor_20250429",
            "arguments": {
                "command": "view",
                "path": file_path
            }
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                print("\nFile contents:")
                print("-" * 40)
                print(content[0].get("text", ""))
                print("-" * 40)
        
        # List workspace files
        print("\nListing workspace files...")
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "ls -la /workspace/"}
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                print(content[0].get("text", ""))
    
    def demo_gui_automation(self):
        """Demonstrate GUI automation capabilities."""
        self.print_header("GUI Automation Demo")
        
        print("Starting GUI automation demo...")
        
        # Take initial screenshot
        print("\n1. Taking initial screenshot...")
        self.save_screenshot("initial")
        
        # Open a terminal
        print("\n2. Opening terminal application...")
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "key",
                "key": "cmd+alt+t"  # Terminal shortcut
            }
        })
        time.sleep(2)
        
        # Type a command
        print("\n3. Typing demo command...")
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "type",
                "text": "echo 'Hello from containerized Computer Use!'"
            }
        })
        time.sleep(1)
        
        # Press Enter
        print("\n4. Executing command...")
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "key",
                "key": "Return"
            }
        })
        time.sleep(1)
        
        # Take final screenshot
        print("\n5. Taking final screenshot...")
        self.save_screenshot("gui_demo")
        
        print("\n✓ GUI automation demo completed")
    
    def demo_desktop_interaction(self):
        """Demonstrate desktop interaction capabilities."""
        self.print_header("Desktop Interaction Demo")
        
        print("Demonstrating mouse and keyboard controls...")
        
        # Move mouse in a pattern
        print("\n1. Moving mouse in a square pattern...")
        positions = [(400, 300), (600, 300), (600, 500), (400, 500), (400, 300)]
        
        for i, (x, y) in enumerate(positions):
            print(f"   Moving to ({x}, {y})")
            response = self.run_mcp_command("tools/call", {
                "name": "computer_20250124",
                "arguments": {
                    "action": "mouse_move",
                    "coordinate": [x, y]
                }
            })
            time.sleep(0.5)
        
        # Demonstrate click
        print("\n2. Clicking at center of screen...")
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "left_click",
                "coordinate": [500, 400]
            }
        })
        
        # Demonstrate scrolling
        print("\n3. Demonstrating scroll...")
        response = self.run_mcp_command("tools/call", {
            "name": "computer_20250124",
            "arguments": {
                "action": "scroll",
                "coordinate": [500, 400],
                "direction": "down",
                "amount": 3
            }
        })
        
        print("\n✓ Desktop interaction demo completed")
    
    def demo_advanced_features(self):
        """Demonstrate advanced features."""
        self.print_header("Advanced Features Demo")
        
        print("Demonstrating advanced capabilities...")
        
        # Create a Python script in the container
        script_content = '''#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave Generated in Container')
plt.xlabel('X')
plt.ylabel('sin(X)')
plt.grid(True)
plt.savefig('/workspace/sine_wave.png')
print("Plot saved to /workspace/sine_wave.png")
'''
        
        print("\n1. Creating Python visualization script...")
        response = self.run_mcp_command("tools/call", {
            "name": "text_editor_20250429",
            "arguments": {
                "command": "create",
                "path": "/workspace/plot_demo.py",
                "file_text": script_content
            }
        })
        
        print("\n2. Installing matplotlib...")
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "pip install matplotlib --quiet"}
        })
        
        print("\n3. Running visualization script...")
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "cd /workspace && python3 plot_demo.py"}
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                print(content[0].get("text", ""))
        
        # Check if file was created
        print("\n4. Verifying output...")
        response = self.run_mcp_command("tools/call", {
            "name": "bash_20250124",
            "arguments": {"command": "ls -la /workspace/*.png"}
        })
        
        if "result" in response and "content" in response.get("result", {}):
            content = response["result"]["content"]
            if content and content[0].get("type") == "text":
                print(content[0].get("text", ""))
        
        print("\n✓ Advanced features demo completed")
    
    def run_interactive_demo(self):
        """Run the full interactive demo."""
        self.print_header("Containerized Computer Use Interactive Demo")
        
        print("This demo will showcase various capabilities of the")
        print("containerized Computer Use MCP server.")
        print("\nMake sure you have VNC viewer connected to see visual demos!")
        print("VNC URL: localhost:5900")
        print("Password: vnc123")
        
        input("\nPress Enter to start the demo...")
        
        demos = [
            ("System Information", self.demo_system_info),
            ("File Operations", self.demo_file_operations),
            ("GUI Automation", self.demo_gui_automation),
            ("Desktop Interaction", self.demo_desktop_interaction),
            ("Advanced Features", self.demo_advanced_features)
        ]
        
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n[{i}/{len(demos)}] Running: {name}")
            
            try:
                demo_func()
                print(f"\n✓ {name} completed successfully")
            except Exception as e:
                print(f"\n✗ {name} failed: {e}")
            
            if i < len(demos):
                input("\nPress Enter to continue to next demo...")
        
        self.print_header("Demo Complete!")
        print("All demonstrations have been completed.")
        print("\nCheck the following outputs:")
        print("- Screenshots: screenshot_*.png files")
        print("- Workspace files: Available in container at /workspace/")
        print("- Container logs: docker logs windows-computer-use")


def main():
    """Run the demo."""
    demo = ContainerDemo()
    
    # Check if container is running
    cmd = ["docker", "ps", "--filter", f"name={demo.container_name}", "--format", "{{.Names}}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if demo.container_name not in result.stdout:
        print(f"Error: Container '{demo.container_name}' is not running!")
        print("Please start the container with: .\\start-container.ps1")
        sys.exit(1)
    
    try:
        demo.run_interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
