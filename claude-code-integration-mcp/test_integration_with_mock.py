#!/usr/bin/env python3
"""
Test Claude Code Integration MCP Server with Mock CLI
This tests the full integration workflow using a simulated Claude Code CLI
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

def create_mock_claude_code_cli():
    """Create a mock claude-code CLI for testing"""
    mock_script = '''#!/bin/bash
# Mock Claude Code CLI for testing
case "$1" in
    --version)
        echo "claude-code v1.0.0-mock"
        exit 0
        ;;
    --task)
        echo "Mock Claude Code: Processing task '$2'"
        echo "Project: $4"
        echo "Mock task execution completed successfully"
        exit 0
        ;;
    *)
        echo "Mock Claude Code CLI - Usage: claude-code [--version] [--task TASK --project PATH]"
        exit 1
        ;;
esac
'''
    
    # Create mock CLI in a temporary location
    mock_path = "/tmp/claude-code"
    with open(mock_path, 'w') as f:
        f.write(mock_script)
    
    os.chmod(mock_path, 0o755)
    
    # Add to PATH temporarily
    os.environ['PATH'] = f"/tmp:{os.environ['PATH']}"
    
    return mock_path

def test_enhanced_server_with_mock():
    """Test the enhanced server with mock Claude Code CLI"""
    print("🧪 Testing Claude Code Integration MCP Server with Mock CLI")
    print("=" * 60)
    
    # Create mock CLI
    mock_path = create_mock_claude_code_cli()
    print(f"✅ Created mock Claude Code CLI at: {mock_path}")
    
    # Test CLI availability
    try:
        result = subprocess.run(['claude-code', '--version'], capture_output=True, text=True)
        print(f"✅ Mock CLI test: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Mock CLI test failed: {e}")
        return False
    
    # Test the enhanced server tools
    print("\n🔧 Testing Enhanced Server Tools:")
    
    # Import and initialize the server components
    sys.path.append('/mnt/c/AI_Projects/Claude-MCP-tools/claude-code-integration-mcp')
    
    try:
        from enhanced_server import (
            claude_code_mcp, 
            check_claude_code_availability,
            analyze_project,
            set_active_project,
            delegate_coding_task,
            get_system_status
        )
        
        print("✅ Successfully imported server components")
        
        # Test 1: Check Claude Code availability
        print("\n1️⃣ Testing Claude Code availability check:")
        availability = check_claude_code_availability()
        print(f"   Result: {json.dumps(availability, indent=2)}")
        
        # Test 2: Create test project
        test_project_path = "/tmp/test_project"
        os.makedirs(test_project_path, exist_ok=True)
        
        # Create a simple Python project structure
        with open(f"{test_project_path}/requirements.txt", 'w') as f:
            f.write("requests>=2.25.0\nflask>=2.0.0\n")
        
        with open(f"{test_project_path}/main.py", 'w') as f:
            f.write("""
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
""")
        
        print(f"\n2️⃣ Testing project analysis for: {test_project_path}")
        analysis = analyze_project(test_project_path)
        print(f"   Result: {json.dumps(analysis, indent=2)}")
        
        # Test 3: Set active project
        print(f"\n3️⃣ Testing set active project:")
        set_result = set_active_project(test_project_path)
        print(f"   Result: {json.dumps(set_result, indent=2)}")
        
        # Test 4: Delegate a coding task
        print(f"\n4️⃣ Testing task delegation:")
        task_result = delegate_coding_task(
            "Add error handling to the hello_world function",
            project_path=test_project_path,
            priority="normal",
            tags=["enhancement", "error-handling"]
        )
        print(f"   Result: {json.dumps(task_result, indent=2)}")
        
        # Test 5: System status
        print(f"\n5️⃣ Testing system status:")
        status = get_system_status()
        print(f"   Result: {json.dumps(status, indent=2)}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during server testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(mock_path):
            os.remove(mock_path)
        if os.path.exists("/tmp/test_project"):
            import shutil
            shutil.rmtree("/tmp/test_project")

if __name__ == "__main__":
    success = test_enhanced_server_with_mock()
    sys.exit(0 if success else 1)
