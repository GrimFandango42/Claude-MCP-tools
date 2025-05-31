#!/usr/bin/env python3
"""
Test script for Enhanced Claude Code Integration MCP Server
This script tests the basic functionality and Claude Code CLI integration
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_claude_code_availability():
    """Test if Claude Code CLI is available"""
    print("🔍 Testing Claude Code CLI availability...")
    try:
        result = subprocess.run(
            ["claude-code", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Claude Code CLI is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Claude Code CLI returned error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Claude Code CLI not found in PATH")
        print("💡 Please install Claude Code CLI: https://docs.anthropic.com/en/docs/claude-code")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_mcp_server_import():
    """Test if the MCP server can be imported and initialized"""
    print("\n🔍 Testing MCP server import and initialization...")
    try:
        # Change to the server directory
        import os
        os.chdir(Path(__file__).parent)
        
        # Import the server module
        import enhanced_server
        
        print("✅ MCP server imported successfully")
        print(f"✅ Claude Code availability check: {enhanced_server.claude_code_mcp.claude_code_available}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import MCP server: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {str(e)}")
        return False

def test_basic_functionality():
    """Test basic MCP server functionality"""
    print("\n🔍 Testing basic MCP server functionality...")
    try:
        import enhanced_server
        
        # Test system status
        print("📊 Getting system status...")
        status = enhanced_server.get_system_status()
        print(f"System status: {json.dumps(status, indent=2)}")
        
        # Test project analysis with current directory
        current_dir = str(Path.cwd())
        print(f"\n📁 Analyzing current project: {current_dir}")
        analysis = enhanced_server.analyze_project(current_dir)
        print(f"Project analysis: {json.dumps(analysis, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ Error during functionality test: {str(e)}")
        return False

def test_claude_code_integration():
    """Test actual Claude Code CLI integration"""
    print("\n🔍 Testing Claude Code CLI integration...")
    try:
        # Test with a simple query using --print flag for non-interactive mode
        test_query = "What is the current directory structure?"
        
        print(f"🤖 Testing Claude Code with query: '{test_query}'")
        result = subprocess.run(
            ["claude-code", "--print", test_query],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print("✅ Claude Code CLI executed successfully")
            print(f"📝 Response length: {len(result.stdout)} characters")
            if result.stdout:
                print(f"📝 Response preview: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ Claude Code CLI failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Claude Code CLI timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude Code integration: {str(e)}")
        return False

def test_mcp_tool_execution():
    """Test MCP tool execution through the server"""
    print("\n🔍 Testing MCP tool execution...")
    try:
        import enhanced_server
        
        # Test the check_claude_code_availability tool
        print("🛠️ Testing check_claude_code_availability tool...")
        availability_result = enhanced_server.check_claude_code_availability()
        print(f"Availability check result: {json.dumps(availability_result, indent=2)}")
        
        # Test analyzing the current project
        current_dir = str(Path.cwd())
        print(f"\n🛠️ Testing analyze_project tool with: {current_dir}")
        analysis_result = enhanced_server.analyze_project(current_dir)
        print(f"Analysis result: {json.dumps(analysis_result, indent=2)}")
        
        # Test setting active project
        print(f"\n🛠️ Testing set_active_project tool...")
        set_project_result = enhanced_server.set_active_project(current_dir)
        print(f"Set project result: {json.dumps(set_project_result, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ Error during MCP tool testing: {str(e)}")
        return False

def test_task_delegation():
    """Test task delegation functionality"""
    print("\n🔍 Testing task delegation functionality...")
    try:
        import enhanced_server
        
        # First ensure we have an active project
        current_dir = str(Path.cwd())
        enhanced_server.set_active_project(current_dir)
        
        # Test delegating a simple task
        test_task = "List the files in the current directory and provide a brief summary"
        print(f"📋 Delegating test task: '{test_task}'")
        
        delegation_result = enhanced_server.delegate_coding_task(
            task_description=test_task,
            priority="normal",
            tags=["test", "integration"]
        )
        
        print(f"Delegation result: {json.dumps(delegation_result, indent=2)}")
        
        if delegation_result.get("success"):
            task_id = delegation_result.get("task_id")
            print(f"✅ Task delegated successfully with ID: {task_id}")
            
            # Wait a moment and check progress
            print("⏳ Waiting 3 seconds before checking progress...")
            time.sleep(3)
            
            progress_result = enhanced_server.monitor_task_progress(task_id)
            print(f"Progress check: {json.dumps(progress_result, indent=2)}")
            
            return True
        else:
            print(f"❌ Task delegation failed: {delegation_result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during task delegation test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Claude Code Integration MCP Server Test Suite")
    print("=" * 60)
    
    tests = [
        ("Claude Code CLI Availability", test_claude_code_availability),
        ("MCP Server Import", test_mcp_server_import),
        ("Basic Functionality", test_basic_functionality),
        ("Claude Code Integration", test_claude_code_integration),
        ("MCP Tool Execution", test_mcp_tool_execution),
        ("Task Delegation", test_task_delegation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🏆 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The Enhanced Claude Code Integration MCP is ready for deployment.")
    elif passed > len(results) // 2:
        print("⚠️  Most tests passed. Some issues may need attention before deployment.")
    else:
        print("🚨 Multiple tests failed. Please review the setup and dependencies.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
