#!/usr/bin/env python3
"""
Quick Docker availability test
"""

import sys
import traceback

def test_docker_availability():
    """Test if Docker is available and accessible"""
    print("=" * 50)
    print("Docker Orchestration MCP Server - Quick Test")
    print("=" * 50)
    
    # Test 1: Check if docker module can be imported
    print("\n1. Testing Docker Python module import...")
    try:
        import docker
        print("✓ Docker module imported successfully")
    except ImportError as e:
        print(f"✗ Docker module not found: {e}")
        print("  Run: pip install docker")
        return False
    
    # Test 2: Check Docker daemon connection
    print("\n2. Testing Docker daemon connection...")
    try:
        client = docker.from_env()
        client.ping()
        print("✓ Docker daemon connection successful")
    except Exception as e:
        print(f"✗ Docker daemon connection failed: {e}")
        print("  Make sure Docker Desktop is running")
        return False
    
    # Test 3: Get Docker system info
    print("\n3. Getting Docker system information...")
    try:
        info = client.info()
        print(f"✓ Docker version: {info.get('ServerVersion', 'unknown')}")
        print(f"✓ Total containers: {info.get('Containers', 0)}")
        print(f"✓ Running containers: {info.get('ContainersRunning', 0)}")
    except Exception as e:
        print(f"✗ Failed to get Docker info: {e}")
        return False
    
    # Test 4: Test basic container operation
    print("\n4. Testing basic container operations...")
    try:
        containers = client.containers.list(all=True)
        print(f"✓ Successfully listed containers: {len(containers)} total")
    except Exception as e:
        print(f"✗ Failed to list containers: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All Docker tests passed!")
    print("✓ Ready for MCP server development")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        success = test_docker_availability()
        if success:
            print("\nNext steps:")
            print("1. Run setup.bat to create virtual environment")
            print("2. Run test.bat to validate full setup")
            print("3. Start the MCP server with: python src/server.py")
        else:
            print("\nPlease fix the issues above before proceeding.")
            sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
