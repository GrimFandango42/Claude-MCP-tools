#!/usr/bin/env python3
"""
🔧 Node.js Debug Installation - Multiple Methods
Try different approaches to get Node.js working in WSL
"""

import sys
sys.path.append('.')
from server import ComputerUseAPI

def try_method_1_nodesource():
    """Method 1: NodeSource repository (official)"""
    print("🔧 Method 1: NodeSource Official Repository")
    
    api = ComputerUseAPI()
    
    # Clean setup
    clean_result = api.bash_20250124("""
        sudo apt update &&
        sudo apt install -y curl ca-certificates gnupg
    """)
    print(f"   Prerequisites: {'✅' if clean_result.get('exit_code') == 0 else '❌'}")
    
    # Add NodeSource repo
    repo_result = api.bash_20250124("""
        curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/nodesource.gpg &&
        echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x jammy main" | sudo tee /etc/apt/sources.list.d/nodesource.list &&
        sudo apt update
    """)
    print(f"   Repository setup: {'✅' if repo_result.get('exit_code') == 0 else '❌'}")
    
    # Install Node.js
    install_result = api.bash_20250124("sudo apt install -y nodejs")
    print(f"   Node.js install: {'✅' if install_result.get('exit_code') == 0 else '❌'}")
    
    # Test
    test_result = api.bash_20250124("node --version && npm --version")
    if test_result.get('exit_code') == 0:
        print(f"   ✅ SUCCESS: {test_result.get('output', '').strip()}")
        return True
    else:
        print(f"   ❌ Failed: {test_result.get('output', '')}")
        return False

def try_method_2_snap():
    """Method 2: Snap package"""
    print("\n🔧 Method 2: Snap Package Manager")
    
    api = ComputerUseAPI()
    
    # Check if snap is available
    snap_check = api.bash_20250124("which snap || echo 'Snap not available'")
    if 'not available' in snap_check.get('output', ''):
        print("   ❌ Snap not available in this WSL")
        return False
    
    # Install via snap
    install_result = api.bash_20250124("sudo snap install node --classic")
    print(f"   Snap install: {'✅' if install_result.get('exit_code') == 0 else '❌'}")
    
    # Test
    test_result = api.bash_20250124("node --version && npm --version")
    if test_result.get('exit_code') == 0:
        print(f"   ✅ SUCCESS: {test_result.get('output', '').strip()}")
        return True
    else:
        print(f"   ❌ Failed: {test_result.get('output', '')}")
        return False

def try_method_3_nvm():
    """Method 3: NVM (Node Version Manager)"""
    print("\n🔧 Method 3: NVM Installation")
    
    api = ComputerUseAPI()
    
    # Install NVM
    nvm_install = api.bash_20250124("""
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash &&
        export NVM_DIR="$HOME/.nvm" &&
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" &&
        nvm --version
    """)
    print(f"   NVM install: {'✅' if nvm_install.get('exit_code') == 0 else '❌'}")
    
    if nvm_install.get('exit_code') == 0:
        # Install Node via NVM
        node_install = api.bash_20250124("""
            export NVM_DIR="$HOME/.nvm" &&
            [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" &&
            nvm install 20 &&
            nvm use 20 &&
            node --version && npm --version
        """)
        
        if node_install.get('exit_code') == 0:
            print(f"   ✅ SUCCESS: {node_install.get('output', '').strip()}")
            
            # Add to bashrc
            bashrc_update = api.bash_20250124("""
                echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc &&
                echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"' >> ~/.bashrc &&
                echo '[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"' >> ~/.bashrc
            """)
            print(f"   Bashrc update: {'✅' if bashrc_update.get('exit_code') == 0 else '❌'}")
            return True
        else:
            print(f"   ❌ Node install failed: {node_install.get('output', '')}")
            return False
    else:
        print(f"   ❌ NVM install failed")
        return False

