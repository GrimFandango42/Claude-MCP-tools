#!/usr/bin/env python3
"""
Test script for API Gateway MCP Server
Validates all tools and provider integrations.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server import APIGatewayMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TestAPIGateway:
    """Test suite for the API Gateway MCP server."""
    
    def __init__(self):
        self.server = None
        self.passed = 0
        self.failed = 0
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
            
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    async def setup_server(self):
        """Initialize the server for testing."""
        try:
            # Set test environment variables if not present
            if not os.getenv("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = "test-key-placeholder"
                print("WARNING: Using placeholder OpenAI API key for testing")
                
            if not os.getenv("ANTHROPIC_API_KEY"):
                os.environ["ANTHROPIC_API_KEY"] = "test-key-placeholder"
                print("WARNING: Using placeholder Anthropic API key for testing")
            
            self.server = APIGatewayMCP()
            self.log_test_result("Server Initialization", True, "API Gateway server created successfully")
            return True
            
        except Exception as e:
            self.log_test_result("Server Initialization", False, f"Failed to initialize server: {e}")
            return False
    
    async def test_tool_registration(self):
        """Test that all tools are properly registered."""
        try:
            # Get list tools handler
            tools = None
            for handler_info in self.server.server._list_tools_handlers:
                handler = handler_info.handler
                tools = await handler()
                break
                
            if not tools:
                self.log_test_result("Tool Registration", False, "No tools found")
                return
                
            expected_tools = [
                "call_api",
                "list_providers", 
                "get_usage_stats",
                "estimate_cost",
                "manage_cache",
                "gateway_status"
            ]
            
            tool_names = [tool.name for tool in tools]
            
            missing_tools = [name for name in expected_tools if name not in tool_names]
            extra_tools = [name for name in tool_names if name not in expected_tools]
            
            if missing_tools:
                self.log_test_result("Tool Registration", False, f"Missing tools: {missing_tools}")
            elif extra_tools:
                self.log_test_result("Tool Registration", True, f"Extra tools found: {extra_tools}")
            else:
                self.log_test_result("Tool Registration", True, f"All {len(expected_tools)} tools registered")
                
        except Exception as e:
            self.log_test_result("Tool Registration", False, f"Tool registration test failed: {e}")
    
    async def test_provider_initialization(self):
        """Test provider initialization."""
        try:
            providers = self.server.providers
            
            if not providers:
                self.log_test_result("Provider Initialization", False, "No providers initialized")
                return
            
            # Test OpenAI provider
            if "openai" in providers:
                openai_provider = providers["openai"]
                info = openai_provider.get_provider_info()
                self.log_test_result("OpenAI Provider", True, f"Initialized with {len(info['available_models']['chat'])} chat models")
            else:
                self.log_test_result("OpenAI Provider", False, "OpenAI provider not found")
            
            # Test Anthropic provider
            if "anthropic" in providers:
                anthropic_provider = providers["anthropic"]
                info = anthropic_provider.get_provider_info()
                self.log_test_result("Anthropic Provider", True, f"Initialized with {len(info['available_models'])} models")
            else:
                self.log_test_result("Anthropic Provider", False, "Anthropic provider not found")
                
            self.log_test_result("Provider Initialization", True, f"Initialized {len(providers)} providers")
            
        except Exception as e:
            self.log_test_result("Provider Initialization", False, f"Provider initialization test failed: {e}")
    
    async def run_basic_tests(self):
        """Run basic test cases."""
        print("=" * 80)
        print("API Gateway MCP Server - Basic Test Suite")
        print("=" * 80)
        
        # Setup
        if not await self.setup_server():
            print("\n❌ Server setup failed - aborting tests")
            return False
        
        # Run basic tests
        print("\n📋 Running Basic Tests...")
        print("-" * 40)
        
        await self.test_tool_registration()
        await self.test_provider_initialization()
        
        # Results summary
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 80)
        
        success_rate = (self.passed / max(1, self.passed + self.failed)) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n✅ Basic tests passed! The API Gateway is ready for deployment.")
        else:
            print(f"\n⚠️  {self.failed} tests failed. Please fix the issues before deployment.")
        
        return self.failed == 0


async def main():
    """Run the test suite."""
    tester = TestAPIGateway()
    
    try:
        success = await tester.run_basic_tests()
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
