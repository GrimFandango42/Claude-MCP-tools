#!/usr/bin/env python3
"""
🚀 Node.js Installation for WSL Ubuntu - Proper Setup
Install Node.js directly in WSL environment for Claude Code
"""

import sys
import time
sys.path.append('.')
from server import ComputerUseAPI

def install_nodejs_wsl():
    """Install Node.js 20.x LTS in WSL Ubuntu."""
    print("🚀 INSTALLING NODE.JS 20.x LTS IN WSL")
    print("=" * 50)
    
    api = ComputerUseAPI()
    
    # Step 1: Update system
    print("\n🔄 Step 1: Updating system packages...")
    update_result = api.bash_20250124("sudo apt update")
    print(f"   System update: {'✅' if update_result.get('exit_code') == 0 else '❌'}")
    
    # Step 2: Install curl if not present
    print("\n🔄 Step 2: Ensuring curl is available...")
    curl_result = api.bash_20250124("sudo apt install -y curl")
    print(f"   Curl installation: {'✅' if curl_result.get('exit_code') == 0 else '❌'}")
    
    # Step 3: Add NodeSource repository
    print("\n🔄 Step 3: Adding NodeSource repository...")
    nodesource_result = api.bash_20250124("""
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    """)
    print(f"   NodeSource repo: {'✅' if nodesource_result.get('exit_code') == 0 else '❌'}")
    
    # Step 4: Install Node.js
    print("\n🔄 Step 4: Installing Node.js...")
    nodejs_result = api.bash_20250124("sudo apt install -y nodejs")
    print(f"   Node.js installation: {'✅' if nodejs_result.get('exit_code') == 0 else '❌'}")
    
    # Step 5: Verify installation
    print("\n🔍 Step 5: Verifying installation...")
    verify_result = api.bash_20250124("""
        node --version &&
        npm --version &&
        echo "Node.js and npm successfully installed!"
    """)
    
    if verify_result.get('exit_code') == 0:
        print(f"   ✅ Verification successful!")
        print(f"   📊 Versions: {verify_result.get('output', '').strip()}")
        return True
    else:
        print(f"   ❌ Verification failed: {verify_result.get('output', '')}")
        return False

def configure_npm_global():
    """Configure npm for global package installation."""
    print("\n⚙️ CONFIGURING NPM FOR GLOBAL PACKAGES")
    print("=" * 50)
    
    api = ComputerUseAPI()
    
    # Create npm global directory
    config_result = api.bash_20250124("""
        mkdir -p ~/.npm-global &&
        npm config set prefix ~/.npm-global &&
        echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc &&
        echo "NPM configured for user directory"
    """)
    
    if config_result.get('exit_code') == 0:
        print("   ✅ NPM global configuration complete")
        return True
    else:
        print(f"   ❌ NPM configuration failed: {config_result.get('output', '')}")
        return False

def install_claude_code_fresh():
    """Install Claude Code with fresh npm setup."""
    print("\n🎯 INSTALLING CLAUDE CODE")
    print("=" * 50)
    
    api = ComputerUseAPI()
    
    # Install Claude Code
    install_result = api.bash_20250124("""
        source ~/.bashrc &&
        export PATH=~/.npm-global/bin:$PATH &&
        npm install -g @anthropic-ai/claude-code &&
        echo "Claude Code installation complete"
    """)
    
    if install_result.get('exit_code') == 0:
        print("   ✅ Claude Code installed successfully!")
        
        # Verify Claude availability
        verify_result = api.bash_20250124("""
            source ~/.bashrc &&
            export PATH=~/.npm-global/bin:$PATH &&
            which claude && echo "Claude Code command available"
        """)
        
        if verify_result.get('exit_code') == 0:
            print("   ✅ Claude Code command verified!")
            print(f"   📍 Claude location: {verify_result.get('output', '').strip()}")
            return True
        else:
            print(f"   ❌ Claude command verification failed")
            return False
    else:
        print(f"   ❌ Claude Code installation failed: {install_result.get('output', '')}")
        return False

def final_test():
    """Final comprehensive test."""
    print("\n🧪 FINAL INTEGRATION TEST")
    print("=" * 50)
    
    api = ComputerUseAPI()
    
    # Create test project
    test_result = api.bash_20250124("""
        cd ~ &&
        rm -rf claude-integration-test &&
        mkdir claude-integration-test &&
        cd claude-integration-test &&
        echo "# Claude Code Integration Test" > README.md &&
        echo "console.log('Hello Claude Code!');" > test.js &&
        echo "def hello(): return 'Hello from Python!'" > test.py &&
        ls -la
    """)
    
    if test_result.get('exit_code') == 0:
        print("   ✅ Test project created")
        
        # Test Claude availability in project
        claude_test = api.bash_20250124("""
            source ~/.bashrc &&
            export PATH=~/.npm-global/bin:$PATH &&
            cd ~/claude-integration-test &&
            which claude && 
            echo "Claude Code ready in test project!"
        """)
        
        if 'ready' in claude_test.get('output', ''):
            print("   ✅ Claude Code available in project directory")
            
            print("\n🎉 INSTALLATION COMPLETE!")
            print("📍 To use Claude Code:")
            print("   cd ~/claude-integration-test")
            print("   source ~/.bashrc")
            print("   claude")
            print("\n🔐 First run requires Anthropic authentication")
            return True
        else:
            print(f"   ❌ Claude test failed: {claude_test.get('output', '')}")
            return False
    else:
        print(f"   ❌ Test project creation failed")
        return False

def main():
    """Main installation process."""
    print("🚀 COMPLETE NODE.JS + CLAUDE CODE INSTALLATION")
    print("🎯 Installing in WSL Ubuntu for AI-powered development")
    print("=" * 60)
    
    try:
        # Install Node.js
        if not install_nodejs_wsl():
            print("\n❌ Node.js installation failed")
            return False
        
        # Configure npm
        if not configure_npm_global():
            print("\n❌ NPM configuration failed")
            return False
        
        # Install Claude Code
        if not install_claude_code_fresh():
            print("\n❌ Claude Code installation failed")
            return False
        
        # Final test
        if not final_test():
            print("\n❌ Final integration test failed")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 CLAUDE CODE INTEGRATION COMPLETE!")
        print("✅ Node.js 20.x LTS installed in WSL")
        print("✅ NPM configured for user packages")
        print("✅ Claude Code globally available")
        print("✅ Test environment ready")
        print("🚀 PHASE 2 COMPLETE - AI coding ready!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Installation error: {str(e)}")
        return False

if __name__ == "__main__":
    main()