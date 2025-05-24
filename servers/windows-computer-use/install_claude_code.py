#!/usr/bin/env python3
"""
🚀 Claude Code Installation Script for WSL Ubuntu
Based on official Anthropic installation guide 2025
"""

import sys
import time
sys.path.append('.')
from server import ComputerUseAPI

def demo_header(title):
    """Print demo section header."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def install_claude_code():
    """Install Claude Code in WSL Ubuntu following official guide."""
    demo_header("CLAUDE CODE INSTALLATION - WSL UBUNTU")
    
    api = ComputerUseAPI()
    
    print("🔄 Step 1: System Update...")
    update_result = api.bash_20250124("sudo apt update && sudo apt upgrade -y")
    print(f"   ✅ System update: {update_result.get('exit_code') == 0}")
    
    print("\n🔄 Step 2: Install Node.js 20.x LTS...")
    nodejs_install = api.bash_20250124("""
        # Install Node.js 20.x (LTS) from NodeSource
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - &&
        sudo apt install -y nodejs &&
        echo "Installation complete" &&
        node --version &&
        npm --version
    """)
    print(f"   📦 Node.js installation: {nodejs_install.get('exit_code') == 0}")
    if nodejs_install.get('output'):
        print(f"   📋 Versions: {nodejs_install.get('output').strip()[-100:]}")
    
    print("\n🔄 Step 3: Configure npm for global packages...")
    npm_config = api.bash_20250124("""
        mkdir -p ~/.npm-global &&
        npm config set prefix ~/.npm-global &&
        echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc &&
        source ~/.bashrc &&
        echo "NPM configured for user directory"
    """)
    print(f"   ⚙️ NPM configuration: {npm_config.get('exit_code') == 0}")
    
    print("\n🔄 Step 4: Install additional dependencies...")
    deps_install = api.bash_20250124("sudo apt install -y git ripgrep")
    print(f"   🔧 Dependencies (git, ripgrep): {deps_install.get('exit_code') == 0}")
    
    print("\n🚀 Step 5: Install Claude Code...")
    claude_install = api.bash_20250124("""
        source ~/.bashrc &&
        npm install -g @anthropic-ai/claude-code &&
        echo "Claude Code installation complete"
    """)
    print(f"   🎯 Claude Code installation: {claude_install.get('exit_code') == 0}")
    if claude_install.get('output'):
        print(f"   📋 Output: {claude_install.get('output').strip()[-200:]}")
    
    print("\n🔍 Step 6: Verify installation...")
    verify_install = api.bash_20250124("""
        source ~/.bashrc &&
        which claude || echo "Claude not in PATH" &&
        node --version &&
        npm --version &&
        npm list -g @anthropic-ai/claude-code 2>/dev/null || echo "Checking installation..."
    """)
    print(f"   ✅ Verification: {verify_install.get('exit_code') == 0}")
    if verify_install.get('output'):
        print(f"   📊 Status: {verify_install.get('output').strip()}")
    
    return verify_install.get('exit_code') == 0

def test_claude_code():
    """Test Claude Code functionality."""
    demo_header("CLAUDE CODE FUNCTIONALITY TEST")
    
    api = ComputerUseAPI()
    
    print("🧪 Testing Claude Code command availability...")
    claude_test = api.bash_20250124("""
        source ~/.bashrc &&
        export PATH=~/.npm-global/bin:$PATH &&
        which claude && 
        echo "Claude Code is available" ||
        echo "Claude Code not found in PATH"
    """)
    
    if "available" in claude_test.get('output', ''):
        print("   ✅ Claude Code command found!")
        
        print("\n📝 Creating test project for Claude Code...")
        project_setup = api.bash_20250124("""
            cd ~ &&
            mkdir -p claude-code-test &&
            cd claude-code-test &&
            echo "# Claude Code Test Project" > README.md &&
            echo "console.log('Hello from Claude Code test!');" > test.js &&
            echo "def hello_world(): return 'Hello from Python!'" > test.py &&
            ls -la
        """)
        print(f"   📁 Test project created: {project_setup.get('exit_code') == 0}")
        
        print("\n🎯 Claude Code is ready for authentication!")
        print("   ℹ️  To start Claude Code: cd ~/claude-code-test && claude")
        print("   ℹ️  First run will prompt for Anthropic API authentication")
        
        return True
    else:
        print("   ❌ Claude Code not found. Installation may have failed.")
        print(f"   🔍 Debug info: {claude_test.get('output', '')}")
        return False

def show_usage_guide():
    """Show Claude Code usage guide."""
    demo_header("CLAUDE CODE USAGE GUIDE")
    
    print("🎯 How to use Claude Code in your development workflow:")
    print()
    print("📍 Starting Claude Code:")
    print("   cd your-project-directory")
    print("   claude")
    print()
    print("🔐 First-time setup:")
    print("   • OAuth authentication with Anthropic account")
    print("   • Terminal style selection")
    print("   • API key configuration")
    print()
    print("💡 Key features:")
    print("   • Natural language code generation")
    print("   • Codebase understanding and analysis")
    print("   • Git workflow integration")
    print("   • Debugging assistance")
    print("   • Code editing and refactoring")
    print()
    print("🚀 Integration with Computer Use API:")
    print("   • Use bash_20250124 tool to run Claude Code commands")
    print("   • Combine with screenshot/automation for VS Code integration")
    print("   • Create automated development workflows")

def main():
    """Main Claude Code installation process."""
    print("🚀 CLAUDE CODE INSTALLATION FOR WSL UBUNTU")
    print("🎯 Following official Anthropic installation guide 2025")
    print("=" * 60)
    
    try:
        # Install Claude Code
        success = install_claude_code()
        
        if success:
            # Test installation
            test_success = test_claude_code()
            
            if test_success:
                show_usage_guide()
                
                print(f"\n{'='*60}")
                print("🎉 CLAUDE CODE INSTALLATION COMPLETE!")
                print("✅ Node.js 20.x LTS installed")
                print("✅ NPM configured for user directory")
                print("✅ Claude Code installed globally")
                print("✅ Dependencies (git, ripgrep) ready")
                print("🚀 Ready for AI-powered coding in WSL!")
                print(f"{'='*60}")
                
                return True
            else:
                print("\n❌ Claude Code installation verification failed")
                return False
        else:
            print("\n❌ Claude Code installation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Installation error: {str(e)}")
        return False

if __name__ == "__main__":
    main()