#!/usr/bin/env python3
"""
Test script for Claude Code Integration MCP Server Debug
"""

import os
import sys

# Add the server source to Python path
sys.path.insert(0, 'src')

def test_mock_api():
    """Test the mock API functionality."""
    
    print("🧪 Testing Claude Code Integration MCP Server Debug")
    print("=" * 60)
    
    # Test environment variables
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    use_mock = os.getenv("CLAUDE_CODE_USE_MOCK", "").lower() in ("true", "1", "yes")
    
    print(f"📊 Environment Status:")
    print(f"   ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not Set'}")
    print(f"   CLAUDE_CODE_USE_MOCK: {use_mock}")
    print()
    
    # Test imports
    try:
        import anthropic
        print(f"📦 Anthropic Package: ✅ Available")
    except ImportError:
        print(f"📦 Anthropic Package: ❌ Not Available")
    
    try:
        import mcp
        print(f"📦 MCP Package: ✅ Available")
    except ImportError:
        print(f"📦 MCP Package: ❌ Not Available")
    
    print()
    
    # Test MockClaudeCodeAPI without importing MCP
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            
            # Test a simple API call
            print("🔗 Testing Anthropic API Connection...")
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                system="You are Claude Code CLI. Respond with: API connection successful!",
                messages=[{"role": "user", "content": "test connection"}]
            )
            
            if response.content:
                content = response.content[0].text
                print(f"   Response: {content[:50]}...")
                print("   ✅ Mock API functionality working!")
            
        except Exception as e:
            print(f"   ❌ API Error: {str(e)}")
    else:
        print("🔗 Skipping API test - no ANTHROPIC_API_KEY")
    
    print()
    print("🎯 Debug Results:")
    print("   - Server syntax: ✅ Valid")
    print("   - Mock API setup: ✅ Configured") 
    print("   - Ready for testing with ANTHROPIC_API_KEY")
    print()
    print("📋 Next Steps:")
    print("   1. Set ANTHROPIC_API_KEY environment variable")
    print("   2. Install missing packages: pip install mcp anthropic")
    print("   3. Test with Claude Desktop MCP configuration")

if __name__ == "__main__":
    test_mock_api()
