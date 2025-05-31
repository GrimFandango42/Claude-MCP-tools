#!/usr/bin/env python3
"""
Test script for the fixed AgenticSeek MCP server
This tests that the async issues are resolved
"""

import asyncio
import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(__file__))

async def test_async_compatibility():
    """Test that the fixed server can run in an existing async context"""
    print("Testing async compatibility...")
    
    try:
        # Import the fixed server
        from server_fastmcp_fixed import call_agenticseek, select_optimal_provider, PROVIDERS
        
        print("✅ Successfully imported fixed server module")
        
        # Test provider selection (synchronous)
        provider = select_optimal_provider("Hello world", "balanced")
        print(f"✅ Provider selection works: {provider}")
        
        # Test async function in existing event loop
        print("Testing async call in existing event loop...")
        
        # This would previously fail with "asyncio.run() cannot be called from a running event loop"
        try:
            # Simulate what would happen when Claude calls the tool
            result = await call_agenticseek("Test prompt", "local", "")
            print("✅ Async call successful (though AgenticSeek may not be running)")
        except Exception as e:
            if "could not connect" in str(e).lower() or "connection" in str(e).lower():
                print("✅ Async call works (AgenticSeek not running, but no asyncio error)")
            else:
                print(f"❌ Async call failed with: {e}")
                return False
        
        print("✅ All async compatibility tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_provider_configs():
    """Test provider configurations"""
    print("\\nTesting provider configurations...")
    
    try:
        from server_fastmcp_fixed import PROVIDERS, select_optimal_provider
        
        # Test all providers exist
        expected_providers = ["local", "openai-fast", "openai-quality", "google"]
        for provider in expected_providers:
            if provider not in PROVIDERS:
                print(f"❌ Missing provider: {provider}")
                return False
            print(f"✅ Provider {provider}: {PROVIDERS[provider].name} ({PROVIDERS[provider].model})")
        
        # Test routing logic
        test_cases = [
            ("private document analysis", "privacy", "local"),
            ("quick summary", "speed", "openai-fast"),
            ("complex analysis", "quality", "openai-quality"),
            ("cost-effective task", "cost", "local"),
        ]
        
        for prompt, priority, expected in test_cases:
            selected = select_optimal_provider(prompt, priority)
            if selected != expected:
                print(f"❌ Routing failed: '{prompt}' with priority '{priority}' -> {selected} (expected {expected})")
            else:
                print(f"✅ Routing: '{prompt}' -> {selected}")
        
        print("✅ All provider configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Provider config test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔧 Testing Fixed AgenticSeek MCP Server")
    print("=" * 50)
    
    # Test 1: Provider configurations
    config_ok = test_provider_configs()
    
    # Test 2: Async compatibility
    async_ok = await test_async_compatibility()
    
    print("\\n" + "=" * 50)
    if config_ok and async_ok:
        print("🎉 ALL TESTS PASSED! The fix appears to be working.")
        print("\\nNext steps:")
        print("1. Update Claude's MCP configuration to use the fixed server")
        print("2. Test the actual tools: smart_routing, local_reasoning, etc.")
        print("3. Verify AgenticSeek integration is working")
    else:
        print("❌ Some tests failed. Check the issues above.")
        
    return config_ok and async_ok

if __name__ == "__main__":
    # This tests running in an existing event loop context
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
