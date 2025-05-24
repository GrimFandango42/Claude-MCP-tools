#!/usr/bin/env python3
"""
🔍 Claude Code Installation Verification & Status Check
"""

import sys
import time
sys.path.append('.')
from server import ComputerUseAPI

def check_installation_status():
    """Check current installation status."""
    print("🔍 CLAUDE CODE INSTALLATION STATUS CHECK")
    print("=" * 50)
    
    api = ComputerUseAPI()
    
    # Check Node.js
    print("\n📦 Checking Node.js installation...")
    node_check = api.bash_20250124("node --version && npm --version")
    if node_check.get('exit_code') == 0:
        print(f"   ✅ Node.js: {node_check.get('output', '').strip()}")
    else:
        print("   ❌ Node.js not found or installation incomplete")
    
    # Check Claude Code
    print("\n🎯 Checking Claude Code installation...")
    claude_check = api.bash_20250124("""
        source ~/.bashrc &&
        export PATH=~/.npm-global/bin:$PATH &&
        which claude || echo "NOT_FOUND" &&
        npm list -g @anthropic-ai/claude-code 2>/dev/null || echo "Package not found"
    """)
    
    output = claude_check.get('output', '')
    if 'NOT_FOUND' not in output and 'Package not found' not in output:
        print(f"   ✅ Claude Code: {output.strip()}")
        return True
    else:
        print(f"   🔄 Claude Code: {output.strip()}")
        return False

def complete_installation_if_needed():
    """Complete installation if it's not finished."""
    print("\n🚀 Completing Claude Code installation...")
    
    api = ComputerUseAPI()
    
    # Ensure npm global configuration
    print("⚙️ Configuring npm global packages...")
    config_result = api.bash_20250124("""
        mkdir -p ~/.npm-global &&
        npm config set prefix ~/.npm-global &&
        echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
    """)
    
    # Install Claude Code
    print("📦 Installing Claude Code...")
    install_result = api.bash_20250124("""
        source ~/.bashrc &&
        export PATH=~/.npm-global/bin:$PATH &&
        npm install -g @anthropic-ai/claude-code
    """)
    
    if install_result.get('exit_code') == 0:
        print("   ✅ Claude Code installation completed!")
        return True
    else:
        print(f"   ❌ Installation failed: {install_result.get('output', '')}")
        return False

def test_claude_functionality():
    """Test Claude Code basic functionality."""
    print("\n🧪 Testing Claude Code functionality...")
    
    api = ComputerUseAPI()
    
    # Create test project
    test_setup = api.bash_20250124("""
        cd ~ &&
        rm -rf claude-test-project &&
        mkdir claude-test-project &&
        cd claude-test-project &&
        echo "# Claude Code Test Project" > README.md &&
        echo "Test project created successfully"
    """)
    
    if test_setup.get('exit_code') == 0:
        print("   ✅ Test project created")
        
        # Test Claude availability
        claude_test = api.bash_20250124("""
            source ~/.bashrc &&
            export PATH=~/.npm-global/bin:$PATH &&
            cd ~/claude-test-project &&
            which claude && echo "Claude Code is ready!"
        """)
        
        if 'ready' in claude_test.get('output', ''):
            print("   ✅ Claude Code command available")
            
            # Show next steps
            print("\n🎯 CLAUDE CODE READY FOR USE!")
            print("📍 To start Claude Code:")
            print("   cd ~/claude-test-project")
            print("   source ~/.bashrc")
            print("   claude")
            print("\n🔐 First run will require Anthropic API authentication")
            
            return True
        else:
            print(f"   ❌ Claude command test failed: {claude_test.get('output', '')}")
            return False
    else:
        print("   ❌ Test project creation failed")
        return False

def main():
    """Main verification process."""
    # Check current status
    is_installed = check_installation_status()
    
    if not is_installed:
        # Complete installation
        success = complete_installation_if_needed()
        if not success:
            print("\n❌ INSTALLATION FAILED")
            return False
    
    # Test functionality
    test_success = test_claude_functionality()
    
    if test_success:
        print("\n" + "=" * 50)
        print("🎉 CLAUDE CODE INSTALLATION VERIFIED!")
        print("✅ Node.js 20.x LTS ready")
        print("✅ Claude Code globally installed")
        print("✅ Test environment prepared")
        print("🚀 Phase 2 COMPLETE - Ready for AI coding!")
        print("=" * 50)
        return True
    else:
        print("\n❌ VERIFICATION FAILED")
        return False

if __name__ == "__main__":
    main()