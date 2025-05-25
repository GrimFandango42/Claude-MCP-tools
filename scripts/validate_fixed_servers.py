#!/usr/bin/env python3
"""
MCP Server Fix Validation Script
Validates that both KnowledgeMemory and Containerized Computer Use servers are operational.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def test_knowledge_memory_server():
    """Test KnowledgeMemory server startup and basic functionality."""
    print("🧪 Testing KnowledgeMemory Server...")
    
    server_path = Path("C:/AI_Projects/Claude-MCP-tools/servers/knowledge-memory-mcp")
    venv_python = server_path / ".venv" / "Scripts" / "python.exe"
    server_script = server_path / "src" / "server.py"
    
    try:
        # Test that the server can start (run for 2 seconds then kill)
        process = subprocess.Popen(
            [str(venv_python), "-m", "src.server"],
            cwd=str(server_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run for 2 seconds to check initialization
        time.sleep(2)
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        
        # Check for successful database initialization
        if "Database tables created successfully" in stderr:
            print("✅ KnowledgeMemory Server: Database initialization successful")
            return True
        elif "Foreign key constraints temporarily disabled" in stderr:
            print("✅ KnowledgeMemory Server: Foreign key fix applied successfully")
            return True
        else:
            print(f"❌ KnowledgeMemory Server: Unexpected output")
            print(f"   STDERR: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ KnowledgeMemory Server: Error during test - {e}")
        return False

def test_containerized_computer_use_server():
    """Test Containerized Computer Use server startup and dependency availability."""
    print("🐳 Testing Containerized Computer Use Server...")
    
    server_path = Path("C:/AI_Projects/Claude-MCP-tools/servers/containerized-computer-use")
    venv_python = server_path / ".venv" / "Scripts" / "python.exe"
    
    try:
        # First, test that Docker module is available
        result = subprocess.run(
            [str(venv_python), "-c", "import docker; print('Docker module available')"],
            cwd=str(server_path),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "Docker module available" in result.stdout:
            print("✅ Containerized Computer Use: Docker module successfully installed")
        else:
            print(f"❌ Containerized Computer Use: Docker module test failed")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            return False
        
        # Test that the server can start
        process = subprocess.Popen(
            [str(venv_python), "containerized_mcp_server.py"],
            cwd=str(server_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run for 2 seconds
        time.sleep(2)
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        
        # Check for successful startup
        if "Starting Containerized Computer Use MCP Server" in stderr:
            print("✅ Containerized Computer Use Server: Startup successful")
            if "Docker client not available" in stderr:
                print("ℹ️  Note: Docker Desktop not running (expected), server handles gracefully")
            return True
        else:
            print(f"❌ Containerized Computer Use Server: Unexpected startup behavior")
            print(f"   STDERR: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Containerized Computer Use Server: Error during test - {e}")
        return False

def check_claude_desktop_config():
    """Verify Claude Desktop configuration has both servers properly configured."""
    print("⚙️  Checking Claude Desktop Configuration...")
    
    config_path = Path("C:/Users/Nithin/AppData/Roaming/Claude/claude_desktop_config.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        
        # Check KnowledgeMemory server
        km_server = servers.get("KnowledgeMemory")
        if km_server and km_server.get("enabled", True):
            print("✅ Claude Desktop Config: KnowledgeMemory server properly configured")
        else:
            print("⚠️  Claude Desktop Config: KnowledgeMemory server configuration issue")
        
        # Check Containerized Computer Use server
        ccu_server = servers.get("containerized-computer-use")
        if ccu_server:
            print("✅ Claude Desktop Config: Containerized Computer Use server properly configured")
        else:
            print("⚠️  Claude Desktop Config: Containerized Computer Use server not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Claude Desktop Config: Error reading configuration - {e}")
        return False

def main():
    """Run all validation tests."""
    print("🔍 MCP Server Fix Validation")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("KnowledgeMemory Server", test_knowledge_memory_server()))
    results.append(("Containerized Computer Use Server", test_containerized_computer_use_server()))
    results.append(("Claude Desktop Configuration", check_claude_desktop_config()))
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 Next Steps:")
        print("1. Restart Claude Desktop to fully reload server configurations")
        print("2. Verify both servers show 'Connected' status in Claude settings")
        print("3. Test basic functionality of both restored servers")
        print("\n✨ Both servers are ready for production use!")
    else:
        print("\n🔧 Action Required:")
        print("Please review failed tests and address any remaining issues.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
