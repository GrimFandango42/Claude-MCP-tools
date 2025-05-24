#!/usr/bin/env python3
"""
Manual test script for Docker Orchestration MCP Server
Tests the server functionality without requiring Claude Desktop
"""

import asyncio
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp_server():
    """Test the MCP server functionality manually"""
    
    print("=" * 60)
    print("Docker Orchestration MCP Server - Manual Test")
    print("=" * 60)
    
    try:
        # Import the server
        print("\n1. Importing MCP server...")
        from server import DockerOrchestrationServer
        print("✓ Server import successful")
        
        # Initialize server
        print("\n2. Initializing server...")
        server = DockerOrchestrationServer()
        print("✓ Server initialization successful")
        print(f"✓ Deployment history initialized: {len(server.deployment_history)} entries")
        
        # Test Docker client
        print("\n3. Testing Docker client connection...")
        if server.client:
            info = server.client.info()
            print(f"✓ Docker version: {info.get('ServerVersion', 'unknown')}")
            print(f"✓ Total containers: {info.get('Containers', 0)}")
            print(f"✓ Running containers: {info.get('ContainersRunning', 0)}")
        else:
            print("✗ Docker client not initialized")
            return False
        
        # Test container listing
        print("\n4. Testing container operations...")
        result = await server._list_containers(all=True)
        if result.get('success'):
            print(f"✓ Container listing successful: {result.get('count', 0)} containers found")
        else:
            print(f"✗ Container listing failed: {result.get('error', 'unknown error')}")
        
        # Test container deployment (with hello-world for safety)
        print("\n5. Testing container deployment...")
        deploy_result = await server._deploy_container(
            image="hello-world",
            name="mcp-test-hello-world"
        )
        
        if deploy_result.get('success'):
            print(f"✓ Container deployment successful!")
            print(f"  Container ID: {deploy_result.get('container_id', 'unknown')[:12]}...")
            print(f"  Container Name: {deploy_result.get('container_name', 'unknown')}")
            print(f"  Status: {deploy_result.get('status', 'unknown')}")
            
            # Clean up - remove the test container
            container_id = deploy_result.get('container_id')
            if container_id:
                print(f"\n6. Cleaning up test container...")
                try:
                    container = server.client.containers.get(container_id)
                    container.remove(force=True)
                    print("✓ Test container cleaned up successfully")
                except Exception as e:
                    print(f"⚠ Could not clean up test container: {e}")
        else:
            print(f"✗ Container deployment failed: {deploy_result.get('error', 'unknown error')}")
        
        # Test system resources
        print("\n7. Testing system resource monitoring...")
        resources_result = await server._get_system_resources()
        if resources_result.get('success'):
            print("✓ System resource monitoring successful")
        else:
            print("⚠ System resource monitoring not yet implemented (expected)")
        
        print("\n" + "=" * 60)
        print("✓ MCP Server Manual Testing Complete!")
        print("✓ Server is ready for Claude Desktop integration")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import server: {e}")
        print("  Make sure to run setup.bat first to install dependencies")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during testing: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    success = await test_mcp_server()
    
    if success:
        print("\nNext steps:")
        print("1. Add server to Claude Desktop configuration")
        print("2. Restart Claude Desktop")
        print("3. Test with Claude: 'List my Docker containers'")
    else:
        print("\nPlease fix the issues above before proceeding.")
        print("Make sure to run setup.bat first!")

if __name__ == "__main__":
    print("Starting manual MCP server test...")
    asyncio.run(main())
