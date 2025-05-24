#!/usr/bin/env python3
"""
Node.js Installation Script for WSL
Installs Node.js LTS in WSL Ubuntu environment via Computer Use API
"""

import sys
import time
from server import ComputerUseAPI

def install_nodejs():
    """Install Node.js in WSL Ubuntu."""
    api = ComputerUseAPI()
    
    print("🚀 Installing Node.js in WSL Ubuntu...")
    print("=" * 50)
    
    # Method 1: Try snap installation (usually fastest)
    print("\n📦 Attempting snap installation...")
    result = api.bash_20250124("sudo snap install node --classic")
    print(f"Snap result: {result}")
    
    if result.get('exit_code') == 0:
        print("✅ Snap installation successful!")
    else:
        print("⚠️ Snap failed, trying NodeSource repository...")
        
        # Method 2: NodeSource repository (official method)
        print("\n📦 Installing from NodeSource repository...")
        
        # Download and install NodeSource repository
        setup_result = api.bash_20250124(
            "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
        )
        print(f"Repository setup: {setup_result}")
        
        if setup_result.get('exit_code') == 0:
            # Install Node.js
            install_result = api.bash_20250124("sudo apt-get install -y nodejs")
            print(f"Installation result: {install_result}")
        else:
            print("❌ NodeSource setup failed, trying alternative...")
            
            # Method 3: Ubuntu default repository
            print("\n📦 Installing from Ubuntu repository...")
            update_result = api.bash_20250124("sudo apt update")
            install_result = api.bash_20250124("sudo apt install -y nodejs npm")
            print(f"Ubuntu install result: {install_result}")
    
    # Verify installation
    print("\n🔍 Verifying Node.js installation...")
    node_version = api.bash_20250124("node --version")
    npm_version = api.bash_20250124("npm --version")
    
    print(f"Node.js version: {node_version}")
    print(f"NPM version: {npm_version}")
    
    if node_version.get('exit_code') == 0 and npm_version.get('exit_code') == 0:
        print("\n🎉 Node.js installation successful!")
        print(f"✅ Node.js: {node_version.get('output', '').strip()}")
        print(f"✅ NPM: {npm_version.get('output', '').strip()}")
        return True
    else:
        print("\n❌ Node.js installation failed")
        return False

def test_nodejs():
    """Test Node.js functionality."""
    api = ComputerUseAPI()
    
    print("\n🧪 Testing Node.js functionality...")
    
    # Test basic Node.js
    test_result = api.bash_20250124("node -e \"console.log('Hello from Node.js!')\"")
    print(f"Node.js test: {test_result}")
    
    # Test NPM
    npm_test = api.bash_20250124("npm --version")
    print(f"NPM test: {npm_test}")
    
    # Create a simple test project
    print("\n📝 Creating test project...")
    project_setup = api.bash_20250124("""
        mkdir -p ~/test-nodejs-project && 
        cd ~/test-nodejs-project && 
        echo '{"name": "test-project", "version": "1.0.0"}' > package.json &&
        echo 'console.log("Test project working!");' > index.js &&
        node index.js
    """)
    print(f"Project test: {project_setup}")
    
    return test_result.get('exit_code') == 0

def main():
    """Main installation process."""
    print("🔧 WSL Node.js Installation & Setup")
    print("=" * 50)
    
    # Check current status
    api = ComputerUseAPI()
    current_status = api.bash_20250124("node --version 2>/dev/null || echo 'Node.js not installed'")
    print(f"Current status: {current_status}")
    
    if "not installed" not in current_status.get('output', ''):
        print("✅ Node.js is already installed!")
        test_nodejs()
        return
    
    # Install Node.js
    success = install_nodejs()
    
    if success:
        # Test the installation
        test_nodejs()
        print("\n🚀 Node.js setup complete! Ready for JavaScript/TypeScript development.")
    else:
        print("\n❌ Installation failed. Please check WSL configuration.")

if __name__ == "__main__":
    main()