def try_method_4_binary():
    """Method 4: Direct binary download"""
    print("\n🔧 Method 4: Direct Binary Download")
    
    api = ComputerUseAPI()
    
    # Download and install Node.js binary
    binary_install = api.bash_20250124("""
        cd /tmp &&
        wget https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz &&
        tar -xf node-v20.11.0-linux-x64.tar.xz &&
        sudo cp -r node-v20.11.0-linux-x64/* /usr/local/ &&
        /usr/local/bin/node --version && /usr/local/bin/npm --version
    """)
    
    if binary_install.get('exit_code') == 0:
        print(f"   ✅ SUCCESS: {binary_install.get('output', '').strip()}")
        
        # Add to PATH
        path_update = api.bash_20250124("""
            echo 'export PATH=/usr/local/bin:$PATH' >> ~/.bashrc &&
            source ~/.bashrc &&
            node --version
        """)
        print(f"   PATH update: {'✅' if path_update.get('exit_code') == 0 else '❌'}")
        return True
    else:
        print(f"   ❌ Binary install failed: {binary_install.get('output', '')}")
        return False

def install_claude_code_once_node_works():
    """Install Claude Code after Node.js is working"""
    print("\n🎯 Installing Claude Code...")
    
    api = ComputerUseAPI()
    
    # Setup npm global directory
    npm_setup = api.bash_20250124("""
        mkdir -p ~/.npm-global &&
        npm config set prefix ~/.npm-global &&
        echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    """)
    print(f"   NPM setup: {'✅' if npm_setup.get('exit_code') == 0 else '❌'}")
    
    # Install Claude Code
    claude_install = api.bash_20250124("""
        source ~/.bashrc &&
        export PATH=~/.npm-global/bin:$PATH &&
        npm install -g @anthropic-ai/claude-code
    """)
    print(f"   Claude install: {'✅' if claude_install.get('exit_code') == 0 else '❌'}")
    
    # Verify
    verify_result = api.bash_20250124("""
        source ~/.bashrc &&
        export PATH=~/.npm-global/bin:$PATH &&
        which claude && echo "Claude Code ready!"
    """)
    
    if 'ready' in verify_result.get('output', ''):
        print("   ✅ Claude Code verified and ready!")
        return True
    else:
        print(f"   ❌ Claude verification failed: {verify_result.get('output', '')}")
        return False

def main():
    """Try all methods until one works"""
    print("🚀 NODE.JS INSTALLATION - MULTIPLE METHODS")
    print("🎯 Trying different approaches until we find one that works")
    print("=" * 60)
    
    methods = [
        try_method_1_nodesource,
        try_method_2_snap, 
        try_method_3_nvm,
        try_method_4_binary
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            if method():
                print(f"\n🎉 SUCCESS with Method {i}!")
                
                # Install Claude Code
                if install_claude_code_once_node_works():
                    print("\n" + "=" * 60)
                    print("🎉 CLAUDE CODE INSTALLATION COMPLETE!")
                    print("✅ Node.js working in WSL")
                    print("✅ NPM configured properly") 
                    print("✅ Claude Code globally installed")
                    print("🚀 Ready for AI-powered development!")
                    
                    # Create test project
                    api = ComputerUseAPI()
                    test_project = api.bash_20250124("""
                        cd ~ &&
                        mkdir -p claude-code-ready &&
                        cd claude-code-ready &&
                        echo "# Claude Code Test Project" > README.md &&
                        echo "console.log('Hello Claude!');" > test.js &&
                        echo "Project ready for Claude Code!"
                    """)
                    
                    print("\n📍 To start using Claude Code:")
                    print("   cd ~/claude-code-ready")
                    print("   source ~/.bashrc")
                    print("   claude")
                    print("\n🔐 First run will prompt for Anthropic authentication")
                    print("=" * 60)
                    return True
                else:
                    print("\n❌ Claude Code installation failed")
                    continue
            else:
                print(f"   Method {i} failed, trying next...")
                continue
                
        except Exception as e:
            print(f"   Method {i} error: {str(e)}")
            continue
    
    print("\n❌ All methods failed. Let's try alternative approach...")
    return False

if __name__ == "__main__":
    main()