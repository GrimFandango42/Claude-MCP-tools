#!/usr/bin/env python3
"""
MCP Servers Validation Test Suite
Comprehensive testing for all configured MCP servers
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

def test_server_startup(server_path, server_name):
    """Test if an MCP server can start up properly"""
    print(f"\n🔍 Testing {server_name} startup...")
    
    try:
        # Test server import and basic functionality
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            }
        }
        
        # Send request and wait for response
        stdout, stderr = process.communicate(
            input=json.dumps(init_request) + "\n", 
            timeout=10
        )
        
        if process.returncode == 0 or "protocolVersion" in stdout:
            print(f"✅ {server_name}: Server starts and responds to initialize")
            return True
        else:
            print(f"❌ {server_name}: Server failed to start properly")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"⏳ {server_name}: Server startup timed out")
        return False
    except Exception as e:
        print(f"❌ {server_name}: Exception during test: {str(e)}")
        return False

def test_docker_environment():
    """Test Docker environment readiness"""
    print("\n🐳 Testing Docker Environment...")
    
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
            
            # Test Docker daemon
            daemon_result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if daemon_result.returncode == 0:
                print("✅ Docker daemon is running")
                return True
            else:
                print("❌ Docker daemon is not running")
                return False
        else:
            print("❌ Docker is not installed or not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Docker test failed: {str(e)}")
        return False

def test_wsl_environment():
    """Test WSL environment for Computer Use"""
    print("\n🐧 Testing WSL Environment...")
    
    try:
        result = subprocess.run(
            ["wsl", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ WSL is installed and accessible")
            
            # Test basic WSL command
            bash_result = subprocess.run(
                ["wsl", "bash", "-c", "echo 'WSL test successful'"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if bash_result.returncode == 0:
                print("✅ WSL bash commands work properly")
                return True
            else:
                print("❌ WSL bash commands failed")
                return False
        else:
            print("❌ WSL is not installed or configured")
            return False
            
    except Exception as e:
        print(f"❌ WSL test failed: {str(e)}")
        return False

def test_python_dependencies():
    """Test Python dependencies for MCP servers"""
    print("\n🐍 Testing Python Dependencies...")
    
    required_packages = [
        ("mcp", "Model Context Protocol"),
        ("docker", "Docker SDK"),
        ("pyautogui", "GUI automation"),
        ("PIL", "Python Imaging Library"),
        ("requests", "HTTP library")
    ]
    
    all_good = True
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: {description} available")
        except ImportError:
            print(f"❌ {package}: {description} missing")
            all_good = False
    
    return all_good

def main():
    """Main test suite execution"""
    print("=" * 60)
    print("🚀 Claude MCP Tools - Comprehensive Test Suite")
    print("=" * 60)
    
    test_results = {}
    
    # Test Python dependencies
    test_results["python_deps"] = test_python_dependencies()
    
    # Test Docker environment
    test_results["docker"] = test_docker_environment()
    
    # Test WSL environment  
    test_results["wsl"] = test_wsl_environment()
    
    # Test MCP servers
    servers_to_test = [
        ("C:\\AI_Projects\\Claude-MCP-tools\\servers\\windows-computer-use\\server_mcp_framework.py", "Windows Computer Use"),
        ("C:\\AI_Projects\\Claude-MCP-tools\\servers\\docker-orchestration-mcp\\src\\server.py", "Docker Orchestration"),
        ("C:\\AI_Projects\\Claude-MCP-tools\\servers\\financial-mcp-server\\server.py", "Financial Datasets"),
        ("C:\\AI_Projects\\Claude-MCP-tools\\servers\\knowledge-memory-mcp\\server.py", "Knowledge Memory"),
        ("C:\\AI_Projects\\Claude-MCP-tools\\servers\\n8n-mcp-server\\server.py", "N8n Workflow")
    ]
    
    server_results = {}
    for server_path, server_name in servers_to_test:
        if Path(server_path).exists():
            server_results[server_name] = test_server_startup(server_path, server_name)
        else:
            print(f"❌ {server_name}: Server file not found at {server_path}")
            server_results[server_name] = False
    
    test_results["servers"] = server_results
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"\n🐍 Python Dependencies: {'✅ PASS' if test_results['python_deps'] else '❌ FAIL'}")
    print(f"🐳 Docker Environment: {'✅ PASS' if test_results['docker'] else '❌ FAIL'}")
    print(f"🐧 WSL Environment: {'✅ PASS' if test_results['wsl'] else '❌ FAIL'}")
    
    print(f"\n🔧 MCP Servers:")
    for server_name, result in server_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {server_name}: {status}")
    
    # Overall status
    all_passed = (
        test_results["python_deps"] and 
        test_results["docker"] and 
        test_results["wsl"] and 
        all(server_results.values())
    )
    
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL SYSTEMS READY' if all_passed else '⚠️ ISSUES FOUND'}")
    
    if all_passed:
        print("\n🚀 All tests passed! Your MCP servers are ready for use.")
        print("   Next step: Restart Claude Desktop and test the tools.")
    else:
        print("\n🔧 Some tests failed. Review the errors above and fix issues before proceeding.")
    
    print("\n" + "=" * 60)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
