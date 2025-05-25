#!/usr/bin/env python3
"""
Quick test script for Docker Orchestration MCP Server
Tests server initialization and basic functionality
"""

import os
import sys
import subprocess
import docker
import asyncio
import json

def test_docker_connection():
    """Test Docker daemon connection"""
    print("Testing Docker connection...")
    try:
        client = docker.from_env()
        client.ping()
        info = client.info()
        print(f"✅ Docker connection successful")
        print(f"   Server Version: {info.get('ServerVersion')}")
        print(f"   Containers: {info.get('Containers', 0)}")
        return True
    except Exception as e:
        print(f"❌ Docker connection failed: {e}")
        return False

def test_server_startup():
    """Test server startup"""
    print("\nTesting server startup...")
    
    # Change to server directory
    server_dir = os.path.dirname(__file__)
    os.chdir(server_dir)
    
    # Test import of server module
    try:
        sys.path.insert(0, os.path.join(server_dir, 'src'))
        from server import DockerOrchestrationServer
        print("✅ Server module imports successfully")
        
        # Test server initialization
        server = DockerOrchestrationServer()
        print("✅ Server initializes successfully")
        print(f"   Deployment history: {len(server.deployment_history)} entries")
        
        return True
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    
    required_packages = ['docker', 'mcp', 'asyncio']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError as e:
            print(f"❌ {package} missing: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("Docker Orchestration MCP Server - Startup Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test dependencies
    if not test_dependencies():
        all_tests_passed = False
    
    # Test Docker connection
    if not test_docker_connection():
        all_tests_passed = False
    
    # Test server startup
    if not test_server_startup():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Docker server is ready.")
        print("\nTo launch the server:")
        print("   1. Run: launch_fixed.bat")
        print("   2. Or run: python src/server.py")
    else:
        print("❌ Some tests failed. Please fix issues before launching.")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())
